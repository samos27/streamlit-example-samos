import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Análisis de Ventas y Profitabilidad")

# Load data
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    # Convert 'Order Date' to datetime objects for proper filtering
    # Assuming 'Order Date' is in days since 1899-12-30 (Excel's epoch)
@st.cache_data
def load_data(path):
    # Carga los datos y convierte la columna 'Order Date' a datetime inmediatamente
    df = pd.read_excel(path, parse_dates=['Order Date']) 
    return df

# Elimina la línea de conversión posterior:
# df['Order Date'] = pd.to_datetime(df['Order Date'], unit='D', origin='1899-12-30')
    return df

df_orders = load_data('OrdersFinal.xlsx')

# --- Region Filter ---
st.sidebar.header("Filtro por Región")
regions = df_orders['Region'].unique().tolist()
selected_region = st.sidebar.selectbox('Selecciona una Región', ['Todas'] + regions)

if selected_region != 'Todas':
    filtered_df = df_orders[df_orders['Region'] == selected_region]
    chart_title_suffix = f' en {selected_region}'
else:
    filtered_df = df_orders
    chart_title_suffix = ''

# --- State Filter (dependent on Region) ---
st.sidebar.header("Filtro por Estado")
# Get unique states based on the current filtered_df (which is already filtered by region if applicable)
states = filtered_df['State'].unique().tolist()
selected_state = st.sidebar.selectbox('Selecciona un Estado', ['Todos'] + states)

if selected_state != 'Todos':
    filtered_df = filtered_df[filtered_df['State'] == selected_state]
    if chart_title_suffix:
        chart_title_suffix = f'{chart_title_suffix}, {selected_state}'
    else:
        chart_title_suffix = f' en {selected_state}'
else:
    # If 'Todos' states, the filtered_df remains as filtered by region only
    pass

# --- Date Filter ---
st.sidebar.header("Filtro por Fecha")
# 1. Quita los valores nulos (NaT) antes de calcular el mínimo.
# 2. Usa .min() para obtener la fecha más antigua.
# 3. Usa .date() para obtener solo el componente de fecha (sin hora).

# La versión segura:
# dashboardventas2025.py (Línea 61)

# Primero, filtramos la serie para quitar NaT
date_series = filtered_df['Order Date'].dropna()

# Luego, verificamos si la serie filtrada tiene datos.
if not date_series.empty:
    min_date = date_series.min().date()
    max_date = date_series.max().date()
else:
    # Si no hay datos (la serie está vacía después del filtro), usa la fecha de hoy.
    min_date = pd.Timestamp.now().date()
    max_date = pd.Timestamp.now().date()

# Ahora puedes usar min_date y max_date con st.date_input
# ...
max_date = filtered_df['Order Date'].max().date() if not filtered_df.empty else pd.Timestamp.now().date()

start_date = st.sidebar.date_input('Fecha de Inicio', value=min_date)
end_date = st.sidebar.date_input('Fecha de Fin', value=max_date)

# Ensure start_date is not after end_date
if start_date > end_date:
    st.sidebar.error('Error: La fecha de inicio no puede ser posterior a la fecha de fin.')
else:
    filtered_df = filtered_df[(filtered_df['Order Date'].dt.date >= start_date) & 
                              (filtered_df['Order Date'].dt.date <= end_date)]
    if chart_title_suffix:
        chart_title_suffix = f'{chart_title_suffix}, del {start_date} al {end_date}'
    else:
        chart_title_suffix = f' del {start_date} al {end_date}'

# --- Top 5 Most Sold Products Chart ---
st.header("Top 5 Productos Más Vendidos por Cantidad")
if not filtered_df.empty:
    top_products = filtered_df.groupby('Product Name')['Quantity'].sum().nlargest(5).reset_index()
    fig_sold = px.bar(top_products, x='Product Name', y='Quantity', 
                      title=f'Top 5 Productos Más Vendidos por Cantidad{chart_title_suffix}',
                      labels={'Product Name': 'Producto', 'Quantity': 'Cantidad Total Vendida'})
    st.plotly_chart(fig_sold, use_container_width=True)
else:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")

# --- Top 5 Products by Profit Chart ---
st.header("Top 5 Productos por Profit")
if not filtered_df.empty:
    top_profit_products = filtered_df.groupby('Product Name')['Profit'].sum().nlargest(5).reset_index()
    fig_profit = px.bar(top_profit_products, x='Product Name', y='Profit', 
                         title=f'Top 5 Productos por Profit{chart_title_suffix}',
                         labels={'Product Name': 'Producto', 'Profit': 'Profit Total'})
    st.plotly_chart(fig_profit, use_container_width=True)
else:
    st.warning("No hay datos para mostrar con los filtros seleccionados.")
