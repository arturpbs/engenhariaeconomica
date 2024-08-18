import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf

# Instruções iniciais
st.title("Análise de Fluxo de Caixa para Alternativas de Investimento - Engenharia Econômica")
st.markdown("Desenvolvido por: Artur Pereira Batista Silva")

st.header("Fluxo de Caixa:")
st.markdown("Insira na tabela abaixo o Fluxo de Caixa das duas alternativas a serem avaliadas. Caso as alternativas possuam mais períodos, clique no '+' no final da tabela para adicionar mais linhas.")

# Dados iniciais
data = {'A': [-200, 100, 100, 100, 100], 'B': [-200, 50, 50, 50, 1000]}
df = pd.DataFrame(data)

# Editor de Dados
df = st.data_editor(
    df,
    num_rows="dynamic",
    column_config={
        "A": st.column_config.NumberColumn(
            "Fluxo de Caixa da Alternativa A",
            help="Insira o Fluxo de Caixa da Alternativa A",
            format="R$ %.2f",
            required=True,
            step=0.01
        ),
        "B": st.column_config.NumberColumn(
            "Fluxo de Caixa da Alternativa B",
            help="Insira o Fluxo de Caixa da Alternativa B",
            format="R$ %.2f",
            required=True,
            step=0.01
        )
    },
    hide_index=False,
)

# TMA
st.markdown("Insira a Taxa Mínima de Atratividade (em %):")
df_tma = pd.DataFrame({'Taxa Mínima de Atratividade (em %):': [0.1]})

df_tma = st.data_editor(
    df_tma,
    column_config={
        "Taxa Mínima de Atratividade (em %):": st.column_config.NumberColumn(
            format="%.3f",
            required=True,
            step=0.001
        )
    },
)

# Função de cálculo do payback descontado
def discounted_payback_period(rate, cash_flows_df):
    """
    Calcula o payback descontado de um fluxo de caixa.

    Parâmetros:
    - rate: Taxa de desconto (em decimal, por exemplo, 0.1 para 10%)
    - cash_flows_df: DataFrame contendo os fluxos de caixa por período, 
                     onde o índice é o ano e a coluna é o fluxo de caixa.

    Retorna:
    - Payback descontado, ou None se o payback não puder ser calculado.
    """
    # Cria um DataFrame para armazenar os fluxos de caixa não descontados
    cf_df = pd.DataFrame(cash_flows_df.copy())
    cf_df.columns = ['UndiscountedCashFlows']
    cf_df.index.name = 'Year'
    
    # Calcula os fluxos de caixa descontados
    cf_df['DiscountedCashFlows'] = npf.pv(rate=rate, pmt=0, nper=cf_df.index, fv=-cf_df['UndiscountedCashFlows'])
    
    # Calcula o fluxo de caixa descontado acumulado
    cf_df['CumulativeDiscountedCashFlows'] = np.cumsum(cf_df['DiscountedCashFlows'])
    
    # Identifica o último ano com fluxo de caixa acumulado negativo
    negative_cash_flows = cf_df[cf_df.CumulativeDiscountedCashFlows < 0]
    
    if negative_cash_flows.empty:
        return float('inf')  # Indica que não há período de payback, ou você pode usar `None`
    
    final_full_year = negative_cash_flows.index.values.max()
    
    # Verifica se o payback ocorre dentro do próximo período
    if final_full_year == cf_df.index.max():
        return float('inf')  # Indica que o fluxo de caixa não é suficiente para o payback
    
    # Calcula a fração do ano em que o fluxo de caixa acumulado se torna positivo
    fractional_yr = -cf_df.CumulativeDiscountedCashFlows[final_full_year] / cf_df.DiscountedCashFlows[final_full_year + 1]
    
    # Calcula o período total de payback descontado
    payback_period = final_full_year + fractional_yr
    
    return payback_period

# Função de comparação das alternativas
def compare_alternatives(tir_a, vpl_a, payback_a, tir_b, vpl_b, payback_b):
    data = {
        'Alternativa A': [tir_a, vpl_a, payback_a],
        'Alternativa B': [tir_b, vpl_b, payback_b],
        'Alternativa Escolhida': [
            'A' if tir_a > tir_b else 'B',
            'A' if vpl_a > vpl_b else 'B',
            'A' if payback_a < payback_b else 'B'
        ]
    }
    return pd.DataFrame(data, index=['TIR', 'VPL', 'Payback'])

# Cálculo dos valores
vpl_a = round(npf.npv(df_tma.iat[0, 0], df['A']), 2)
tir_a = npf.irr(df['A'])
payback_a = round(discounted_payback_period(df_tma.iat[0, 0], df['A']), 2)

vpl_b = round(npf.npv(df_tma.iat[0, 0], df['B']), 2)
tir_b = npf.irr(df['B'])
payback_b = round(discounted_payback_period(df_tma.iat[0, 0], df['B']), 2)

# Exibição dos gráficos e resultados
st.header("Gráficos dos Fluxos de Caixa:")
st.subheader("Gráfico do Fluxo de Caixa da Alternativa A:")
st.bar_chart(df['A'].copy())  # Usar copy() para forçar atualização

st.markdown(f"VPL da Alternativa A: R$ {vpl_a}")
st.markdown(f"TIR da Alternativa A: {round(tir_a * 100,2)}%")
st.markdown(f"Payback Descontado da Alternativa A: {payback_a} anos")

st.subheader("Gráfico do Fluxo de Caixa da Alternativa B:")
st.bar_chart(df['B'].copy())  # Usar copy() para forçar atualização

st.markdown(f"VPL da Alternativa B: R$ {vpl_b}")
st.markdown(f"TIR da Alternativa B: {round(tir_b * 100,2)}%")
st.markdown(f"Payback Descontado da Alternativa B: {payback_b} anos")

# Comparação das alternativas
st.header("Análise das Alternativas")
resultado_comparacao = compare_alternatives(tir_a, vpl_a, payback_a, tir_b, vpl_b, payback_b)
st.dataframe(resultado_comparacao)

