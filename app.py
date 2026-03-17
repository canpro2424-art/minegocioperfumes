import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de pantalla ancha y título
st.set_page_config(page_title="eleventa - Punto de Venta", layout="wide")

# Estilo para imitar la barra de navegación gris/azul de eleventa
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; border-radius: 4px 4px 0px 0px;
        padding: 10px 20px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background-color: #0056b3 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BASES DE DATOS (ESTADO DE SESIÓN) ---
if 'productos' not in st.session_state:
    st.session_state.productos = pd.DataFrame(columns=["Código", "Descripción", "Costo", "Precio Venta", "Stock", "Mínimo"])
if 'ventas' not in st.session_state:
    st.session_state.ventas = pd.DataFrame(columns=["Fecha", "Producto", "Monto", "Método", "Costo_Ref"])
if 'fondo_caja' not in st.session_state:
    st.session_state.fondo_caja = 450.0  # Como en el video [00:01:51]

# --- TABS SUPERIORES (BARRA DE NAVEGACIÓN) ---
# F1: Ventas, F2: Clientes, F3: Productos, F4: Inventario, F5: Config, F6: Corte
t1, t2, t3, t4, t5 = st.tabs(["🛒 F1 VENTAS", "👥 F2 CLIENTES", "📦 F3 PRODUCTOS", "📋 F4 INVENTARIO", "💰 F5 CORTE"])

# --- MODULO VENTAS ---
with t1:
    st.subheader("Venta de Productos")
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        with st.form("caja_venta"):
            cod = st.text_input("Código o nombre del perfume")
            cant = st.number_input("Cantidad", min_value=1, value=1)
            btn_v = st.form_submit_button("AGREGAR ARTÍCULO")
            if btn_v:
                # Lógica simplificada de búsqueda
                prod_data = st.session_state.productos[st.session_state.productos["Nombre"] == cod]
                if not prod_data.empty:
                    st.success(f"Agregado: {cod}")
                else:
                    st.error("Producto no encontrado")
    with col_v2:
        st.markdown("### TOTAL: S/. 0.00")
        st.button("✅ COBRAR (F12)")

# --- MODULO CLIENTES ---
with t2:
    st.subheader("Administración de Clientes")
    st.button("➕ Nuevo Cliente")
    st.button("📝 Estado de Cuenta")

# --- MODULO PRODUCTOS ---
with t3:
    st.subheader("Catálogo de Productos")
    with st.expander("Nuevo Producto"):
        with st.form("add_p"):
            n = st.text_input("Descripción / Nombre")
            c1, c2, c3 = st.columns(3)
            with c1: cost = st.number_input("Costo", min_value=0.0)
            with c2: prev = st.number_input("Precio Venta", min_value=0.0)
            with c3: stock = st.number_input("Inventario Inicial", min_value=0)
            if st.form_submit_button("Guardar Producto"):
                nuevo = pd.DataFrame([{"Nombre": n, "Costo": cost, "Precio Venta": prev, "Stock": stock, "Mínimo": 2}])
                st.session_state.productos = pd.concat([st.session_state.productos, nuevo], ignore_index=True)
    st.table(st.session_state.productos)

# --- MODULO INVENTARIO (KARDEX) ---
with t4:
    st.subheader("Control de Inventarios")
    op = st.radio("Acción", ["Reporte de Inventario", "Agregar Stock", "Kardex de Movimientos"], horizontal=True)
    if op == "Reporte de Inventario":
        st.dataframe(st.session_state.productos, use_container_width=True)

# --- MODULO CORTE (COMO EN EL VIDEO) ---
with t5:
    st.header(f"Corte de Caja - {datetime.now().strftime('%d/%m/%Y')}")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.metric("Fondo de Caja inicial", f"S/. {st.session_state.fondo_caja}")
        st.metric("Ventas Totales", f"S/. {st.session_state.ventas['Monto'].sum():.2f}")
    with col_c2:
        efectivo_total = st.session_state.fondo_caja + st.session_state.ventas['Monto'].sum()
        st.metric("Efectivo esperado en caja", f"S/. {efectivo_total:.2f}")
    
    if st.button("🔴 HACER CORTE DEL DÍA"):
        st.warning("Cerrando caja y generando reporte...")
