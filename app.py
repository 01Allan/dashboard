# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import plotly.express as px

# engine = create_engine('sqlite:///../solucion/database/destino.db')
engine = create_engine('sqlite:///database/destino.db')

@st.cache_data
def cargar_datos():
    query = "SELECT * FROM ordenes_compra_unificadas;"
    df = pd.read_sql(query, con=engine)
    return df

# Configuración de página
st.set_page_config(
    page_title="Dashboard Órdenes de Compra",
    page_icon="AP",
    layout="wide"
)

st.title("Dashboard de Órdenes de Compra")

# Cargar datos
df = cargar_datos()
df = df.dropna(subset=["mes_act"])
df["mes_act"] = df["mes_act"].astype(int)
df["mes_act_str"] = df["mes_act"].astype(str)
df["mes_act_str"] = df["mes_act_str"].str.slice(0, 4) + "-" + df["mes_act_str"].str.slice(4, 6)

# Filtros
st.sidebar.header("Filtros")
ubicaciones = st.sidebar.multiselect(
    "Selecciona ubicaciones:", 
    options=df["ubicación"].unique(),
    default=df["ubicación"].unique()
)

meses = st.sidebar.multiselect(
    "Selecciona meses (mes_act):", 
    options=df["mes_act"].sort_values().unique(),
    default=df["mes_act"].sort_values().unique()
)

# Aplicar filtros
df_filtrado = df[
    (df["ubicación"].isin(ubicaciones)) &
    (df["mes_act"].isin(meses))
]

# KPIs
st.subheader("Indicadores Clave (KPIs)")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Órdenes Totales", value=f"{len(df_filtrado):,}")
with col2:
    st.metric(label="Productos Diferentes", value=f"{df_filtrado['codigo_producto'].nunique():,}")
with col3:
    st.metric(label="Ubicaciones", value=f"{df_filtrado['ubicación'].nunique():,}")

st.markdown("---")

# Mostrar datos
st.subheader("Tabla de Órdenes de Compra")
st.dataframe(df_filtrado, use_container_width=True)

# Gráficos
st.subheader("📈 Evolución de Ventas (Cantidad) por Ubicación")

ventas_por_mes = df_filtrado.groupby(["mes_act_str", "ubicación"])["cantidad"].sum().reset_index()
ventas_por_mes = ventas_por_mes.sort_values(by="mes_act_str")

fig = px.line(
    ventas_por_mes,
    x="mes_act_str",
    y="cantidad",
    color="ubicación",
    markers=True,
    line_shape="spline", 
    title="Evolución de Ventas por Ubicación",
    labels={
        "mes_act_str": "Mes",
        "cantidad": "Cantidad de Órdenes",
        "ubicación": "Ubicación"
    }
)

fig.update_layout(
    xaxis_title="Mes (YYYY-MM)",
    yaxis_title="Cantidad de Órdenes",
    title_x=0.5,
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# Gráfico de Barras Apiladas

st.subheader("📊 Órdenes por Mes y Ubicación (Barras Apiladas)")

ventas_por_mes = df_filtrado.groupby(["mes_act_str", "ubicación"])["cantidad"].sum().reset_index()
ventas_por_mes = ventas_por_mes.sort_values(by="mes_act_str")

fig_stacked = px.bar(
    ventas_por_mes,
    x="mes_act_str",
    y="cantidad",
    color="ubicación",
    title="Órdenes por Mes y Ubicación",
    labels={
        "mes_act_str": "Mes",
        "cantidad": "Cantidad de Órdenes",
        "ubicación": "Ubicación"
    },
    text_auto=True
)

fig_stacked.update_layout(
    barmode="stack",
    xaxis_title="Mes",
    yaxis_title="Cantidad de Órdenes",
    title_x=0.5,
    template="plotly_white"
)

st.plotly_chart(fig_stacked, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Desarrollado por Allan Pineda | Prueba Tecnica Evaluación Ingeniería de Datos")