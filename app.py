import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="POS Pro - Pago Mixto", layout="wide")

# --- BASES DE DATOS ---
if 'productos' not in st.session_state:
    st.session_state.productos = pd.DataFrame(columns=["Nombre", "Venta", "Stock"])
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=["Nombre", "Deuda"])
if 'ventas_dia' not in st.session_state:
    st.session_state.ventas_dia = pd.DataFrame(columns=["Fecha", "Producto", "Total", "Detalle_Pago"])

# Función para registrar en historial de cliente (Estado de Cuenta)
def registrar_movimiento(cliente, concepto, cargo, abono):
    if cliente != "Venta General":
        idx = st.session_state.clientes[st.session_state.clientes["Nombre"] == cliente].index[0]
        st.session_state.clientes.at[idx, "Deuda"] += (cargo - abono)

# --- INTERFAZ DE VENTAS (F1) ---
st.title("🛒 Punto de Venta Profesional")

if not st.session_state.productos.empty:
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1. Selección de Venta")
            prod_nom = st.selectbox("Producto", st.session_state.productos["Nombre"].unique())
            cant = st.number_input("Cantidad", min_value=1, value=1)
            
            p_idx = st.session_state.productos[st.session_state.productos["Nombre"] == prod_nom].index[0]
            precio_unitario = st.session_state.productos.at[p_idx, "Venta"]
            total_pagar = precio_unitario * cant
            
            st.markdown(f"## TOTAL A COBRAR: S/. {total_pagar:.2f}")
            
            cliente_sel = st.selectbox("Cliente", ["Venta General"] + list(st.session_state.clientes["Nombre"].unique()))

        with col2:
            st.subheader("2. Método de Pago (Combinado)")
            st.info("Ingresa los montos según cómo te pague el cliente:")
            
            p_efectivo = st.number_input("💵 Efectivo / Cash", min_value=0.0, value=0.0)
            p_tarjeta = st.number_input("💳 Tarjeta / Transferencia / Yape", min_value=0.0, value=0.0)
            
            pago_total_ingresado = p_efectivo + p_tarjeta
            saldo_pendiente = total_pagar - pago_total_ingresado
            
            if saldo_pendiente > 0:
                st.warning(f"Faltan S/. {saldo_pendiente:.2f} que se irán a CRÉDITO.")
            elif saldo_pendiente < 0:
                st.success(f"VUELTO para el cliente: S/. {abs(saldo_pendiente):.2f}")
            else:
                st.success("Pago exacto completado.")

            if st.button("🏁 FINALIZAR Y COBRAR"):
                # 1. Descontar Stock
                st.session_state.productos.at[p_idx, "Stock"] -= cant
                
                # 2. Si hay saldo pendiente, registrar deuda (Solo si hay cliente)
                detalle = f"Efec: {p_efectivo}, Tarj: {p_tarjeta}"
                if saldo_pendiente > 0:
                    if cliente_sel == "Venta General":
                        st.error("No puedes dejar deuda a 'Venta General'. Selecciona un cliente registrado.")
                        st.stop()
                    else:
                        registrar_movimiento(cliente_sel, f"Compra {prod_nom}", saldo_pendiente, 0)
                        detalle += f", Crédito: {saldo_pendiente}"
                
                # 3.
