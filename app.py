from datetime import date
import json
import os
import hmac
import pandas as pd
import plotly.express as px
import streamlit as st
import banco
from financeiro import saldo, aporte_necessario, prazo, mes_futuro

st.set_page_config(page_title='Projeto Apartamento', page_icon='🏡', layout='wide')

# Na hospedagem, configure APP_PASSWORD como segredo do provedor.
password = os.environ.get('APP_PASSWORD', '')
if os.environ.get('REQUIRE_APP_PASSWORD') == 'true' and not password:
    st.error('Configure a senha de acesso na hospedagem antes de abrir o app.')
    st.stop()
if password and not st.session_state.get('autenticado', False):
    st.title('🏡 Projeto Apartamento')
    with st.form('login'):
        tentativa = st.text_input('Senha de acesso', type='password')
        if st.form_submit_button('Entrar'):
            if hmac.compare_digest(tentativa.encode(), password.encode()):
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error('Senha incorreta.')
    st.stop()
st.markdown('''<style>
.stApp {background: #f6f8fc;} h1,h2,h3 {color:#14324f;}
[data-testid="stMetric"] {background:white;padding:18px;border-radius:14px;border:1px solid #e2e8f0;}
</style>''', unsafe_allow_html=True)

def brl(valor):
    return 'R$ ' + f'{valor:,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.')

PADRAO = dict(imovel=400000., entrada=80000., custos=20000., reserva=10000.,
              inicial=0., renda_edu=0., renda_esposa=0., fixos=0., variaveis=0.,
              dividas=0., aporte=0., taxa=0., inicio=date.today().replace(day=1).isoformat(), horizonte=48)
config = banco.carregar(PADRAO)
st.title('🏡 Projeto Apartamento')
st.caption('O plano de vocês, da primeira economia até a mudança.')
if os.environ.get('EPHEMERAL_STORAGE') == 'true':
    st.warning('Hospedagem de teste: os dados podem ser apagados ao reiniciar. Exporte seus aportes e o backup JSON antes de sair. Para uso contínuo, configure armazenamento persistente.')

with st.sidebar:
    st.header('Seu plano')
    st.caption('Valores iniciais de custos e reserva são exemplos ajustáveis. Preencha as rendas e despesas reais.')
    with st.form('premissas'):
        st.subheader('Objetivo e ponto de partida')
        campos = {}
        for chave, label in [('imovel','Valor do imóvel'),('entrada','Entrada desejada'),('custos','Custos extras da compra'),('reserva','Reserva pós-compra'),('inicial','Saldo no início do plano')]:
            campos[chave] = st.number_input(label + ' (R$)', min_value=0., value=float(config[chave]), step=1000.)
        inicio = st.date_input('Mês inicial do plano', value=date.fromisoformat(config['inicio']))
        st.subheader('Orçamento mensal')
        for chave, label in [('renda_edu','Renda líquida Edu'),('renda_esposa','Renda líquida esposa'),('fixos','Despesas fixas'),('variaveis','Despesas variáveis'),('dividas','Parcelas de dívidas'),('aporte','Aporte planejado')]:
            campos[chave] = st.number_input(label + ' (R$)', min_value=0., value=float(config[chave]), step=100.)
        campos['taxa'] = st.number_input('Rendimento líquido estimado (% ao mês)', min_value=0., max_value=5., value=float(config['taxa']), step=.1, help='Após impostos e taxas. Hipótese constante, sem garantia de retorno; use zero para projeção sem rendimento.')
        campos['horizonte'] = st.slider('Meses no gráfico', 12, 120, int(config['horizonte']), step=6)
        if st.form_submit_button('Salvar e recalcular', type='primary'):
            if campos['imovel'] <= 0 or campos['entrada'] > campos['imovel']:
                st.error('O imóvel deve ter valor positivo e a entrada não pode superar seu preço.')
            else:
                campos['inicio'] = inicio.replace(day=1).isoformat()
                banco.salvar(campos)
                st.rerun()

