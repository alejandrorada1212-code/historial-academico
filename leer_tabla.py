
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
    """
    Redondea a 1 decimal.
    Si el segundo decimal >= 6 → sube
    """
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

# Fuente Roboto (GLOBAL, AQUÍ ES DONDE VA)
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

    # Entrar primero
    session.get("https://sma.unicartagena.edu.co:8443/Smaix12/", headers=headers)

    # Login
    payload = {
        "codcia": "UDC",
        "codprs": codprs,
        "pswprs": pswprs,
        "logout": "In"
    }

    login_url = "https://sma.unicartagena.edu.co:8443/Smaix12/servlet/Adm/ValidLogin"
    session.post(login_url, data=payload, headers=headers)

    # Verificar historia académica
    historia_url = (
        "https://sma.unicartagena.edu.co:8443"
        "/Smaix12/servlet/Adm/DataStudent"
        f"?events=HRYAKD&title_=Historia%20Academica&codbas={codprs}"
    )

    r = session.get(historia_url, headers=headers)

    if r.status_code != 200 or "Historia Academica" not in r.text:
        st.error("❌ Usuario o contraseña incorrectos")
        return

    # Guardar sesión
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
    tabla = tablas[8]
    filas = tabla.find_all("tr")

    suma_ponderada = 0.0
    total_creditos = 0

    for fila in filas:
        c = fila.find_all("td")
        if len(c) < 7:
            continue

        materia = c[2].get_text(strip=True)
        codigo_mat = c[1].get_text(strip=True)
        creditos = int(to_float(c[3].get_text(strip=True)))

        p1 = to_float(c[4].get_text(strip=True))
        p2 = to_float(c[5].get_text(strip=True))
        p3 = to_float(c[6].get_text(strip=True))

        nota_final = redondear_nota((0.3 * p1) + (0.3 * p2) + (0.4 * p3))

        suma_ponderada += creditos * nota_final
        total_creditos += creditos

        color = (
            "#e74c3c" if nota_final < 2.9 else
            "#f39c12" if nota_final <= 3.5 else
            "#2ecc71"
        )

        components.html(
            f"""
            <html>
            <head>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

                    * {{
                        font-family: 'Roboto', sans-serif;
                        color: white;
                    }}
                </style>
            </head>
            <body style="margin:0; background:transparent;">

                <div style="
                    padding:18px;
                    margin-bottom:18px;
                    border-radius:14px;
                    background:#0f172a;
                ">

                    <h3 style="margin-bottom:6px;">{materia}</h3>

                    <p style="opacity:0.85; margin-bottom:14px;">
                        <b>Código:</b> {codigo_mat} | <b>Créditos:</b> {creditos}
                    </p>

                    <!-- CORTES -->
                    <div style="max-width:360px;">

                        <div style="
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                            padding:12px;
                            margin-bottom:10px;
                            border-radius:10px;
                            background:#020617;
                        ">
                            <div>
                                <div style="font-size:15px;">Primer corte</div>
                                <div style="font-size:13px; color:#38bdf8;">30%</div>
                            </div>
                            <div style="font-size:22px; font-weight:600;">{p1}</div>
                        </div>

                        <div style="
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                            padding:12px;
                            margin-bottom:10px;
                            border-radius:10px;
                            background:#020617;
                        ">
                            <div>
                                <div style="font-size:15px;">Segundo corte</div>
                                <div style="font-size:13px; color:#38bdf8;">30%</div>
                            </div>
                            <div style="font-size:22px; font-weight:600;">{p2}</div>
                        </div>

                        <div style="
                            display:flex;
                            justify-content:space-between;
                            align-items:center;
                            padding:12px;
                            border-radius:10px;
                            background:#020617;
                        ">
                            <div>
                                <div style="font-size:15px;">Examen final</div>
                                <div style="font-size:13px; color:#38bdf8;">40%</div>
                            </div>
                            <div style="font-size:22px; font-weight:600;">{p3}</div>
                        </div>
                    </div>

                    <!-- NOTA FINAL -->
                    <div style="
                        margin-top:16px;
                        background:{color};
                        padding:14px;
                        border-radius:12px;
                        font-size:26px;
                        font-weight:700;
                        width:180px;
                        text-align:center;
                        color:black;
                    ">
                       Final: {nota_final}
                    </div>

                </div>

            </body>
            </html>
            """,
            height=420,
        )

    if total_creditos > 0:
        promedio = redondear_nota(suma_ponderada / total_creditos)
        st.markdown("---")
        st.subheader("📊 Promedio ponderado")
        st.markdown(f"""
        <div style="background:#020617; padding:20px; border-radius:16px;
                    font-size:36px; font-weight:bold; width:220px; text-align:center;
                    color:#38bdf8;">
            {promedio}
        </div>
        """, unsafe_allow_html=True)


# --------------------------------------------------
# CONTROLADOR PRINCIPAL
# --------------------------------------------------
if st.session_state.logged:
    pantalla_historial()
else:
    pantalla_login()
