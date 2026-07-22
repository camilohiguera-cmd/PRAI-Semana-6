import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="Global Insights Analytics", layout="wide")
st.title("📊 Global Insights Analytics — Executive Dashboard")

# Cargar datos
df_ventas = pd.read_csv("data/fuente1_ventas_sql.csv")
with open("data/fuente2_csat_api.json", "r") as f:
    data_json = json.load(f)
df_csat = pd.DataFrame(data_json["metricas"])
df_costos = pd.read_excel("data/fuente3_costos_excel.xlsx")

df_master = df_ventas.merge(df_csat, on="industria").merge(df_costos, on="industria")

# Filtros laterales
industria_sel = st.sidebar.multiselect("Industria:", df_master['industria'].unique(), default=df_master['industria'].unique())
df_filtered = df_master[df_master['industria'].isin(industria_sel)]

# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("Ingresos Totales", f"${df_filtered['monto_usd'].sum():,.2f} USD")
c2.metric("Transacciones", f"{len(df_filtered):,}")
c3.metric("CSAT Promedio", f"{df_filtered['csat_score'].mean():.2f} / 5.0")

# Gráficos
st.plotly_chart(px.bar(df_filtered.groupby("industria")["monto_usd"].sum().reset_index(), x="industria", y="monto_usd", color="industria"), use_container_width=True)
st.plotly_chart(px.pie(df_filtered, names="region", values="monto_usd", hole=0.4), use_container_width=True)
