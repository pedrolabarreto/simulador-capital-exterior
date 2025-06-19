import streamlit as st
import numpy as np
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Simulador de Capital no Exterior", layout="wide")

st.title("Simulador de Projeção de Capital — Investidor Brasileiro no Exterior")

# -------------- Parâmetros -----------------
st.sidebar.header("Parâmetros gerais")
years = st.sidebar.number_input("Prazo de investimento (anos)", 1, 50, 10)
usd_initial = st.sidebar.number_input("Aporte inicial único (USD)", 0.0, 1_000_000.0, 10_000.0, step=100.0)
monthly_contrib = st.sidebar.number_input("Contribuição mensal (USD)", 0.0, 100_000.0, 0.0, step=100.0)

usd_growth_etf = st.sidebar.number_input("Valorização anual do ETF (%)", 0.0, 20.0, 5.0) / 100
div_yield = st.sidebar.number_input("Dividend yield anual ETF (%)", 0.0, 10.0, 2.0) / 100

bond_coupon = st.sidebar.number_input("Cupom anual do bond (%)", 0.0, 15.0, 4.0) / 100
reinvest_rate = st.sidebar.number_input("Taxa de reinv. dos cupons (%)", 0.0, 10.0, 2.0) / 100

usd_growth_mutual = st.sidebar.number_input("Valorização anual do mutual fund (%)", 0.0, 20.0, 5.0) / 100

usd_buy = st.sidebar.number_input("Câmbio na compra (BRL/USD)", 1.0, 20.0, 5.5, step=0.1)
usd_sell = st.sidebar.number_input("Câmbio na venda (BRL/USD)", 1.0, 20.0, 6.0, step=0.1)

# ------------ Conversões mensais ----------
months = years * 12
etf_month_growth = (1 + usd_growth_etf) ** (1/12) - 1
div_month_yield = div_yield / 12

bond_month_coupon = bond_coupon / 12
reinvest_month_rate = (1 + reinvest_rate) ** (1/12) - 1

mutual_month_growth = (1 + usd_growth_mutual) ** (1/12) - 1

# ------------- Funções --------------------
def simulate_etf():
    value = usd_initial
    tax_us_total = 0.0
    yearly = []
    for m in range(1, months + 1):
        value += monthly_contrib
        dividend = value * div_month_yield
        tax_us_total += dividend * 0.30
        value = (value + dividend * 0.70) * (1 + etf_month_growth)
        if m % 12 == 0:
            yearly.append(value)
    gain = value - (usd_initial + monthly_contrib * months)
    tax_br = max(gain * 0.15, 0.0)
    return yearly, tax_us_total, tax_br

def simulate_bond():
    principal = usd_initial
    reinvested = 0.0
    tax_br_total = 0.0
    yearly = []
    for m in range(1, months + 1):
        principal += monthly_contrib
        coupon = principal * bond_month_coupon
        tax_br_total += coupon * 0.15
        reinvested = (reinvested + coupon * 0.85) * (1 + reinvest_month_rate)
        total = principal + reinvested
        if m % 12 == 0:
            yearly.append(total)
    return yearly, 0.0, tax_br_total

def simulate_mutual():
    value = usd_initial
    yearly = []
    for m in range(1, months + 1):
        value += monthly_contrib
        value *= (1 + mutual_month_growth)
        if m % 12 == 0:
            yearly.append(value)
    gain = value - (usd_initial + monthly_contrib * months)
    tax_br = max(gain * 0.15, 0.0)
    return yearly, 0.0, tax_br

# ------------- Simulações -----------------
etf_series, etf_tax_us, etf_tax_br = simulate_etf()
bond_series, bond_tax_us, bond_tax_br = simulate_bond()
mut_series, mut_tax_us, mut_tax_br = simulate_mutual()

years_range = np.arange(1, years + 1)

# ------------- Navegação ------------------
page = st.radio("Visão:", ["Tabela Resumo", "Gráfico de Evolução", "Baixar Excel"])

if page == "Tabela Resumo":
    scenarios = ["ETF c/ Dividendos", "Bond c/ Cupom", "Mutual Fund Acumulativo"]
    final_values = [etf_series[-1], bond_series[-1], mut_series[-1]]
    taxes_us = [etf_tax_us, 0.0, 0.0]
    taxes_br = [etf_tax_br, bond_tax_br, mut_tax_br]

    df = pd.DataFrame({
        "Cenário": scenarios,
        "Valor Final (USD)": final_values,
        "Imposto EUA (USD)": taxes_us,
        "Imposto Brasil (USD)": taxes_br,
    })
    df["Valor Líquido (USD)"] = df["Valor Final (USD)"] - df["Imposto Brasil (USD)"]
    df["Valor Líquido (BRL)"] = df["Valor Líquido (USD)"] * usd_sell
    st.dataframe(df.style.format({c: "{:,.2f}" for c in df.select_dtypes('number').columns}))

elif page == "Gráfico de Evolução":
    df_plot = pd.DataFrame({
        "Ano": years_range,
        "ETF (BRL)": np.array(etf_series) * usd_sell,
        "Bond (BRL)": np.array(bond_series) * usd_sell,
        "Mutual (BRL)": np.array(mut_series) * usd_sell,
    }).set_index("Ano")
    st.line_chart(df_plot)

else:
    df_yearly = pd.DataFrame({
        "Ano": years_range,
        "ETF (USD)": etf_series,
        "Bond (USD)": bond_series,
        "Mutual (USD)": mut_series,
        "ETF (BRL)": np.array(etf_series) * usd_sell,
        "Bond (BRL)": np.array(bond_series) * usd_sell,
        "Mutual (BRL)": np.array(mut_series) * usd_sell,
    })
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_yearly.to_excel(writer, index=False, sheet_name="Ano_a_Ano")
    buffer.seek(0)
    st.download_button("📥 Baixar Excel Ano-a-Ano",
                       buffer.getvalue(),
                       file_name="simulador_capital_exterior.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.write("Prévia:", df_yearly.head())
