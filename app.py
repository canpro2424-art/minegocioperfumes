import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Perfumería Business Pro", layout="wide")

conn = sqlite3.connect('perfumes_empresa.db', check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS productos (codigo TEXT PRIMARY KEY, nombre TEXT, precio REAL, stock INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS ventas (id INTEGER PRIMARY KEY, total REAL, efectivo REAL, yape REAL, credito REAL, cliente TEXT, fecha TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY, concepto TEXT, monto REAL, fecha TEXT)')
conn.commit()

st.sidebar.title("💎 Mi Negocio de Perfumes")
menu = ["🛒 Ventas y Gastos", "📦 Inventario Pro", "👥 Deudas", "📊 Estadísticas"]
choice = st.sidebar.radio("Ir a:", menu)

if choice == "🛒 Ventas y Gastos":
    tab1, tab2 = st.tabs(["🛍️ Nueva Venta", "💸 Registrar Gasto"])
    with tab1:
        st.subheader("Punto de Venta")
        foto = st.camera_input("Escaneo de Cámara")
        df_p = pd.read_sql_query("SELECT * FROM productos", conn)
        busqueda = st.selectbox("Buscar por nombre o código:", [""] + df_p['nombre'].tolist() + df_p['codigo'].tolist())
        if busqueda:
            p_data = df_p[(df_p['nombre'] == busqueda) | (df_p['codigo'] == busqueda)].iloc[0]
            st.info(f"Producto: {p_data['nombre']} | Stock: {p_data['stock']}")
            cant = st.number_input("Cantidad", min_value=1, max_value=int(p_data['stock']), value=1)
            total = p_data['precio'] * cant
            st.write(f"### TOTAL: ${total:.2f}")
            c1, c2 = st.columns(2)
            p_efectivo = c1.number_input("Efectivo $", min_value=0.0)
            p_yape = c2.number_input("Yape/Transf $", min_value=0.0)
            deuda = max(0.0, total - (p_efectivo + p_yape))
            cliente = st.text_input("Nombre del Cliente") if deuda > 0 else "Venta General"
            if st.button("Finalizar Cobro"):
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute("INSERT INTO ventas (total, efectivo, yape, credito, cliente, fecha) VALUES (?,?,?,?,?,?)", (total, p_efectivo, p_yape, deuda, cliente, fecha))
                c.execute("UPDATE productos SET stock = stock - ? WHERE codigo = ?", (cant, p_data['codigo']))
                conn.commit()
                st.success("Venta Guardada")
                st.balloons()
    with tab2:
        st.subheader("Gastos")
        concepto = st.text_input("Concepto")
        monto_g = st.number_input("Monto $", min_value=0.1)
        if st.button("Guardar Gasto"):
            c.execute("INSERT INTO gastos (concepto, monto, fecha) VALUES (?,?,?)", (concepto, monto_g, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("Gasto registrado")

elif choice == "📦 Inventario Pro":
    st.header("Inventario")
    with st.expander("➕ Nuevo Perfume"):
        c_cod = st.text_input("Código")
        c_nom = st.text_input("Nombre")
        c_pre = st.number_input("Precio", min_value=0.0)
        c_sto = st.number_input("Stock", min_value=0)
        if st.button("Añadir"):
            c.execute("INSERT OR REPLACE INTO productos VALUES (?,?,?,?)", (c_cod, c_nom, c_pre, c_sto))
            conn.commit()
            st.success("Registrado")
    st.dataframe(pd.read_sql_query("SELECT * FROM productos", conn), use_container_width=True)

elif choice == "📊 Estadísticas":
    st.header("Análisis de Ventas")
    df_v = pd.read_sql_query("SELECT * FROM ventas", conn)
    df_g = pd.read_sql_query("SELECT * FROM gastos", conn)
    if not df_v.empty:
        df_v['fecha'] = pd.to_datetime(df_v['fecha'])
        resumen = df_v.groupby(df_v['fecha'].dt.date)['total'].sum().reset_index()
        st.plotly_chart(px.bar(resumen, x='fecha', y='total', title="Ventas por Día"), use_container_width=True)
        st.metric("Ventas Totales", f"${df_v['total'].sum():.2f}")
        st.metric("Gastos Totales", f"-${df_g['monto'].sum():.2f}")
        st.success(f"Ganancia Neta: ${df_v['total'].sum() - df_g['monto'].sum():.2f}")
    else:
        st.info("Sin datos.")
