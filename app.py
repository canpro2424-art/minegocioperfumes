import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema POS Perfumería", layout="wide")

# --- BASES DE DATOS (INICIALIZACIÓN) ---
if 'productos' not in st.session_state:
    st.session_state.productos = pd.DataFrame(columns=["Nombre", "Venta", "Stock"])
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=["Nombre", "Deuda", "Teléfono"])
if 'ventas_dia' not in st.session_state:
    st.session_state.ventas_dia = pd.DataFrame(columns=["Fecha", "Producto", "Total", "Detalle_Pago", "Cliente"])
if 'historial_cuentas' not in st.session_state:
    st.session_state.historial_cuentas = pd.DataFrame(columns=["Fecha", "Cliente", "Concepto", "Cargo", "Abono", "Saldo"])

# --- FUNCIONES DE LÓGICA ---
def actualizar_deuda(cliente_nom, concepto_mov, monto_cargo, monto_abono):
    if cliente_nom != "Venta General":
        idx = st.session_state.clientes[st.session_state.clientes["Nombre"] == cliente_nom].index[0]
        saldo_ant = st.session_state.clientes.at[idx, "Deuda"]
        nuevo_saldo = saldo_ant + monto_cargo - monto_abono
        st.session_state.clientes.at[idx, "Deuda"] = nuevo_saldo
        
        # Guardar en historial
        reg = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Cliente": cliente_nom,
            "Concepto": concepto_mov,
            "Cargo": monto_cargo,
            "Abono": monto_abono,
            "Saldo": nuevo_saldo
        }])
        st.session_state.historial_cuentas = pd.concat([st.session_state.historial_cuentas, reg], ignore_index=True)

# --- NAVEGACIÓN ---
t1, t2, t3, t4, t5 = st.tabs(["🛒 VENTAS", "📦 PRODUCTOS", "👥 CLIENTES", "📜 ESTADOS DE CUENTA", "💰 CORTE"])

# --- TAB 1: VENTAS ---
with t1:
    st.header("Punto de Venta")
    if st.session_state.productos.empty:
        st.warning("⚠️ Primero registra tus perfumes en la pestaña 'PRODUCTOS'.")
    else:
        with st.container():
            col_a, col_b = st.columns(2)
            with col_a:
                prod_nom = st.selectbox("Elegir Perfume", st.session_state.productos["Nombre"].unique())
                cant = st.number_input("Cantidad", min_value=1, value=1)
                p_idx = st.session_state.productos[st.session_state.productos["Nombre"] == prod_nom].index[0]
                total_a_cobrar = st.session_state.productos.at[p_idx, "Venta"] * cant
                st.markdown(f"## TOTAL: S/. {total_a_cobrar:.2f}")
                cliente_v = st.selectbox("Cliente", ["Venta
