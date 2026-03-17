import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Perfumeria Pro", layout="wide")

# 1. BASES DE DATOS
for key in ['prod','cli','vnt','hist']:
    if key not in st.session_state:
        if key == 'prod': st.session_state.prod = pd.DataFrame(columns=["Nombre", "Venta", "Stock"])
        if key == 'cli': st.session_state.cli = pd.DataFrame(columns=["Nombre", "Deuda", "WhatsApp"])
        if key == 'vnt': st.session_state.vnt = pd.DataFrame(columns=["Fecha", "Producto", "Total", "Pago", "Cliente"])
        if key == 'hist': st.session_state.hist = pd.DataFrame(columns=["Fecha", "Cliente", "Concepto", "Cargo", "Abono", "Saldo"])

def act_deuda(c_nom, concepto, cargo, abono):
    if c_nom != "Venta General":
        idx = st.session_state.cli[st.session_state.cli["Nombre"] == c_nom].index[0]
        s_ant = st.session_state.cli.at[idx, "Deuda"]
        n_s = s_ant + cargo - abono
        st.session_state.cli.at[idx, "Deuda"] = n_s
        nuevo_h = pd.DataFrame([{"Fecha": datetime.now().strftime("%d/%m/%Y"), "Cliente": c_nom, "Concepto": concepto, "Cargo": cargo, "Abono": abono, "Saldo": n_s}])
        st.session_state.hist = pd.concat([st.session_state.hist, nuevo_h], ignore_index=True)

# 2. NAVEGACIÓN
t1, t2, t3, t4, t5 = st.tabs(["🛒 VENTAS", "📦 PRODUCTOS", "👥 CLIENTES", "📜 CUENTAS", "💰 CORTE"])

with t1:
    st.header("Ventas")
    if st.session_state.prod.empty:
        st.warning("Agregue productos en la pestaña PRODUCTOS primero.")
    else:
        c_a, c_b = st.columns(2)
        with c_a:
            p_sel = st.selectbox("Perfume", st.session_state.prod["Nombre"].unique())
            cant = st.number_input("Cantidad", min_value=1, value=1)
            p_idx = st.session_state.prod[st.session_state.prod["Nombre"] == p_sel].index[0]
            precio_v = st.session_state.prod.at[p_idx, "Venta"]
            total = precio_v * cant
            st.write("Total a cobrar: S/.", total)
            clie = st.selectbox("Cliente", ["Venta General"] + list(st.session_state.cli["Nombre"].unique()))
        with c_b:
            efec = st.number_input("S/. Efectivo", min_value=0.0)
            tarj = st.number_input("S/. Tarjeta/Yape", min_value=0.0)
            falta = total - (efec + tarj)
            if falta > 0: st.error("Falta: S/. " + str(falta))
            if st.button("COBRAR"):
                st.session_state.prod.at[p_idx, "Stock"] -= cant
                # Detalle de pago sin usar f-strings para evitar errores de comillas
                det_pago = "Efe: " + str(efec) + " Tarj: " + str(tarj)
                if falta > 0:
                    if clie == "Venta General": st.error("No se puede fiar a Venta General")
                    else:
                        act_deuda(clie, "Compra de " + p_sel, falta, 0)
                        det_pago = det_pago + " Cred: " + str(falta)
                nv = pd.DataFrame([{"Fecha": datetime.now(), "Producto
