import streamlit as st
import pandas as pd

st.set_page_config(page_title="Perfumes", layout="wide")

# BASES DE DATOS
if 'prod' not in st.session_state:
    st.session_state.prod = pd.DataFrame(columns=["Nombre", "Precio", "Stock"])
if 'cli' not in st.session_state:
    st.session_state.cli = pd.DataFrame(columns=["Nombre", "Deuda"])
if 'vnt' not in st.session_state:
    st.session_state.vnt = pd.DataFrame(columns=["Producto", "Total", "Cliente"])

# NAVEGACION
t1, t2, t3 = st.tabs(["VENTAS", "PRODUCTOS", "CLIENTES"])

with t2:
    st.header("Productos")
    with st.form("f1"):
        n = st.text_input("Nombre")
        p = st.number_input("Precio", min_value=0.0)
        s = st.number_input("Stock", min_value=0)
        if st.form_submit_button("Guardar"):
            df = pd.DataFrame([{"Nombre":n, "Precio":p, "Stock":s}])
            st.session_state.prod = pd.concat([st.session_state.prod, df])
            st.rerun()
    st.dataframe(st.session_state.prod)

with t3:
    st.header("Clientes")
    with st.form("f2"):
        nc = st.text_input("Nombre Cliente")
        if st.form_submit_button("Registrar"):
            dfc = pd.DataFrame([{"Nombre":nc, "Deuda":0.0}])
            st.session_state.cli = pd.concat([st.session_state.cli, dfc])
            st.rerun()
    st.dataframe(st.session_state.cli)

with t1:
    st.header("Ventas")
    if st.session_state.prod.empty:
        st.write("Agregue productos primero")
    else:
        ps = st.selectbox("Perfume", st.session_state.prod["Nombre"].unique())
        cant = st.number_input("Cant", min_value=1)
        cl = st.selectbox("Cliente", ["General"] + list(st.session_state.cli["Nombre"].unique()))
        
        if st.button("COBRAR"):
            st.success("Venta Realizada")
            st.balloons()
