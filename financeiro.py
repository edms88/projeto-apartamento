"""Projeções com aportes no final do mês e taxa líquida mensal constante."""
from datetime import date


def saldo(inicial, aporte, taxa, meses):
    if meses == 0:
        return inicial
    if taxa == 0:
        return inicial + aporte * meses
    crescimento = (1 + taxa) ** meses
    return inicial * crescimento + aporte * (crescimento - 1) / taxa


def aporte_necessario(meta, inicial, taxa, meses):
    if meses <= 0:
        raise ValueError('O prazo deve ser positivo.')
    if taxa == 0:
        return max(0., (meta - inicial) / meses)
    fator = (1 + taxa) ** meses
    return max(0., (meta - inicial * fator) * taxa / (fator - 1))


def prazo(meta, inicial, aporte, taxa, limite=600):
    if inicial >= meta:
        return 0
    for meses in range(1, limite + 1):
        if saldo(inicial, aporte, taxa, meses) >= meta:
            return meses
    return None


def mes_futuro(inicio, meses):
    indice = inicio.year * 12 + inicio.month - 1 + meses
    return date(indice // 12, indice % 12 + 1, 1)