inicio = date.fromisoformat(config['inicio'])
taxa = config['taxa'] / 100
meta = config['entrada'] + config['custos'] + config['reserva']
renda = config['renda_edu'] + config['renda_esposa']
despesas = config['fixos'] + config['variaveis'] + config['dividas']
sobra = renda - despesas
rows = banco.historico()
# Cada registro é o total real de aporte de um mês fechado. Meses não registrados têm aporte zero.
ultimo_fechado = mes_futuro(date.today().replace(day=1), -1)
fechados = max(0, (ultimo_fechado.year-inicio.year)*12+ultimo_fechado.month-inicio.month)
real = {r[0]: r[1] for r in rows}
atual = config['inicial']
trajetoria = [{'Mês':inicio,'Planejado':atual,'Real estimado':atual}]
for n in range(fechados + 1):
    mes = mes_futuro(inicio, n)
    if mes > ultimo_fechado:
        break
    atual = atual * (1 + taxa) + real.get(mes.isoformat(), 0.)
    trajetoria.append({'Mês':mes_futuro(mes,1),'Planejado':saldo(config['inicial'],config['aporte'],taxa,n+1),'Real estimado':atual})
base = max(inicio, date.today().replace(day=1))

painel, cenarios, historico, detalhes = st.tabs(['Visão geral','Simulador e cenários','Aportes realizados','Premissas e backup'])
with painel:
    a,b,c,d = st.columns(4)
    a.metric('Entrada desejada',brl(config['entrada']))
    b.metric('Meta com custos e reserva',brl(meta))
    c.metric('Saldo estimado atual',brl(atual))
    d.metric('Falta para a meta completa',brl(max(0., meta-atual)))
    st.progress(min(1., atual/meta) if meta else 1., text=f'{min(100., atual/meta*100) if meta else 100:.1f}% da meta completa')
    a,b,c = st.columns(3)
    a.metric('Sobra mensal',brl(sobra))
    b.metric('Aporte planejado',brl(config['aporte']))
    c.metric('Taxa de poupança planejada',f'{config["aporte"]/renda*100:.1f}%' if renda else 'Preencha as rendas')
    if config['aporte'] > sobra:
        st.warning('O aporte planejado supera a sobra mensal. Ajustem despesas, renda ou prazo antes de adotar o cenário.')
    for alvo, label in [(config['entrada'],'entrada'),(meta,'meta com custos e reserva')]:
        meses = prazo(alvo, atual, config['aporte'], taxa)
        if meses == 0:
            st.success(f'A {label} já foi alcançada no saldo estimado.')
        elif meses is None:
            st.info(f'A {label} não é alcançada em até 600 meses com essas premissas.')
        else:
            # Aporte no final do mês base: primeiro aporte corresponde ao próprio mês base.
            chegada = mes_futuro(base, meses-1)
            st.write(f'**{label.capitalize()}:** {meses} meses de aportes • mês estimado {chegada:%m/%Y}')
    proj = pd.DataFrame([{'Mês':mes_futuro(base,n),'Saldo projetado':saldo(atual,config['aporte'],taxa,n)} for n in range(config['horizonte']+1)])
    fig = px.area(proj, x='Mês',y='Saldo projetado',color_discrete_sequence=['#1d7994'],labels={'Saldo projetado':'Saldo (R$)'})
    fig.add_hline(y=config['entrada'],line_dash='dot',annotation_text='Entrada')
    fig.add_hline(y=meta,line_dash='dash',annotation_text='Meta completa')
    fig.update_layout(template='plotly_white',margin=dict(t=35,b=20))
    st.plotly_chart(fig, width='stretch')
    st.caption('O ponto inicial é o começo do mês; cada ponto seguinte inclui o rendimento e o aporte ao fim do mês anterior.')
    st.download_button('Baixar projeção CSV',proj.to_csv(index=False,sep=';',decimal=',').encode('utf-8-sig'),'projecao_apartamento.csv','text/csv')
    st.metric('Financiamento nominal estimado',brl(max(0.,config['imovel']-config['entrada'])))
    st.caption('Preço menos entrada. Não inclui juros, seguros ou tarifas e não representa aprovação de crédito ou enquadramento no Minha Casa Minha Vida.')

