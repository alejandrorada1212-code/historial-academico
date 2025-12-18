import streamlit as st
import requests
from bs4 import BeautifulSoup

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(page_title="Historia Académica", layout="wide")

# =========================
# ESTADO DE SESIÓN
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "session" not in st.session_state:
    st.session_state.session = None

if "codigo" not in st.session_state:
    st.session_state.codigo = None

# =========================
# FUNCIÓN LOGIN
# =========================
def login(codigo, password):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-CO,es;q=0.9",
        "Connection": "keep-alive"
    }

    # 1️⃣ Entrar al sistema
    home_url = "https://sma.unicartagena.edu.co:8443/Smaix12/"
    session.get(home_url, headers=headers)

    # 2️⃣ Login
    login_url = "https://sma.unicartagena.edu.co:8443/Smaix12/servlet/Adm/ValidLogin"

    payload = {
        "codcia": "UDC",
        "codprs": codigo,
        "pswprs": password,
        "logout": "In"
    }

    response = session.post(login_url, data=payload, headers=headers, allow_redirects=True)

    # Validación simple (si no redirige a error)
    if response.status_code == 200 and "ValidLogin" not in response.url:
        return session
    else:
        return None

# =========================
# FUNCIÓN HISTORIA ACADÉMICA
# =========================
def obtener_notas(session, codigo):
    historia_url = (
        "https://sma.unicartagena.edu.co:8443"
        "/Smaix12/servlet/Adm/DataStudent"
        f"?events=HRYAKD&title_=Historia%20Academica&codbas={codigo}"
    )

    response = session.get(historia_url)

    soup = BeautifulSoup(response.text, "html.parser")
    tablas = soup.find_all("table")

    tabla_notas = tablas[8]
    filas = tabla_notas.find_all("tr")

    materias = []

    for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) >= 10:
            materias.append({
                "Materia": celdas[2].get_text(strip=True),
                "Código": celdas[1].get_text(strip=True),
                "Créditos": celdas[3].get_text(strip=True),
                "Definitiva": celdas[-2].get_text(strip=True),
                "Final": celdas[-1].get_text(strip=True),
            })

    return materias

# =========================
# LOGIN UI
# =========================
if not st.session_state.logged_in:
    st.title("🔐 Iniciar sesión")

    with st.form("login_form"):
        codigo = st.text_input("Código estudiantil")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Ingresar")

    if submit:
        with st.spinner("Validando credenciales..."):
            session = login(codigo, password)

        if session:
            st.session_state.logged_in = True
            st.session_state.session = session
            st.session_state.codigo = codigo
            st.success("✅ Login correcto")
            st.rerun()
        else:
            st.error("❌ Código o contraseña incorrectos")

# =========================
# HISTORIA ACADÉMICA
# =========================
else:
    st.title("📘 Historia académica")

    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.session = None
        st.session_state.codigo = None
        st.rerun()

    materias = obtener_notas(
        st.session_state.session,
        st.session_state.codigo
    )

    st.subheader("📋 Materias")

    for m in materias:
        with st.container():
            st.markdown(f"### {m['Materia']}")
            col1, col2, col3, col4 = st.columns(4)

            col1.write(f"**Código:** {m['Código']}")
            col2.write(f"**Créditos:** {m['Créditos']}")
            col3.write(f"**Definitiva:** {m['Definitiva']}")
            col4.write(f"**Final:** {m['Final']}")

            st.divider()
