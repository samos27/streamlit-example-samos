import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Análisis de Ventas y Profitabilidad")

# Load data
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
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
