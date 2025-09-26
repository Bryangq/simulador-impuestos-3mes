import streamlit as st
import pandas as pd
import os

st.title("📊 Control de impuestos trimestrales (Autónomos)")

# ======================
# SELECCIÓN DE TRIMESTRE
# ======================
trimestre = st.selectbox(
    "Selecciona el trimestre",
    ["1T", "2T", "3T", "4T"],
    index=0
)

# Archivos dinámicos por trimestre
INGRESOS_FILE = f"ingresos_{trimestre}.csv"
GASTOS_FILE = f"gastos_{trimestre}.csv"

# ======================
# FUNCIONES AUXILIARES
# ======================
def cargar_datos():
    ingresos = pd.read_csv(INGRESOS_FILE) if os.path.exists(INGRESOS_FILE) else pd.DataFrame(columns=["Importe", "IVA"])
    gastos = pd.read_csv(GASTOS_FILE) if os.path.exists(GASTOS_FILE) else pd.DataFrame(columns=["Importe"])
    return ingresos, gastos

def guardar_datos(df, file):
    df.to_csv(file, index=False)

# ======================
# CARGAR O CREAR DATOS
# ======================
if "ingresos" not in st.session_state or "gastos" not in st.session_state or st.session_state.get("trimestre") != trimestre:
    ingresos, gastos = cargar_datos()
    st.session_state.ingresos = ingresos
    st.session_state.gastos = gastos
    st.session_state.trimestre = trimestre

# ======================
# ENTRADA DE INGRESOS
# ======================
st.subheader("💶 Registrar ingreso (factura)")

nuevo_ingreso = st.number_input("Importe base imponible (€)", min_value=0.0, step=50.0, key="input_ingreso")
tipo_iva = st.selectbox("Tipo de IVA", [0.10, 0.21], index=0, key="tipo_ingreso")

if st.button("➕ Añadir ingreso"):
    nuevo = pd.DataFrame([{"Importe": nuevo_ingreso, "IVA": tipo_iva}])
    st.session_state.ingresos = pd.concat([st.session_state.ingresos, nuevo], ignore_index=True)
    guardar_datos(st.session_state.ingresos, INGRESOS_FILE)
    st.success(f"Ingreso de {nuevo_ingreso:.2f} € añadido y guardado.")

# ======================
# ENTRADA DE GASTOS
# ======================
st.subheader("🧾 Registrar gasto")

nuevo_gasto = st.number_input("Importe gasto base imponible (€)", min_value=0.0, step=20.0, key="input_gasto")

if st.button("➕ Añadir gasto"):
    nuevo = pd.DataFrame([{"Importe": nuevo_gasto}])
    st.session_state.gastos = pd.concat([st.session_state.gastos, nuevo], ignore_index=True)
    guardar_datos(st.session_state.gastos, GASTOS_FILE)
    st.success(f"Gasto de {nuevo_gasto:.2f} € añadido y guardado.")

# ======================
# CÁLCULOS ACUMULADOS
# ======================
st.subheader("📈 Resumen acumulado del trimestre")

# Calcular ingresos
total_ingresos = st.session_state.ingresos["Importe"].sum()
total_iva_repercutido = (st.session_state.ingresos["Importe"] * st.session_state.ingresos["IVA"]).sum()
total_irpf = total_ingresos * 0.20

# Calcular gastos
total_gastos = st.session_state.gastos["Importe"].sum()
total_iva_soportado = total_gastos * 0.21  # suponemos 21% en gastos
total_irpf_gastos = total_gastos * 0.20    # 20% de los gastos deducibles en IRPF


# Resultados finales
iva_a_pagar = total_iva_repercutido - total_iva_soportado
irpf_a_pagar = (total_ingresos - total_gastos) * 0.20
total_a_pagar = iva_a_pagar + irpf_a_pagar

st.write(f"**Ingresos acumulados:** {total_ingresos:.2f} €")
st.write(f"IVA repercutido acumulado: {total_iva_repercutido:.2f} €")
st.write(f"IRPF acumulado: {total_irpf:.2f} €")

st.write(f"**Gastos acumulados:** {total_gastos:.2f} €")
st.write(f"IVA soportado acumulado: {total_iva_soportado:.2f} €")
st.write(f"IRPF deducible por gastos: {total_irpf_gastos:.2f} €")

st.subheader("💰 Impuestos a pagar al final del trimestre")
st.write(f"IVA a pagar: {iva_a_pagar:.2f} €")
st.write(f"IRPF a pagar: {irpf_a_pagar:.2f} €")
st.success(f"TOTAL a pagar: {total_a_pagar:.2f} €")

