import streamlit as st
import pandas as pd
import json
import os

# Configuración de página
st.set_page_config(page_title="Global Insights Analytics", layout="wide")

# Obtener ruta base segura
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar datos de forma segura (soporta carpeta Data o data)
folder_name = "data" if os.path.exists(os.path.join(BASE_DIR, "data")) else "Data"

df_ventas = pd.read_csv(os.path.join(BASE_DIR, folder_name, "fuente1_ventas_sql.csv"))

with open(os.path.join(BASE_DIR, folder_name, "fuente2_csat_api.json"), "r") as f:
    df_csat = pd.DataFrame(json.load(f)["metricas"])

df_costos = pd.read_excel(os.path.join(BASE_DIR, folder_name, "fuente3_costos_excel.xlsx"))

# Merge de DataFrames
df_master = df_ventas.merge(df_csat, on="industria", how="left").merge(df_costos, on="industria", how="left")

import plotly.express as px

# Encabezado
st.title("📊 Global Insights Analytics — Executive Dashboard")
st.markdown("**Solución Integral de Visualización de Datos Multi-Industria**")

# Sidebar - Filtros Dinámicos
st.sidebar.header("🔍 Filtros de Negocio")
industria_sel = st.sidebar.multiselect(
    "Seleccionar Industria:", 
    options=df_master['industria'].unique(), 
    default=df_master['industria'].unique()
)
region_sel = st.sidebar.multiselect(
    "Seleccionar Región:", 
    options=df_master['region'].unique(), 
    default=df_master['region'].unique()
)

# Aplicar Filtros
df_filtered = df_master[(df_master['industria'].isin(industria_sel)) & (df_master['region'].isin(region_sel))]

st.divider()

# 1. Tarjetas de KPIs Principales
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Ingresos Totales", f"${df_filtered['monto_usd'].sum():,.2f} USD")
kpi2.metric("Nº Transacciones", f"{len(df_filtered):,}")

csat_val = df_filtered['csat_score'].mean() if 'csat_score' in df_filtered.columns else 0
kpi3.metric("CSAT Promedio", f"{csat_val:.2f} / 5.0")

efic_val = df_filtered['indice_eficiencia'].mean() if 'indice_eficiencia' in df_filtered.columns else 0
kpi4.metric("Índice Eficiencia", f"{efic_val:.1f}%")

st.divider()

# 2. Bloque de Gráficos (Organizados en Grid 2x2)
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Ingresos Totales por Industria")
    fig_bar = px.bar(
        df_filtered.groupby("industria")["monto_usd"].sum().reset_index(), 
        x="industria", y="monto_usd", color="industria", text_auto='.2s'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("⭐ Satisfacción (CSAT) por Industria")
    if 'csat_score' in df_filtered.columns:
        fig_csat = px.bar(
            df_filtered[['industria', 'csat_score']].drop_duplicates(), 
            x="industria", y="csat_score", color="industria"
        )
        st.plotly_chart(fig_csat, use_container_width=True)

with col2:
    st.subheader("🌍 Distribución de Ventas por Región")
    fig_pie = px.pie(df_filtered, names="region", values="monto_usd", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("⚡ Eficiencia Operativa por Industria")
    if 'indice_eficiencia' in df_filtered.columns:
        fig_efic = px.bar(
            df_filtered[['industria', 'indice_eficiencia']].drop_duplicates(), 
            x="industria", y="indice_eficiencia", color="industria"
        )
        st.plotly_chart(fig_efic, use_container_width=True)
