import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="POS Perfumería Pro", layout="wide")

if 'productos' not in st.session_state:
    st.session_state.productos = pd.DataFrame(columns=["Nombre", "Costo", "Precio Venta", "Stock", "Ganancia Unidad"])
if 'ventas' not in st.session_state:
    st.session_state.ventas = pd.DataFrame(columns=["Fecha", "Cliente", "Producto", "Monto", "Estado", "Metodo Pago"])

st.title("🚀 POS Profesional - Gestión de Perfumería")

st.sidebar.header("Menú Principal")
menu = st.sidebar.radio("Navegación", ["🛒 Caja (Ventas)", "📦 Inventario", "👤 Clientes y Deudas", "📈 Análisis de Negocio"])

if menu == "🛒 Caja (Ventas)":
    st.header("Punto de Venta")
    with st.form("form_venta"):
        c1, c2 = st.columns(2)
        with c1:
            cliente = st.text_input("Nombre del Cliente")
            lista_prods = st.session_state.productos[st.session_state.productos["Stock"] > 0]["Nombre"].tolist()
            prod_sel = st.selectbox("Producto", lista_prods if lista_prods else ["Sin Stock"])
        with c2:
            metodo = st.selectbox("Método de Pago", ["Efectivo", "Yape/Plin", "Tarjeta"])
            monto = st.number_input("Monto (S/.)", min_value=0.0)
        if st.form_submit_button("✅ FINALIZAR VENTA"):
            nueva_v = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Cliente": cliente, "Producto": prod_sel, "Monto": monto, "Estado": "Pagado", "Metodo Pago": metodo}])
            st.session_state.ventas = pd.concat([st.session_state.ventas, nueva_v], ignore_index=True)
            st.success("Venta guardada")

elif menu == "📦 Inventario":
    st.header("Inventario")
    with st.form("nuevo_p"):
        n = st.text_input("Nombre")
        c = st.number_input("Costo", min_value=0.0)
        v = st.number_input("Venta", min_value=0.0)
        s = st.number_input("Stock", min_value=1)
        if st.form_submit_button("Guardar"):
            nuevo = pd.DataFrame([{"Nombre": n, "Costo": c, "Precio Venta": v, "Stock": s, "Ganancia Unidad": v-c}])
            st.session_state.productos = pd.concat([st.session_state.productos, nuevo], ignore_index=True)
    st.dataframe(st.session_state.productos)

elif menu == "👤 Clientes y Deudas":
    st.header("Deudas")
    st.dataframe(st.session_state.ventas)

else:
    st.header("Reportes")
    st.metric("Ventas Totales", f"S/. {st.session_state.ventas['Monto'].sum():.2f}")
