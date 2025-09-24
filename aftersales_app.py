# SESSA After Sales – layout finale (sidebar blu + menu compatto + input bianchi + login sicuro)
import os, sqlite3, datetime as dt
import pandas as pd
import streamlit as st
from PIL import Image
from contextlib import contextmanager

# ───────────────────────────── Page config ─────────────────────────────

def _find_logo():
    for p in [os.path.join("./data", "logo.png"), "./logo.png"]:
        if os.path.exists(p):
            return p
    return None

LOGO = _find_logo()


def _page_icon():
    try:
        if LOGO:
            return Image.open(LOGO)
    except Exception:
        pass
    return "⚓"


st.set_page_config(page_title="SESSA After Sales", page_icon=_page_icon(), layout="wide")

# ───────────────────────────── CSS ─────────────────────────────
st.markdown(
    """
<style>
:root{ --sessa:#3E79B3; --navy:#0b2a4a; --off:#F6F9FC; }
.stApp, .main .block-container{ background:var(--off)!important; font-family:'Times New Roman', Times, serif!important; }

/* --- SIDEBAR --- */
aside[aria-label="sidebar"], section[data-testid="stSidebar"]{ background:var(--sessa)!important; }
aside[aria-label="sidebar"] *:not(input):not(textarea):not(select),
section[data-testid="stSidebar"] *:not(input):not(textarea):not(select){ color:#fff!important; }  /* testi bianchi, NON gli input */
aside[aria-label="sidebar"] img{ border-radius:12px; }

/* Etichette bianche per login (non toccano gli input) */
.s-label{ color:#fff; font-weight:700; margin:8px 0 6px; letter-spacing:.2px; }

/* INPUT LOGIN in sidebar: sempre testo nero su bianco + autofill */
aside[aria-label="sidebar"] input, aside[aria-label="sidebar"] textarea,
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea,
div[data-testid="stSidebar"] input, div[data-testid="stSidebar"] textarea{
  background:#fff!important; color:#111!important; -webkit-text-fill-color:#111!important; caret-color:#111!important;
  border:1px solid #d0d6df!important; border-radius:10px!important; box-shadow:none!important;
}
aside[aria-label="sidebar"] input::placeholder,
section[data-testid="stSidebar"] input::placeholder,
div[data-testid="stSidebar"] input::placeholder{ color:#6B7280!important; opacity:1!important; }
aside[aria-label="sidebar"] input:-webkit-autofill,
section[data-testid="stSidebar"] input:-webkit-autofill,
div[data-testid="stSidebar"] input:-webkit-autofill{
  -webkit-text-fill-color:#111!important;
  -webkit-box-shadow:0 0 0 1000px #fff inset!important;
          box-shadow:inset 0 0 0 1000px #fff!important;
}

/* Bottone ENTRA (solo login) */
.login-btn .stButton>button{
  width:100%; background:var(--navy)!important; color:#fff!important; border:0!important; border-radius:10px!important; padding:10px 16px!important;
}

/* MENU in sidebar: compatto, niente sfondo, underline bianca sulla pagina attiva */
.sidebar-menu .nav-item{ margin:2px 0; }                                      /* spazi ridotti */
.sidebar-menu .stButton>button{
  width:100%; text-align:left; background:transparent!important; color:#fff!important; border:none!important;
  padding:4px 8px!important; margin:0!important; border-radius:8px!important; font-weight:700!important;
}
.sidebar-menu .stButton>button:hover{ background:rgba(255,255,255,.12)!important; }
.sidebar-menu .nav-item{ border-bottom:3px solid transparent; }
.sidebar-menu .nav-item.active{ border-bottom:3px solid #fff; }               /* underline pagina attiva */

/* Bottoni d'azione NEL MAIN (non toccare quelli della sidebar) */
[data-testid="stAppViewContainer"] .stButton>button{
  background:var(--navy)!important; color:#fff!important; border:0!important; border-radius:10px!important; padding:10px 16px!important;
}

/* Header card */
.brand{ background:#3E79B3; color:#fff; border-radius:14px; padding:14px 16px; margin-bottom:18px; }
.brand h1{ color:#fff!important; margin:0; }
.brand small{ color:#fff!important; opacity:.95; }

/* Card */
.card{ background:#fff; border-radius:14px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,.06); }
.card.no-bg{ background:transparent; box-shadow:none; padding:0; }

/* Campi nel MAIN: sempre bianchi */
[data-testid="stAppViewContainer"] .stTextInput input,
[data-testid="stAppViewContainer"] .stTextArea textarea,
[data-testid="stAppViewContainer"] .stNumberInput input,
[data-testid="stAppViewContainer"] .stDateInput input,
[data-testid="stAppViewContainer"] [data-baseweb="select"]>div,
[data-testid="stAppViewContainer"] [data-baseweb="input"]{
  background:#ffffff!important; color:#111!important; -webkit-text-fill-color:#111!important; caret-color:#111!important;
  border:1px solid #d0d6df!important; border-radius:10px!important; box-shadow:none!important;
}

/* Divider invisibili */
hr, .stDivider, div[role="separator"], *[data-testid="stHorizontalRule"]{ display:none!important; height:0!important; }
</style>
""",
    unsafe_allow_html=True,
)

