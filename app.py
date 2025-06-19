import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador de Capital no Exterior", layout="wide")

st.title("Simulador de Projeção de Capital — Investidor Brasileiro no Exterior")

# ---------------- Sidebar parâmetros ----------------
st.sidebar.header("Parâmetros gerais")
years = st.sidebar.number_input("Prazo de investimento (anos)", 1, 50, 10)
usd_initial = st.sidebar.number_input("Aporte inicial (USD)", 100.0, 1_000_000.0, 10_000.0, step=100.0)

usd_growth_etf = st.sidebar.number_input("Valorização anual do ETF (%)", 0.0, 20.0, 5.0) / 100
div_yield = st.sidebar.number_input("Dividend yield anual ETF (%)", 0.0, 10.0, 2.0) / 100
bond_coupon = st.sidebar.number_input("Cupom anual do bond (%)", 0.0, 15.0, 4.0) / 100
usd_growth_mutual = st.sidebar.number_input("Valorização anual do mutual fund (%)", 0.0, 20.0, 5.0) / 100

usd_buy = st.sidebar.number_input("Câmbio na compra (BRL/USD)", 1.0, 20.0, 5.5, step=0.1)
usd_sell = st.sidebar.number_input("Câmbio na venda (BRL/USD)", 1.0, 20.0, 6.0, step=0.1)

# ---------------- Funções de simulação ----------------

def simulate_etf():
    """ETF que distribui dividendos; retenção 30% EUA, crédito 15% BR"""
    value = usd_initial
    tax_us = 0.0
    for _ in range(years):
        dividend = value * div_yield
        tax_us += dividend * 0.30  # retenção nos EUA
        value = (value + dividend * 0.70) * (1 + usd_growth_etf)
    gain = value - usd_initial
    tax_br = gain * 0.15  # IR Brasil sobre ganho de capital
    return value, tax_us, tax_br


def simulate_bond():
    """Bond que paga cupom anual; cupom tributa 15% no Brasil cada ano"""
    principal = usd_initial
    reinvested = 0.0
    tax_br = 0.0
    for _ in range(years):
        coupon = principal * bond_coupon
        tax_br += coupon * 0.15  # IR Brasil sobre cupom
        reinvested = (reinvested + coupon * 0.85) * (1 + 0.02)  # assume 2% no reinvestimento
    total = principal + reinvested
    return total, 0.0, tax_br


def simulate_mutual():
    """Mutual fund acumulativo – só imposto no resgate"""
    value = usd_initial * ((1 + usd_growth_mutual) ** years)
    gain = value - usd_initial
    tax_br = gain * 0.15
    return value, 0.0, tax_br

# ---------------- Execução ----------------
etf_val, etf_tax_us, etf_tax_br = simulate_etf()
bond_val, bond_tax_us, bond_tax_br = simulate_bond()
mut_val, mut_tax_us, mut_tax_br = simulate_mutual()

# ---------------- Monta DataFrame ----------------

data = {
    "Cenário": [
        "ETF c/ Dividendos",
        "Bond c/ Cupom",
        "Mutual Fund Acumulativo",
    ],
    "Valor Final (USD)": [etf_val, bond_val, mut_val],
    "Imposto EUA (USD)": [etf_tax_us, 0.0, 0.0],
    "Imposto Brasil (USD eq.)": [etf_tax_br, bond_tax_br, mut_tax_br],
}

df = pd.DataFrame(data)
df["Valor Líquido (USD)"] = df["Valor Final (USD)"] - df["Imposto Brasil (USD eq.)"]

df["Valor Final (BRL)"] = df["Valor Final (USD)"] * usd_sell
df["Imposto EUA (BRL)"] = df["Imposto EUA (USD)"] * usd_sell
df["Imposto Brasil (BRL)"] = df["Imposto Brasil (USD eq.)"] * usd_sell
df["Valor Líquido (BRL)"] = df["Valor Líquido (USD)"] * usd_sell

# ---------------- Exibição ----------------

st.subheader("Resultados")
numeric_cols = df.select_dtypes(include="number").columns
st.dataframe(df.style.format({c: "{:,.2f}" for c in numeric_cols}))

st.subheader("Comparação do Valor Líquido em BRL")
fig, ax = plt.subplots()
ax.bar(df["Cenário"], df["Valor Líquido (BRL)"])
ax.set_ylabel("Valor Líquido (R$)")
st.pyplot(fig)