# ======================
# --- TOGGLE PERSISTENTE PARA MOSTRAR/OCULTAR ACUMULADO ---
if "show_acum" not in st.session_state:
    st.session_state.show_acum = False

if st.button("📋 Ver acumulado" if not st.session_state.show_acum else "🔽 Ocultar acumulado"):
    st.session_state.show_acum = not st.session_state.show_acum

# Variable de confirmación
# st.session_state.confirm = {"kind": "ingreso"/"gasto", "idx": i}  # cuando toque

if st.session_state.show_acum:
    st.subheader("📊 Ingresos registrados")
    if not st.session_state.ingresos.empty:
        # Totales
        total_importe_ing = st.session_state.ingresos["Importe"].sum()
        total_iva_ing = (st.session_state.ingresos["Importe"] * st.session_state.ingresos["IVA"]).sum()
        total_irpf_ing = (st.session_state.ingresos["Importe"] * 0.20).sum()

        # Filas con botón eliminar + IRPF
        for i in range(len(st.session_state.ingresos)):
            row = st.session_state.ingresos.iloc[i]
            c1, c2, c3, c4, c5 = st.columns([2,2,2,2,1])
            c1.write(f"💶 {row['Importe']:.2f} €")
            c2.write(f"IVA: {row['IVA']*100:.0f}%")
            c3.write(f"IVA Repercutido: {row['Importe']*row['IVA']:.2f} €")
            c4.write(f"IRPF (20%): {row['Importe']*0.20:.2f} €")
            if c5.button("❌", key=f"del_ing_{i}"):
                st.session_state.confirm = {"kind": "ingreso", "idx": i}

        st.markdown("---")
        st.success(f"**TOTAL Ingresos → Importe: {total_importe_ing:.2f} € | IVA: {total_iva_ing:.2f} € | IRPF: {total_irpf_ing:.2f} €**")
    else:
        st.info("Todavía no has registrado ingresos.")

    st.subheader("📊 Gastos registrados")
    if not st.session_state.gastos.empty:
        # Totales
        total_importe_gas = st.session_state.gastos["Importe"].sum()
        total_iva_gas = (st.session_state.gastos["Importe"] * 0.21).sum()
        total_irpf_gas = (st.session_state.gastos["Importe"] * 0.20).sum()

        for i in range(len(st.session_state.gastos)):
            row = st.session_state.gastos.iloc[i]
            c1, c2, c3, c4 = st.columns([3,3,3,1])
            c1.write(f"🧾 {row['Importe']:.2f} €")
            c2.write(f"IVA Soportado: {row['Importe']*0.21:.2f} €")
            c3.write(f"IRPF Deducible (20%): {row['Importe']*0.20:.2f} €")
            if c4.button("❌", key=f"del_gas_{i}"):
                st.session_state.confirm = {"kind": "gasto", "idx": i}

        st.markdown("---")
        st.success(f"**TOTAL Gastos → Importe: {total_importe_gas:.2f} € | IVA: {total_iva_gas:.2f} € | IRPF: {total_irpf_gas:.2f} €**")
    else:
        st.info("Todavía no has registrado gastos.")

    # --- DIÁLOGO DE CONFIRMACIÓN ---
    if "confirm" in st.session_state:
        kind = st.session_state.confirm["kind"]
        idx = st.session_state.confirm["idx"]

        if kind == "ingreso" and idx < len(st.session_state.ingresos):
            importe_txt = f"{st.session_state.ingresos.iloc[idx]['Importe']:.2f} €"
            borrar = lambda: (
                st.session_state.ingresos.drop(st.session_state.ingresos.index[idx], inplace=True),
                st.session_state.ingresos.reset_index(drop=True, inplace=True),
                guardar_datos(st.session_state.ingresos, INGRESOS_FILE)
            )
        elif kind == "gasto" and idx < len(st.session_state.gastos):
            importe_txt = f"{st.session_state.gastos.iloc[idx]['Importe']:.2f} €"
            borrar = lambda: (
                st.session_state.gastos.drop(st.session_state.gastos.index[idx], inplace=True),
                st.session_state.gastos.reset_index(drop=True, inplace=True),
                guardar_datos(st.session_state.gastos, GASTOS_FILE)
            )
        else:
            importe_txt = "registro"
            borrar = lambda: None

        st.warning(f"⚠️ ¿Seguro que quieres eliminar el {kind} de {importe_txt}?")
        cc1, cc2 = st.columns(2)
        if cc1.button("✅ Confirmar"):
            borrar()
            del st.session_state["confirm"]
            try:
                st.rerun()
            except:
                st.rerun()
        if cc2.button("❌ Cancelar"):
            del st.session_state["confirm"]
            try:
                st.rerun()
            except:
                st.rerun()