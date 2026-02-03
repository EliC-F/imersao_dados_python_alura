import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# Configurações iniciais da aplicação
st.set_page_config(
    page_title="Análise Salarial na Área de Dados",
    page_icon="📊",
    layout="wide"
)

# Leitura do conjunto de dados
df = pd.read_csv(https://raw.githubusercontent.com/EliC-F/imersao_dados_python_alura/refs/heads/main/Eli_dados_imersao.csv)


# Conversão de código ISO-2 para ISO-3
def iso2_to_iso3(code):
    country = pycountry.countries.get(alpha_2=code)
    return country.alpha_3 if country else None

# Barra lateral com filtros interativos
st.sidebar.header("🔎 Filtros de Análise")

anos = sorted(df['ano'].unique())
anos_sel = st.sidebar.multiselect("Ano", anos, default=anos)

senioridades = sorted(df['senioridade'].unique())
senioridades_sel = st.sidebar.multiselect("Senioridade", senioridades, default=senioridades)

contratos = sorted(df['contrato'].unique())
contratos_sel = st.sidebar.multiselect("Tipo de contrato", contratos, default=contratos)

tamanhos = sorted(df['tamanho_empresa'].unique())
tamanhos_sel = st.sidebar.multiselect("Tamanho da empresa", tamanhos, default=tamanhos)

# Aplicação dos filtros
df_filtrado = df[
    (df['ano'].isin(anos_sel)) &
    (df['senioridade'].isin(senioridades_sel)) &
    (df['contrato'].isin(contratos_sel)) &
    (df['tamanho_empresa'].isin(tamanhos_sel))
].copy()

# Título principal
st.title("🎲 Dashboard de Análise Salarial na Área de Dados")
st.markdown(
    "Este dashboard permite explorar dados salariais da área de dados por meio de filtros "
    "e visualizações interativas."
)

# Métricas gerais
st.subheader("Métricas gerais (salário anual em USD)")

if not df_filtrado.empty:
    media_salario = df_filtrado['usd'].mean()
    max_salario = df_filtrado['usd'].max()
    total = df_filtrado.shape[0]
    cargo_freq = df_filtrado['cargo'].mode()[0]
else:
    media_salario = max_salario = total = 0
    cargo_freq = ""

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salário médio", f"${media_salario:,.0f}")
c2.metric("Salário máximo", f"${max_salario:,.0f}")
c3.metric("Total de registros", f"{total:,}")
c4.metric("Cargo mais frequente", cargo_freq)

st.markdown("---")

# Área de gráficos
st.subheader("Visualizações")

col1, col2 = st.columns(2)

# Top 10 cargos por salário médio
with col1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado
            .groupby('cargo')['usd']
            .mean()
            .nlargest(10)
            .sort_values()
            .reset_index()
        )

        graf_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Salário médio anual (USD)', 'cargo': ''}
        )
        graf_cargos.update_layout(title_x=0.1)
        st.plotly_chart(graf_cargos, use_container_width=True)
    else:
        st.warning("Não há dados para exibir este gráfico.")

# Distribuição salarial
with col2:
    if not df_filtrado.empty:
        graf_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        graf_hist.update_layout(title_x=0.1)
        st.plotly_chart(graf_hist, use_container_width=True)
    else:
        st.warning("Não há dados para exibir este gráfico.")

col3, col4 = st.columns(2)

# Proporção de tipos de trabalho
with col3:
    if not df_filtrado.empty:
        remoto = df_filtrado['remoto'].value_counts().reset_index()
        remoto.columns = ['tipo_trabalho', 'quantidade']

        graf_remoto = px.pie(
            remoto,
            names='tipo_trabalho',
            values='quantidade',
            title="Proporção dos tipos de trabalho",
            hole=0.5
        )
        graf_remoto.update_traces(textinfo='percent+label')
        graf_remoto.update_layout(title_x=0.1)
        st.plotly_chart(graf_remoto, use_container_width=True)
    else:
        st.warning("Não há dados para exibir este gráfico.")

# --- SEU GRÁFICO ---
with col4:
    if not df_filtrado.empty:
        df_filtrado['residencia_iso3'] = df_filtrado['residencia'].apply(iso2_to_iso3)

        df_ds = df_filtrado[
            df_filtrado['cargo'].str.contains('data scien', case=False, na=False)
        ]

        salario_pais = (
            df_ds
            .groupby('residencia_iso3')['usd']
            .mean()
            .reset_index()
            .dropna()
            .sort_values(by='usd', ascending=False)
            .head(10)
        )

        graf_paises_bar = px.bar(
            salario_pais,
            x='residencia_iso3',
            y='usd',
            title="Top 10 países com maior salário médio em Data Science",
            labels={'residencia_iso3': 'País', 'usd': 'Salário médio anual (USD)'},
            color='usd',
            color_continuous_scale='RdBu_r'
        )
        graf_paises_bar.update_layout(title_x=0.1)
        st.plotly_chart(graf_paises_bar, use_container_width=True)
    else:
        st.warning("Não há dados para exibir este gráfico.")

# Mapa geográfico
if not df_filtrado.empty:
    media_ds_pais = (
        df_ds
        .groupby('residencia_iso3')['usd']
        .mean()
        .reset_index()
    )

    graf_mapa = px.choropleth(
        media_ds_pais,
        locations='residencia_iso3',
        color='usd',
        color_continuous_scale='RdYlGn',
        title="Salário médio de Cientistas de Dados por país",
        labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'}
    )
    graf_mapa.update_layout(title_x=0.1)
    st.plotly_chart(graf_mapa, use_container_width=True)
else:
    st.warning("Não há dados para exibir o mapa.")

# Tabela final
st.subheader("Dados detalhados")
st.dataframe(df_filtrado)

