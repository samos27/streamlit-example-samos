
# Load data
@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    return df
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Análisis de Ventas y Profitabilidad")

df_orders = load_data('OrdersFinal.xlsx')

# --- Top 5 Most Sold Products Chart ---
st.header("Top 5 Productos Más Vendidos por Cantidad")
top_products = df_orders.groupby('Product Name')['Quantity'].sum().nlargest(5).reset_index()
fig_sold = px.bar(top_products, x='Product Name', y='Quantity', 
                  title='Top 5 Productos Más Vendidos por Cantidad',
                  labels={'Product Name': 'Producto', 'Quantity': 'Cantidad Total Vendida'})
st.plotly_chart(fig_sold, use_container_width=True)

# --- Top 5 Products by Profit Chart ---
st.header("Top 5 Productos por Profit")
top_profit_products = df_orders.groupby('Product Name')['Profit'].sum().nlargest(5).reset_index()
fig_profit = px.bar(top_profit_products, x='Product Name', y='Profit', 
                     title='Top 5 Productos por Profit',
                     labels={'Product Name': 'Producto', 'Profit': 'Profit Total'})
st.plotly_chart(fig_profit, use_container_width=True)