with cenarios:
    st.subheader('Quanto precisamos guardar por mês?')
    tabela = pd.DataFrame([{'Prazo (meses)':m,'Para entrada (R$)':aporte_necessario(config['entrada'],atual,taxa,m),'Para meta completa (R$)':aporte_necessario(meta,atual,taxa,m)} for m in [12,18,24,30,36,48]])
    st.dataframe(tabela.style.format({'Para entrada (R$)':brl,'Para meta completa (R$)':brl}),hide_index=True,width='stretch')
    novo = st.number_input('E se aportarmos por mês (R$)?', min_value=0.,value=float(config['aporte']),step=100.)
    meses = prazo(meta,atual,novo,taxa)
    original = prazo(meta,atual,config['aporte'],taxa)
    if meses is None:
        st.info('A meta não é atingida em até 600 meses nesse cenário.')
    elif meses == 0:
        st.success('A meta já está alcançada.')
    else:
        st.metric('Prazo da meta completa',f'{meses} meses',f'{original-meses} meses de antecipação' if original is not None and original != meses else None)
        st.write('Mês da conclusão:',mes_futuro(base,meses-1).strftime('%m/%Y'))
    if novo > sobra:
        st.warning('Esse cenário exige aporte acima da sobra do orçamento.')
    destino = st.date_input('Mês em que desejam alcançar a meta',value=mes_futuro(base,23),min_value=base)
    meses_destino = (destino.year-base.year)*12+destino.month-base.month+1
    necessario = aporte_necessario(meta,atual,taxa,meses_destino)
    st.metric('Aporte necessário para essa data',brl(necessario))

with historico:
    st.subheader('Fechamento de aportes mensais')
    st.caption('Registre o total guardado em cada mês fechado, incluindo renda extra e 13º. Salvar novamente o mesmo mês substitui o total. O saldo inicial não deve incluir esses aportes.')
    with st.form('aporte_real'):
        mes = st.date_input('Mês do aporte',value=ultimo_fechado)
        valor = st.number_input('Total aportado no mês (R$)',min_value=0.,value=0.,step=100.)
        nota = st.text_input('Observação (opcional)')
        if st.form_submit_button('Salvar total do mês'):
            mes = mes.replace(day=1)
            if mes < inicio or mes > ultimo_fechado:
                st.error('Escolha um mês fechado entre o início do plano e o mês passado.')
            else:
                banco.registrar(mes.isoformat(),valor,nota)
                st.rerun()
    df = pd.DataFrame(rows,columns=['Mês','Aporte (R$)','Observação'])
    st.dataframe(df,hide_index=True,width='stretch')
    st.download_button('Exportar aportes CSV',df.to_csv(index=False,sep=';',decimal=',').encode('utf-8-sig'),'aportes.csv','text/csv')
    if rows:
        escolha = st.selectbox('Registro a remover',[r[0] for r in rows])
        confirmar = st.checkbox('Confirmo a exclusão deste registro')
        if st.button('Excluir registro',disabled=not confirmar):
            banco.excluir(escolha)
            st.rerun()
    if len(trajetoria)>1:
        st.plotly_chart(px.line(pd.DataFrame(trajetoria),x='Mês',y=['Planejado','Real estimado'],labels={'value':'Saldo (R$)','variable':'Série'},template='plotly_white'),width='stretch')

with detalhes:
    st.subheader('Como interpretar o plano')
    st.write('Entrada + custos extras + reserva formam a meta completa. Os R$ 20 mil de custos e R$ 10 mil de reserva são exemplos, não tarifas oficiais nem uma recomendação personalizada.')
    st.write('A projeção usa rendimento líquido constante e aportes no fim do mês. Não corrige o preço do imóvel pela inflação. O saldo atual é estimado: parte do saldo inicial e aplica os aportes registrados e o rendimento hipotético aos meses fechados. Meses sem registro têm aporte zero; compare esse saldo com o extrato real.')
    st.write('Este app planeja a acumulação. Ele não calcula prestações nem valida regras do Minha Casa Minha Vida. FGTS, venda do apartamento atual e subsídios não são adicionados automaticamente.')
    st.write('Configurações e aportes ficam em dados/apartamento.db na pasta do projeto. Reabrir o app preserva esses dados no mesmo computador. A base é compartilhada por quem acessar essa instalação.')
    fora = [r for r in rows if not inicio.isoformat() <= r[0] <= ultimo_fechado.isoformat()]
    if fora:
        st.warning('Existem registros fora do período atual do plano. Eles foram preservados no histórico, mas não entram no saldo estimado.')
    backup = {'config':config,'aportes':[{'mes':r[0],'valor':r[1],'nota':r[2]} for r in rows]}
    st.download_button('Baixar backup JSON',json.dumps(backup,ensure_ascii=False,indent=2),'backup_apartamento.json','application/json')
    st.caption('Para restauração integral, guarde uma cópia de dados/apartamento.db com o app fechado. O JSON é uma exportação para consulta; esta versão não tem importação de JSON.')
