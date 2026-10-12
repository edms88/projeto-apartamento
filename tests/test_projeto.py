import os
import tempfile
import unittest
from datetime import date
from pathlib import Path
from financeiro import saldo, prazo, aporte_necessario, mes_futuro
import banco

class Financas(unittest.TestCase):
    def test_sem_juros(self):
        self.assertEqual(prazo(80000,0,4000,0),20)
        self.assertEqual(aporte_necessario(80000,0,0,20),4000)
        self.assertIsNone(prazo(80000,0,0,0))
        self.assertEqual(prazo(80000,80000,0,0),0)
    def test_formula_contra_recurrencia(self):
        valor=1500
        for _ in range(24):
            valor=valor*1.005+2000
        self.assertAlmostEqual(saldo(1500,2000,.005,24),valor)
        aporte=aporte_necessario(110000,1500,.005,24)
        self.assertAlmostEqual(saldo(1500,aporte,.005,24),110000)
    def test_virada_ano(self):
        self.assertEqual(mes_futuro(date(2026,12,1),1),date(2027,1,1))
        self.assertEqual(mes_futuro(date(2026,1,1),-1),date(2025,12,1))

class Banco(unittest.TestCase):
    def test_persistencia(self):
        with tempfile.TemporaryDirectory() as d:
            original=banco.DB
            banco.DB=Path(d)/'teste.db'
            try:
                banco.salvar({'aporte':1500})
                self.assertEqual(banco.carregar({})['aporte'],1500)
                banco.registrar('2026-09-01',1000,'primeiro')
                banco.registrar('2026-09-01',2000,'corrigido')
                self.assertEqual(banco.historico(),[('2026-09-01',2000.,'corrigido')])
                banco.excluir('2026-09-01')
                self.assertEqual(banco.historico(),[])
            finally:
                banco.DB=original

if __name__=='__main__': unittest.main()
