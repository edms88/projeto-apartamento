import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

@unittest.skipUnless(importlib.util.find_spec('streamlit'), 'Streamlit não instalado')
class Interface(unittest.TestCase):
    def test_simulacao_e_persistencia(self):
        from streamlit.testing.v1 import AppTest
        import banco
        with tempfile.TemporaryDirectory() as d:
            original=banco.DB
            banco.DB=Path(d)/'app.db'
            try:
                app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py')).run(timeout=30)
                self.assertFalse(app.exception)
                inputs={item.label:item for item in app.number_input}
                inputs['Renda líquida Edu (R$)'].set_value(7000.)
                inputs['Renda líquida esposa (R$)'].set_value(4000.)
                inputs['Despesas fixas (R$)'].set_value(5000.)
                inputs['Aporte planejado (R$)'].set_value(4000.)
                next(b for b in app.button if b.label=='Salvar e recalcular').click().run()
                self.assertFalse(app.exception)
                self.assertEqual(banco.carregar({})['aporte'],4000.)
                self.assertTrue(any('20 meses' in str(x.value) for x in app.markdown))
                inputs={item.label:item for item in app.number_input}
                inputs['Total aportado no mês (R$)'].set_value(2500.)
                # Date outside plan is rejected, then persist a closed month within the plan.
                from datetime import date
                from financeiro import mes_futuro
                fechado=mes_futuro(date.today().replace(day=1),-1)
                cfg=banco.carregar({})
                cfg['inicio']=fechado.isoformat()
                banco.salvar(cfg)
                app.run()
                next(x for x in app.number_input if x.label=='Total aportado no mês (R$)').set_value(2500.)
                next(b for b in app.button if b.label=='Salvar total do mês').click().run()
                self.assertFalse(app.exception)
                self.assertEqual(banco.historico()[0][1],2500.)
            finally:
                banco.DB=original