# ───────────────────────────── DB ─────────────────────────────
DATA_ROOT = "./data"
DB_PATH = os.path.join(DATA_ROOT, "db", "aftersales.db")
UPLOADS = os.path.join(DATA_ROOT, "uploads")
for d in (os.path.dirname(DB_PATH), UPLOADS):
    os.makedirs(d, exist_ok=True)


def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def ensure_schema(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS wir(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, dealer TEXT, boat TEXT,
        title TEXT, description TEXT, brand TEXT, serial TEXT,
        full_name TEXT, email TEXT, phone TEXT,
        boat_model TEXT, hull_serial TEXT,
        warranty_start TEXT, boat_location TEXT, onboard_contact TEXT
    )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS spr(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, dealer TEXT, boat TEXT,
        description TEXT, item_brand TEXT, item_serial TEXT,
        full_name TEXT, email TEXT, phone TEXT,
        boat_model TEXT, hull_serial TEXT,
        boat_location TEXT, onboard_contact TEXT
    )"""
    )
    conn.commit()


def df_read(conn, table):
    try:
        return pd.read_sql_query(f"SELECT * FROM {table} ORDER BY id DESC", conn)
    except Exception:
        return pd.DataFrame()


# ───────────────────────────── UI helpers ─────────────────────────────
@contextmanager
def card(cls: str = ""):
    st.markdown(f'<div class="card {cls}">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


def header():
    st.markdown(
        '<div class="brand"><h1>SESSA AFTER SALES</h1><small>After Sales Dashboard</small></div>',
        unsafe_allow_html=True,
    )


# ───────────────────────────── Login ─────────────────────────────

def require_auth() -> bool:
    """
    Login robusto (Cloud + locale).
    - Bypass immediato se nella URL c'è ?demo=1 (o DEMO=1 in secrets/env).
    - Se non esistono credenziali in secrets/env -> login disabilitato (si entra sempre).
    - Se esistono credenziali -> serve user/password.
    """

    def _truthy(x):
        return str(x).strip().lower() in ("1", "true", "yes", "on")

    # --- 1) BYPASS DEMO ---
    demo = _truthy(os.environ.get("DEMO", "0"))
    try:
        if "DEMO" in st.secrets:
            demo = demo or _truthy(st.secrets["DEMO"])
    except Exception:
        pass
    # querystring ?demo=1
    try:
        demo = demo or _truthy(st.query_params.get("demo", "0"))
    except Exception:
        try:
            demo = demo or _truthy(st.experimental_get_query_params().get("demo", ["0"])[0])
        except Exception:
            pass

    if demo:
        st.session_state.auth_ok = True
        st.session_state.auth_user = "demo"
        return True  # entra SUBITO, senza UI

    # --- 2) LEGGI CREDENZIALI ---
    USER = PASS = ""
    try:
        if "APP_USER" in st.secrets:
            USER = str(st.secrets["APP_USER"]).strip()
        if "APP_PASS" in st.secrets:
            PASS = str(st.secrets["APP_PASS"]).strip()
    except Exception:
        pass
    USER = os.environ.get("APP_USER", USER).strip()
    PASS = os.environ.get("APP_PASS", PASS).strip()

    auth_disabled = USER == "" and PASS == ""

    # Se non ci sono credenziali, niente login: entra direttamente
    if auth_disabled:
        st.session_state.auth_ok = True
        st.session_state.auth_user = "dev"
        return True

    # già autenticato?
    if st.session_state.get("auth_ok"):
        return True

    # --- 3) UI LOGIN (sidebar) ---
    with st.sidebar:
        if LOGO:
            st.image(LOGO, use_container_width=True)
        st.markdown("### 🔐 Accesso")
        st.markdown('<div class="s-label">User</div>', unsafe_allow_html=True)
        user = st.text_input(
            "User", placeholder="username", key="login_user", label_visibility="collapsed"
        )
        st.markdown('<div class="s-label">Password</div>', unsafe_allow_html=True)
        pwd = st.text_input(
            "Password", placeholder="password", type="password", key="login_pass", label_visibility="collapsed"
        )

        st.markdown('<div class="login-btn">', unsafe_allow_html=True)
        if st.button("Entra", use_container_width=True):
            ok = user.strip() == USER and pwd == PASS
            if ok:
                st.session_state.auth_ok = True
                st.session_state.auth_user = user.strip() or "guest"
                try:
                    st.rerun()
                except Exception:
                    st.experimental_rerun()
            else:
                st.error("Credenziali errate.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Indicatore chiaro (ti dice cosa vede la Cloud)
        st.caption("🔒 Autenticazione: ATTIVA | bypass demo: aggiungi ?demo=1 alla URL")

    return False


# ───────────────────────────── Sezioni ─────────────────────────────

def section_wir(conn):
    st.subheader("⚓ Warranty Intervention Requests (WIR)")
    st.markdown("### DATI")
    with card():
        c = st.columns(4)
        c[0].date_input("Data", dt.date.today(), key="wir_date")
        c[1].text_input("Nome & Cognome *", key="wir_fullname")
        c[2].text_input("Dealer *", key="wir_dealer")
        c[3].text_input("E-mail *", key="wir_email")
        c2 = st.columns(4)
        c2[0].text_input("Cellulare *", key="wir_phone")
        c2[1].text_input("Modello di barca *", key="wir_boat_model")
        c2[2].text_input("Matricola nr *", key="wir_hull")
        c2[3].date_input("Data attivazione garanzia *", dt.date.today(), key="wir_wstart")
        c3 = st.columns(2)
        c3[0].text_input("Locazione barca", key="wir_loc")
        c3[1].text_input("Contatto a bordo", key="wir_onboard")

    st.markdown("### RICHIESTE")
    with card():
        with st.expander("Richiesta 1", expanded=True):
            st.text_area("Descrizione *", key="wir_desc_1")
            st.file_uploader(
                "Foto (una o più)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="wir_ph_1"
            )
            cc2 = st.columns(2)
            cc2[0].text_input("Marchio", key="wir_brand_1")
            cc2[1].text_input("Articolo / N. Serie", key="wir_item_1")


def section_spr(conn):
    st.subheader("🛠️ Spare Parts Request (SPR)")
    st.markdown("### DATI")
    with card():
        c = st.columns(4)
        c[0].date_input("Data", dt.date.today(), key="spr_date")
        c[1].text_input("Nome & Cognome *", key="spr_fullname")
        c[2].text_input("Dealer *", key="spr_dealer")
        c[3].text_input("E-mail *", key="spr_email")
        c2 = st.columns(4)
        c2[0].text_input("Cellulare *", key="spr_phone")
        c2[1].text_input("Modello di barca *", key="spr_boat_model")
        c2[2].text_input("Matricola nr *", key="spr_hull")
        c2[3].empty()
        c3 = st.columns(2)
        c3[0].text_input("Locazione barca", key="spr_loc")
        c3[1].text_input("Contatto a bordo", key="spr_onboard")


def section_clienti(conn):
    st.subheader("CLIENTI")
    with card():
        st.write("Anagrafica Clienti.")


def section_dealer(conn):
    st.subheader("DEALER")
    with card():
        st.write("Anagrafica Dealer.")


def section_ddt033(conn):
    st.subheader("DOCUMENTI GARANZIE")
    with card():
        st.write("Documenti Garanzie.")


def section_ddt006(conn):
    st.subheader("DOCUMENTI VENDITE")
    with card():
        st.write("Documenti Vendite.")


def section_quotes_invoices(conn):
    st.subheader("€ RIPARAZIONI")
    with card():
        st.write("Preventivi / Fatture.")


def section_trips(conn):
    st.subheader("TRASFERTE")
    with card():
        st.write("Trasferte.")


def section_boats(conn):
    st.subheader("BARCHE")
    with card():
        st.write("Archivio barche.")


def section_storico(conn):
    st.subheader("STORICO PRATICHE")
    dfw, dfs = df_read(conn, "wir"), df_read(conn, "spr")
    if (dfw is None or dfw.empty) and (dfs is None or dfs.empty):
        with card():
            st.info("Ancora nessuna pratica presente.")
            return
    if dfw is not None and not dfw.empty:
        st.markdown("### WIR")
        with card():
            st.dataframe(dfw, use_container_width=True)
    if dfs is not None and not dfs.empty:
        st.markdown("### SPR")
        with card():
            st.dataframe(dfs, use_container_width=True)


# ───────────────────────────── Routing ─────────────────────────────
PAGES = {
    "WIR": section_wir,
    "SPR": section_spr,
    "CLIENTI": section_clienti,
    "DEALER": section_dealer,
    "DOCUMENTI GARANZIE": section_ddt033,
    "DOCUMENTI VENDITE": section_ddt006,
    "€ RIPARAZIONI": section_quotes_invoices,
    "TRASFERTE": section_trips,
    "BARCHE": section_boats,
    "STORICO PRATICHE": section_storico,
}


def get_current_page():
    keys = list(PAGES.keys())
    current = st.session_state.get("nav")
    try:
        qp = st.query_params
        if not current:
            current = qp.get("nav", keys[0])
        if isinstance(current, list):
            current = current[0]
    except Exception:
        try:
            qp = st.experimental_get_query_params()
            if not current:
                current = qp.get("nav", [keys[0]])[0]
        except Exception:
            current = keys[0]
    if current not in PAGES:
        current = keys[0]
        st.session_state.nav = current
        try:
            st.query_params.update({"nav": current})
        except Exception:
            st.experimental_set_query_params(nav=current)
    return current


def main():
    # LOGIN
    if not require_auth():
        st.info("Inserisci credenziali per accedere.")
        st.stop()

    current = get_current_page()

    # MENU in sidebar (wrapper per lo stile)
    with st.sidebar:
        st.markdown("### MENU")
        st.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
        for page in PAGES.keys():
            css = "nav-item active" if page == current else "nav-item"
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(page, key=f"nav_{page}"):
                st.session_state.nav = page
                try:
                    st.query_params.update({"nav": page})
                except Exception:
                    st.experimental_set_query_params(nav=page)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # HEADER + CONTENUTO
    header()
    conn = get_conn()
    try:
        ensure_schema(conn)
        PAGES[current](conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

