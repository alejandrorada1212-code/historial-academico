import streamlit as st
import requests
import math
import streamlit.components.v1 as components
from bs4 import BeautifulSoup

# --------------------------------------------------
# UTILIDADES
# --------------------------------------------------
def to_float(valor):
    try:
        return float(valor.replace(",", "."))
    except:
        return 0.0


def redondear_nota(nota):
    base = math.floor(nota * 10) / 10
    segundo_decimal = int((nota * 100) % 10)
    if segundo_decimal >= 6:
        return round(base + 0.1, 1)
    return round(base, 1)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "logged" not in st.session_state:
    st.session_state.logged = False

if "session" not in st.session_state:
    st.session_state.session = None

if "codigo" not in st.session_state:
    st.session_state.codigo = None


# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(page_title="Historia académica", layout="wide")

# Fuente Roboto (GLOBAL)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# PANTALLA 1: LOGIN (NO TOCAR)
# --------------------------------------------------
def pantalla_login():
    st.title("🔐 Ingreso al sistema académico")

    with st.form("login"):
        codprs = st.text_input("Código de estudiante")
        pswprs = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")

    if not submit:
        return

    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0"}

    session.get("https://sma.unicartagena.edu.co:8443/Smaix12/", headers=headers)

    payload = {
        "codcia": "UDC",
        "codprs": codprs,
        "pswprs": pswprs,
        "logout": "In"
    }

    login_url = "https://sma.unicartagena.edu.co:8443/Smaix12/servlet/Adm/ValidLogin"
    session.post(login_url, data=payload, headers=headers)

    historia_url = (
        "https://sma.unicartagena.edu.co:8443"
        "/Smaix12/servlet/Adm/DataStudent"
        f"?events=HRYAKD&title_=Historia%20Academica&codbas={codprs}"
    )

    r = session.get(historia_url, headers=headers)

    if r.status_code != 200 or "Historia Academica" not in r.text:
        st.error("❌ Usuario o contraseña incorrectos")
        return

    st.session_state.session = session
    st.session_state.codigo = codprs
    st.session_state.logged = True
    st.rerun()


# --------------------------------------------------
# PANTALLA 2: HISTORIAL ACADÉMICO
# --------------------------------------------------
def pantalla_historial():
    st.title("📘 Historia académica")

    if st.button("Cerrar sesión"):
        st.session_state.logged = False
        st.session_state.session = None
        st.session_state.codigo = None
        st.rerun()

    session = st.session_state.session
    codigo = st.session_state.codigo

    historia_url = (
        "https://sma.unicartagena.edu.co:8443"
        "/Smaix12/servlet/Adm/DataStudent"
        f"?events=HRYAKD&title_=Historia%20Academica&codbas={codigo}"
    )

    response = session.get(historia_url)
    soup = BeautifulSoup(response.text, "html.parser")
    tablas = soup.find_all("table")

    if len(tablas) < 9:
        st.error("No se encontraron las notas")
        return

    filas = tablas[8].find_all("tr")

    suma = 0.0
    total_creditos = 0

    for fila in filas:
        c = fila.find_all("td")
        if len(c) < 9:
            continue

        materia = c[2].get_text(strip=True)
        codigo_mat = c[1].get_text(strip=True)
        creditos = int(to_float(c[3].get_text(strip=True)))

        # Cortes (pueden o no existir)
        p1 = to_float(c[4].get_text(strip=True))
        p2 = to_float(c[5].get_text(strip=True))
        p3 = to_float(c[6].get_text(strip=True))

        # DEFINITIVA REAL (la verdad)
        def_raw = to_float(c[8].get_text(strip=True))

        # Si existe definitiva, ESA es la nota
        if def_raw > 0:
            final = redondear_nota(def_raw)

            suma += creditos * final
            total_creditos += creditos

            color = (
                "#e74c3c" if final < 2.9 else
                "#f39c12" if final <= 3.5 else
                "#2ecc71"
            )
        else:
            final = None

        components.html(
            f"""
            <div style="
                padding:20px;
                margin-bottom:20px;
                border-radius:16px;
                background:linear-gradient(145deg,#0b1220,#020617);
                color:white;
                max-width:420px;
                font-family:Roboto, sans-serif;
            ">
                <h3 style="margin-bottom:6px;">{materia}</h3>
                <p style="opacity:0.75; margin-bottom:14px;">
                    <b>Código:</b> {codigo_mat} | <b>Créditos:</b> {creditos}
                </p>

                <!-- CORTES -->
                <div style="margin-bottom:16px;">

                    {f'''
                    <div style="display:flex; justify-content:space-between;
                                padding:12px 14px; margin-bottom:8px;
                                border-radius:10px; background:#020617;">
                        <div>
                            <div style="font-size:14px;">Primer corte</div>
                            <div style="font-size:12px; color:#38bdf8;">30%</div>
                        </div>
                        <div style="font-size:22px; font-weight:bold;">{p1}</div>
                    </div>
                    ''' if p1 not in (None, 0) else ""}

                    {f'''
                    <div style="display:flex; justify-content:space-between;
                                padding:12px 14px; margin-bottom:8px;
                                border-radius:10px; background:#020617;">
                        <div>
                            <div style="font-size:14px;">Segundo corte</div>
                            <div style="font-size:12px; color:#38bdf8;">30%</div>
                        </div>
                        <div style="font-size:22px; font-weight:bold;">{p2}</div>
                    </div>
                    ''' if p2 not in (None, 0) else ""}

                    {f'''
                    <div style="display:flex; justify-content:space-between;
                                padding:12px 14px;
                                border-radius:10px; background:#020617;">
                        <div>
                            <div style="font-size:14px;">Examen final</div>
                            <div style="font-size:12px; color:#38bdf8;">40%</div>
                        </div>
                        <div style="font-size:22px; font-weight:bold;">{p3}</div>
                    </div>
                    ''' if p3 not in (None, 0) else ""}

                </div>

                <!-- NOTA FINAL -->
                {f'''
                <div style="
                    background:{color};
                    padding:14px;
                    border-radius:12px;
                    font-size:26px;
                    font-weight:bold;
                    width:190px;
                    text-align:center;
                    color:black;
                ">
                    Final: {final}
                </div>
                ''' if final is not None else '''
                <div style="opacity:0.6; font-style:italic;">
                    Sin notas registradas
                </div>
                '''}

            </div>
            """,
            height=480
        )

    if total_creditos > 0:
        promedio = redondear_nota(suma / total_creditos)
        st.markdown("---")
        st.subheader("📊 Promedio ponderado")
        st.markdown(f"""
        <div style="background:#020617; padding:20px; border-radius:16px;
                    font-size:36px; font-weight:bold; width:220px;
                    text-align:center; color:#38bdf8;">
            {promedio}
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# CONTROLADOR
# --------------------------------------------------
if st.session_state.logged:
    pantalla_historial()
else:
    pantalla_login()
