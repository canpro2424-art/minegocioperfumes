import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema POS Todo-en-Uno", layout="wide")

# --- BASES DE DATOS (INICIALIZACIÓN) ---
if 'productos' not in st.session_state:
    st.session_state.productos = pd.DataFrame(columns=["Código", "Nombre", "Venta", "Stock"])
if 'clientes' not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=["Nombre", "Deuda", "Teléfono"])
if 'ventas_dia' not in st.session_state:
    st.session_state.ventas_dia = pd.DataFrame(columns=["Fecha", "Producto", "Total", "Detalle_Pago", "Cliente"])
if 'historial_cuentas' not in st.session_state:
    st.session_state.historial_cuentas = pd.DataFrame(columns=["Fecha", "Cliente", "Concepto", "Cargo", "Abono", "Saldo"])

# --- FUNCIONES DE LÓGICA ---
def actualizar_deuda(cliente, concepto, cargo, abono):
    if cliente != "Venta General":
        idx = st.session_state.clientes[st.session_state.clientes["Nombre"] == cliente].index[0]
        saldo_ant = st.session_state.clientes.at[idx, "Deuda"]
        nuevo_saldo = saldo_ant + cargo - abono
        st.session_state.clientes.at[idx, "Deuda"] = nuevo_saldo
        # Guardar en historial
        reg = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": cliente, "Concepto": concepto, "Cargo": cargo, "Abono": abono, "Saldo": nuevo_saldo}])
        st.session_state.historial_cuentas = pd.concat([st.session_state.historial_cuentas, reg], ignore_index=True)

# --- NAVEGACIÓN ---
t1, t2, t3, t4, t5 = st.tabs(["🛒 VENTAS", "📦 PRODUCTOS", "👥 CLIENTES", "📜 ESTADOS DE CUENTA", "💰 CORTE"])

# --- TAB 1: VENTAS (CON PAGO MIXTO) ---
with t1:
    st.header("Punto de Venta")
    if st.session_state.productos.empty:
        st.warning("⚠️ No tienes productos. Ve a la pestaña 'PRODUCTOS' para registrar tu mercadería primero.")
    else:
        with st.container():
            col_a, col_b = st.columns(2)
            with col_a:
                prod_nom = st.selectbox("Elegir Perfume", st.session_state.productos["Nombre"].unique())
                cant = st.number_input("Cantidad", min_value=1, value=1)
                p_idx = st.session_state.productos[st.session_state.productos["Nombre"] == prod_nom].index[0]
                total_a_cobrar = st.session_state.productos.at[p_idx, "Venta"] * cant
                st.markdown(f"## TOTAL: S/. {total_a_cobrar:.2f}")
                cliente_v = st.selectbox("Cliente", ["Venta General"] + list(st.session_state.clientes["Nombre"].unique()))
            
            with col_b:
                st.write("💳 **Distribución de Pago**")
                p_efec = st.number_input("Efectivo S/.", min_value=0.0)
                p_tarj = st.number_input("Yape / Tarjeta S/.", min_value=0.0)
                
                faltante = total_a_cobrar - (p_efec + p_tarj)
                
                if faltante > 0:
                    st.error(f"Faltan S/. {faltante:.2f} (Se irá a CRÉDITO)")
                elif faltante < 0:
                    st.success(f"Vuelto: S/. {abs(faltante):.2f}")
                
                if st.button("CONFIRMAR COBRO"):
                    # Descontar stock
                    st.session_state.productos.at[p_idx, "Stock"] -= cant
                    # Lógica de crédito
                    det = f"Efe: {p_efec}, Tarj: {p_tarj}"
                    if faltante > 0:
                        if cliente_v == "Venta General":
                            st.error("¡No puedes dejar deuda a Venta General!")
                        else:
                            actualizar_deuda(cliente_v, f"Compra {prod_nom}", faltante, 0)
                            det += f", Crédito: {faltante}"
                            st.success("Venta procesada con crédito.")
                    
                    # Registro venta día
                    nv = pd.DataFrame([{"Fecha": datetime.now(), "Producto": prod_nom, "Total": total_a_cobrar, "Detalle_Pago": det, "Cliente": cliente_v}])
                    st.session_state.ventas_dia = pd.concat([st.session_state.ventas_dia, nv], ignore_index=True)
                    st.balloons()

# --- TAB 2: PRODUCTOS ---
with t2:
    st.header("Inventario de Perfumes")
    with st.expander("➕ Agregar Nuevo"):
        with st.form("new_p"):
            n
