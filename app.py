import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

st.set_page_config(page_title="Dashboard de Salários na Área de Dados", page_icon="📊", layout="wide")

@st.cache_data
def carregar_dados():
    return pd.read_csv("https://raw.githubusercontent.com/EliC-F/imersao_dados_python_alura/main/Eli_dados_imersao.csv")

def iso2_to_iso3(code):
    country = pycountry.countries.get(alpha_2=code)
    return country.alpha_3 if country else None

df = carregar_dados()

st.sidebar.header("🔍 Filtros")

anos = sorted(df['ano'].unique())
senioridades = sorted(df['senioridade'].unique())
contratos = sorted(df['contrato'].unique())
tamanhos = sorted(df['tamanho_empresa'].unique())

anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)
senior_sel = st.sidebar.multiselect("Senioridade", senioridades, default=senioridades)
contratos_sel = st.sidebar.multiselect("Tipo de contrato", contratos, default=contratos)
tamanhos_sel = st.sidebar.multiselect("Tamanho da empresa", tamanhos, default=tamanhos)

df_filtrado = df[
    df['ano'].isin(anos_sel) &
    df['senioridade'].isin(senior_sel) &
    df['contrato'].isin(contratos_sel) &
    df['tamanho_empresa'].isin(tamanhos_sel)
].copy()

df_filtrado['residencia_iso3'] = df_filtrado['residencia'].apply(iso2_to_iso3)

st.title("📊 Análise de Salários na Área de Dados")
st.markdown(
    "Este dashboard permite explorar padrões salariais na área de dados, comparando cargos, "
    "distribuição de salários e diferenças geográficas, com base nos filtros selecionados."
)

st.subheader("Métricas gerais (USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_max = df_filtrado['usd'].max()
    total = len(df_filtrado)
    cargo_freq = df_filtrado['cargo'].mode()[0]
else:
    salario_medio = salario_max = total = 0
    cargo_freq = "-"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salário médio", f"${salario_medio:,.0f}")
c2.metric("Salário máximo", f"${salario_max:,.0f}")
c3.metric("Total de registros", f"{total:,}")
c4.metric("Cargo mais frequente", cargo_freq)

st.markdown("---")
st.subheader("Visualizações")

col1, col2 = st.columns(2)

with col1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values().reset_index()
        fig_cargos = px.bar(top_cargos, x='usd', y='cargo', orientation='h',
                            title="Top 10 cargos por salário médio",
                            labels={'usd': 'Salário médio anual (USD)', 'cargo': ''})
        st.plotly_chart(fig_cargos, use_container_width=True)
    else:
        st.warning("Sem dados para o gráfico de cargos.")

with col2:
    if not df_filtrado.empty:
        fig_hist = px.histogram(df_filtrado, x='usd', nbins=30,
                                title="Distribuição salarial",
                                labels={'usd': 'Faixa salarial (USD)'})
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.warning("Sem dados para o gráfico de distribuição.")

col3, col4 = st.columns(2)

with col3:
    if not df_filtrado.empty:
        remoto = df_filtrado['remoto'].value_counts().reset_index()
        remoto.columns = ['tipo', 'quantidade']
        fig_remoto = px.pie(remoto, names='tipo', values='quantidade',
                            title="Proporção dos tipos de trabalho", hole=0.5)
        fig_remoto.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_remoto, use_container_width=True)
    else:
        st.warning("Sem dados para o gráfico de trabalho remoto.")

with col4:
    df_ds = df_filtrado[df_filtrado['cargo'].str.contains('data scientist', case=False, na=False)]
    if not df_ds.empty:
        media_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index().dropna()
        fig_mapa = px.choropleth(media_pais, locations='residencia_iso3', color='usd',
                                 color_continuous_scale='RdYlGn',
                                 title="Salário médio de Cientistas de Dados por país",
                                 labels={'usd': 'Salário médio (USD)'})
        st.plotly_chart(fig_mapa, use_container_width=True)
    else:
        st.warning("Sem dados para o mapa.")

st.subheader("Top 10 países por salário médio (Data Science)")

if not df_ds.empty:
    top_paises = media_pais.sort_values(by='usd', ascending=False).head(10).sort_values(by='usd')
    fig_bar = px.bar(top_paises, x='usd', y='residencia_iso3', orientation='h',
                     color='usd', color_continuous_scale='RdYlGn',
                     title="Top 10 países com maior salário médio em Data Science",
                     labels={'usd': 'Salário médio anual (USD)', 'residencia_iso3': 'País'})
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Sem dados para o gráfico de países.")

st.subheader("Dados detalhados")
st.dataframe(df_filtrado, use_container_width=True)
