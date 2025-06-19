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

reinvest_rate = st.sidebar.number_input("Taxa de reinv. (cupons) (%)", 0.0, 10.0, 2.0) / 100

usd_buy = st.sidebar.number_input("Câmbio na compra (BRL/USD)", 1.0, 20.0, 5.5, step=0.1)
usd_sell = st.sidebar.number_input("Câmbio na venda (BRL/USD)", 1.0, 20.0, 6.0, step=0.1)

# ---------------- Funções de simulação ----------------

def simulate_etf():
    series = []
    value = usd_initial
    tax_us_total = 0.0
    for _ in range(years):
        dividend = value * div_yield
        tax_us_total += dividend * 0.30  # retenção EUA
        value = (value + dividend * 0.70) * (1 + usd_growth_etf)
        series.append(value)
    gain = value - usd_initial
    tax_br = gain * 0.15  # IR Brasil sobre ganho
    return series, tax_us_total, tax_br

def simulate_bond():
    principal = usd_initial
    reinvested = 0.0
    tax_br_total = 0.0
    series = []
    for _ in range(years):
        coupon = principal * bond_coupon
        tax_br_total += coupon * 0.15  # IR Brasil
        reinvested = (reinvested + coupon * 0.85) * (1 + reinvest_rate)
        total = principal + reinvested
        series.append(total)
    return series, 0.0, tax_br_total

def simulate_mutual():
    series = []
    for yr in range(1, years + 1):
        value = usd_initial * ((1 + usd_growth_mutual) ** yr)
        series.append(value)
    gain = series[-1] - usd_initial
    tax_br = gain * 0.15
    return series, 0.0, tax_br

# ---------------- Execução ----------------
etf_series, etf_tax_us, etf_tax_br = simulate_etf()
bond_series, bond_tax_us, bond_tax_br = simulate_bond()
mut_series, mut_tax_us, mut_tax_br = simulate_mutual()

# ---------------- Tabela final ----------------
scenarios = ["ETF c/ Dividendos", "Bond c/ Cupom", "Mutual Fund Acumulativo"]
final_values = [etf_series[-1], bond_series[-1], mut_series[-1]]
taxes_us = [etf_tax_us, bond_tax_us, mut_tax_us]
taxes_br = [etf_tax_br, bond_tax_br, mut_tax_br]

df = pd.DataFrame({
    "Cenário": scenarios,
    "Valor Final (USD)": final_values,
    "Imposto EUA (USD)": taxes_us,
    "Imposto Brasil (USD)": taxes_br,
})
df["Valor Líquido (USD)"] = df["Valor Final (USD)"] - df["Imposto Brasil (USD)"]
df["Valor Líquido (BRL)"] = df["Valor Líquido (USD)"] * usd_sell

st.subheader("Tabela Resumo")
numeric_cols = df.select_dtypes(include="number").columns
st.dataframe(df.style.format({c: "{:,.2f}" for c in numeric_cols}))

# ---------------- Evolução ----------------
years_range = np.arange(1, years + 1)
plt.figure(figsize=(10, 5))
plt.plot(years_range, np.array(etf_series) * usd_sell, label="ETF c/ Dividendos")
plt.plot(years_range, np.array(bond_series) * usd_sell, label="Bond c/ Cupom")
plt.plot(years_range, np.array(mut_series) * usd_sell, label="Mutual Fund Ac.")
plt.xlabel("Ano")
plt.ylabel("Valor bruto em BRL")
plt.title("Evolução do Capital (BRL)")
plt.legend()
st.pyplot(plt.gcf())
