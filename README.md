# Projeto Apartamento — Streamlit

Planejamento da entrada de R$ 80.000 para imóvel de R$ 400.000, com custos e reserva editáveis. App local com simulador, orçamento, cenários, acompanhamento de aportes e SQLite.

## Windows

1. Instale Python 3.11 ou superior, incluindo o launcher `py`.
2. Extraia o ZIP inteiro em uma pasta.
3. Execute `INICIAR_WINDOWS.bat`. A primeira execução instala as dependências e exige internet.
4. Abra http://localhost:8501 se o navegador não abrir automaticamente.

Alternativa no PowerShell, dentro da pasta extraída (sem necessidade de ativar scripts):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost
```

macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address localhost
```

## Primeiro uso

Preencha as rendas, despesas, saldo no começo do plano, mês inicial e aporte planejado na barra lateral. Clique em **Salvar e recalcular**. Rendas e aportes começam zerados para não inventar a situação financeira do casal. Custos de R$ 20.000 e reserva de R$ 10.000 são apenas exemplos.

O saldo inicial corresponde ao começo do mês inicial. Em **Aportes realizados**, registre o total aportado nos meses fechados. Um novo registro no mesmo mês substitui o anterior. Os aportes do mês corrente entram depois do fechamento. Meses não registrados usam zero. O rendimento é hipotético; o saldo exibido não substitui o extrato bancário. Alterar a taxa recalcula também o saldo estimado histórico.

Na projeção, o ponto inicial é o começo do mês atual (ou do mês inicial se futuro). Os pontos seguintes incluem rendimento e aporte no fim do mês anterior. Exemplo: início em outubro, meta atingida após um aporte → conclusão em outubro.

Não há integração bancária, login, cálculo de prestação ou validação do Minha Casa Minha Vida. O app não incorpora inflação do imóvel, FGTS, subsídio ou venda do apartamento atual automaticamente. Não publique a instalação com dados pessoais sem implementar autenticação e isolamento por usuário.

## Dados e backup

Os dados são salvos em `dados/apartamento.db`. Feche o app e copie esse arquivo para backup; para restaurar, recoloque-o na mesma pasta com o app fechado. CSVs e JSON são exportações para consulta, sem importação nesta versão. Instalações em hospedagens com disco temporário precisam de armazenamento persistente. A variável opcional `APARTAMENTO_DB` permite definir outro caminho da base.

## Verificação

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem cálculos financeiros, datas, persistência e, quando Streamlit está instalado, navegação e gravação pela interface.

## Hospedagem com Docker

O Dockerfile executa o app em Python 3.12 e usa a variável PORT do provedor. Na hospedagem, defina APP_PASSWORD como segredo; não salve a senha no código. O contêiner exige essa senha antes de liberar o aplicativo. Localmente, ela é opcional. Use HTTPS oferecido pelo provedor.

Monte um disco persistente em /app/dados para preservar a base SQLite entre reinícios e deploys. Execute apenas uma instância do app com essa base. A senha é compartilhada pelo casal; não há contas individuais. Não envie dados/apartamento.db nem segredos para o repositório.
