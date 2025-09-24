# SESSA After Sales – sidebar blu Sessa + logo + menu compatto
# Pagina attiva: BOLD + UNDERLINE; inattive: light no underline.
# Header blu più in alto (allineamento col logo), logo nell'header a sinistra del titolo.
# Bottoni: "➕ Aggiungi Richiesta" (sotto RICHIESTE) e "💾 Salva & Genera Modulo" (sotto).

import os, sqlite3, datetime as dt, base64
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
        if LOGO: return Image.open(LOGO)
    except Exception:
        pass
    return "⚓"

def _logo_data_uri():
    if not LOGO: return ""
    try:
        with open(LOGO, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

st.set_page_config(page_title="SESSA After Sales", page_icon=_page_icon(), layout="wide")

# ───────────────────────────── CSS ─────────────────────────────
st.markdown("""
<style>
:root{
  --sessa:#3E79B3; --navy:#0b2a4a; --off:#F6F9FC;
  --sb-logo-top:14px;        /* micro spostamento solo del logo in sidebar */
  --menu-offset:96px;        /* distanza tra logo sidebar e blocco MENU */
  --brand-h:96px;            /* altezza fascia blu header */
  --header-up:-24px;         /* spingi SU il blocco blu: -20/-24/-28… */
}

.stApp, .main .block-container{
  background:var(--off)!important;
  font-family:'Times New Roman', Times, serif!important;
}

/* Riduci padding top del main, poi spingi su solo il blocco blu */
[data-testid="stAppViewContainer"] .main .block-container{ padding-top:0 !important; }

/* ====== SIDEBAR ====== */
aside[aria-label="sidebar"], section[data-testid="stSidebar"]{ background:var(--sessa)!important; }
aside[aria-label="sidebar"] *:not(input):not(textarea):not(select),
section[data-testid="stSidebar"] *:not(input):not(textarea):not(select){ color:#fff!important; }
aside[aria-label="sidebar"] img{ border-radius:12px; }

/* Logo sidebar: resta in alto; micro-tuning con --sb-logo-top */
.sb-brand{ margin-top:var(--sb-logo-top)!important; margin-bottom:12px; }

/* Solo il blocco (MENU + lista) scende rispetto al logo */
.sb-menu-wrap{ margin-top:var(--menu-offset) !important; }

.sb-title{ font-weight:800; color:#fff; margin:0 0 8px 0; letter-spacing:.3px; font-size:20px !important; }

/* MENU compatto */
.sidebar-menu{ display:flex; flex-direction:column; gap:6px; }
.sidebar-menu .nav-item{ margin:0!important; border:0; }

/* Link menu: default light no underline; lo stato attivo è gestito inline */
aside[aria-label="sidebar"] .sidebar-menu a.menu-item,
aside[aria-label="sidebar"] .sidebar-menu a.menu-item:link,
aside[aria-label="sidebar"] .sidebar-menu a.menu-item:visited,
aside[aria-label="sidebar"] .sidebar-menu a.menu-item:hover,
aside[aria-label="sidebar"] .sidebar-menu a.menu-item:active,
section[data-testid="stSidebar"] .sidebar-menu a.menu-item,
section[data-testid="stSidebar"] .sidebar-menu a.menu-item:link,
section[data-testid="stSidebar"] .sidebar-menu a.menu-item:visited,
section[data-testid="stSidebar"] .sidebar-menu a.menu-item:hover,
section[data-testid="stSidebar"] .sidebar-menu a.menu-item:active{
  display:block; padding:6px 8px; border:0; border-radius:0; cursor:pointer;
  color:#fff !important; text-decoration:none !important;
  font-size:0.95rem; line-height:1.15;
}

/* ===== Header brand nel MAIN (logo a piena altezza) ===== */
.brand{
  background:#3E79B3; color:#fff; border-radius:14px;
  height:var(--brand-h);                 /* altezza esatta della fascia */
  margin-top:var(--header-up) !important;
  margin-bottom:18px;
  padding:10px 16px;                        /* niente padding verticale, il logo può arrivare ai bordi */
  display:flex;                          /* mantiene layout in riga */
}
.brand-row{
  display:flex; align-items:center; gap:16px;
  width:100%; height:100%;               /* per consentire al logo l'altezza 100% */
}
.brand-logo{
  height:100%; width:auto;               /* il logo riempie tutta l'altezza della fascia */
  object-fit:contain; display:block; border-radius:10px;
}
.brand h1{ color:#fff!important; margin:0; }
.brand small{ color:#fff!important; opacity:.95; }

/* ====== Card ====== */
.card{ background:#fff; border-radius:14px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,.06); }
.card.no-bg{ background:transparent; box-shadow:none; padding:0; }

/* Campi MAIN bianchi */
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

/* Etichette bianche login */
.s-label{ color:#fff; font-weight:700; margin:8px 0 6px; letter-spacing:.2px; }

/* INPUT LOGIN sidebar */
aside[aria-label="sidebar"] input, aside[aria-label="sidebar"] textarea,
section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] textarea {
  background:#fff!important; color:#111!important; -webkit-text-fill-color:#111!important; caret-color:#111!important;
  border:1px solid #d0d6df!important; border-radius:10px!important; box-shadow:none!important;
}

/* Bottoni nel MAIN */
[data-testid="stAppViewContainer"] .stButton>button{
  background:var(--navy)!important; color:#fff!important; border:0!important; border-radius:10px!important; padding:10px 16px!important;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────── DB ─────────────────────────────
DATA_ROOT = "./data"
DB_PATH   = os.path.join(DATA_ROOT, "db", "aftersales.db")
UPLOADS   = os.path.join(DATA_ROOT, "uploads")
for d in (os.path.dirname(DB_PATH), UPLOADS): os.makedirs(d, exist_ok=True)

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def ensure_schema(conn: sqlite3.Connection):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS wir(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, dealer TEXT, boat TEXT,
        title TEXT, description TEXT, brand TEXT, serial TEXT,
        full_name TEXT, email TEXT, phone TEXT,
        boat_model TEXT, hull_serial TEXT,
        warranty_start TEXT, boat_location TEXT, onboard_contact TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS spr(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, dealer TEXT, boat TEXT,
        description TEXT, item_brand TEXT, item_serial TEXT,
        full_name TEXT, email TEXT, phone TEXT,
        boat_model TEXT, hull_serial TEXT,
        boat_location TEXT, onboard_contact TEXT
    )""")
    conn.commit()

def run_sql(conn, q, p=None):
    cur = conn.cursor()
    cur.execute(q, p or [])
    conn.commit()
    return cur

def df_read(conn, table):
    try: return pd.read_sql_query(f"SELECT * FROM {table} ORDER BY id DESC", conn)
    except Exception: return pd.DataFrame()

# ───────────────────────────── Helpers ─────────────────────────────
def _save_uploaded_files(files, base_dir, prefix):
    """Salva i file caricati e ritorna la lista dei path salvati."""
    saved = []
    if not files: return saved
    os.makedirs(base_dir, exist_ok=True)
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    for i, f in enumerate(files):
        safe_name = f.name.replace("/", "_").replace("\\", "_")
        out_path = os.path.join(base_dir, f"{prefix}_{ts}_{i}_{safe_name}")
        with open(out_path, "wb") as out:
            out.write(f.getbuffer())
        saved.append(out_path)
    return saved

# ───────────────────────────── UI helpers ─────────────────────────────
@contextmanager
def card(cls: str=""):
    st.markdown(f'<div class="card {cls}">', unsafe_allow_html=True)
    try: yield
    finally: st.markdown('</div>', unsafe_allow_html=True)

def header():
    """Header blu con logo a sinistra del testo."""
    logo_uri = _logo_data_uri()
    img_html = f'<img class="brand-logo" src="{logo_uri}" alt="logo"/>' if logo_uri else ""
    st.markdown(f'''
      <div class="brand">
        <div class="brand-row">
          {img_html}
          <div>
            <h1>SESSA AFTER SALES</h1>
            <small>After Sales Dashboard</small>
          </div>
        </div>
      </div>
    ''', unsafe_allow_html=True)

def sidebar_brand():
    st.markdown('<div class="sb-brand">', unsafe_allow_html=True)
    if LOGO: st.image(LOGO, use_container_width=True)
    else:    st.markdown('<h3 style="margin:0;color:#fff">SESSA AFTER SALES</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ───────────────────────────── Login ─────────────────────────────
def require_auth() -> bool:
    """Bypass con ?demo=1. Se APP_USER/APP_PASS assenti → no login (locale)."""
    def _t(x): return str(x).strip().lower() in ("1","true","yes","on")

    demo = _t(os.environ.get("DEMO", "0"))
    try:
        if "DEMO" in st.secrets: demo = demo or _t(st.secrets["DEMO"])
    except Exception: pass
    try:
        demo = demo or _t(st.query_params.get("demo", "0"))
    except Exception:
        try:    demo = demo or _t(st.experimental_get_query_params().get("demo", ["0"])[0])
        except Exception: pass
    if demo:
        st.session_state.auth_ok = True
        st.session_state.auth_user = "demo"
        return True

    USER = PASS = ""
    try:
        if "APP_USER" in st.secrets: USER = str(st.secrets["APP_USER"]).strip()
        if "APP_PASS" in st.secrets: PASS = str(st.secrets["APP_PASS"]).strip()
    except Exception: pass
    USER = os.environ.get("APP_USER", USER).strip()
    PASS = os.environ.get("APP_PASS", PASS).strip()

    if USER == "" and PASS == "":
        st.session_state.auth_ok = True
        st.session_state.auth_user = "dev"
        return True

    if st.session_state.get("auth_ok"): return True

    with st.sidebar:
        sidebar_brand()
        st.markdown("### 🔐 Accesso")
        st.markdown('<div class="s-label">User</div>', unsafe_allow_html=True)
        user = st.text_input("User", placeholder="username", key="login_user", label_visibility="collapsed")
        st.markdown('<div class="s-label">Password</div>', unsafe_allow_html=True)
        pwd  = st.text_input("Password", placeholder="password", type="password", key="login_pass", label_visibility="collapsed")

        if st.button("Entra", use_container_width=True, key="login_btn"):
            if user.strip() == USER and pwd == PASS:
                st.session_state.auth_ok  = True
                st.session_state.auth_user = user.strip() or "guest"
                try: st.rerun()
                except Exception: st.experimental_rerun()
            else:
                st.error("Credenziali errate.")
        st.caption("🔒 Autenticazione: ATTIVA | bypass: ?demo=1")
    return False

# ───────────────────────────── Sezioni ─────────────────────────────
def section_wir(conn):
    # inizializza il numero di richieste dinamiche
    if "wir_nreq" not in st.session_state:
        st.session_state.wir_nreq = 1

    st.subheader("⚓ Warranty Intervention Requests (WIR)")

    # — DATI INTESTAZIONE —
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

    # — RICHIESTE DINAMICHE —
    st.markdown("### RICHIESTE")
    with card():
        for i in range(1, st.session_state.wir_nreq + 1):
            with st.expander(f"Richiesta {i}", expanded=(i == 1)):
                st.text_area("Descrizione *", key=f"wir_desc_{i}")
                st.file_uploader(
                    "Foto (una o più)",
                    type=["png", "jpg", "jpeg"],
                    accept_multiple_files=True,
                    key=f"wir_ph_{i}",
                )
                cc2 = st.columns(2)
                cc2[0].text_input("Marchio", key=f"wir_brand_{i}")
                cc2[1].text_input("Articolo / N. Serie", key=f"wir_item_{i}")

        # bottone sotto al blocco RICHIESTE
        if st.button("➕ Aggiungi Richiesta", key="wir_add"):
            st.session_state.wir_nreq += 1
            st.rerun()

    # — SALVA & GENERA MODULO —
    if st.button("💾 Salva & Genera Modulo", key="wir_save"):
        # Validazione campi obbligatori intestazione
        errors = []
        fullname   = (st.session_state.get("wir_fullname") or "").strip()
        dealer     = (st.session_state.get("wir_dealer") or "").strip()
        email      = (st.session_state.get("wir_email") or "").strip()
        phone      = (st.session_state.get("wir_phone") or "").strip()
        boat_model = (st.session_state.get("wir_boat_model") or "").strip()
        hull       = (st.session_state.get("wir_hull") or "").strip()
        wstart     = st.session_state.get("wir_wstart")

        if not fullname:   errors.append("Nome & Cognome")
        if not dealer:     errors.append("Dealer")
        if not email:      errors.append("E-mail")
        if not phone:      errors.append("Cellulare")
        if not boat_model: errors.append("Modello di barca")
        if not hull:       errors.append("Matricola nr")

        richieste = []
        for i in range(1, st.session_state.wir_nreq + 1):
            desc  = (st.session_state.get(f"wir_desc_{i}") or "").strip()
            brand = (st.session_state.get(f"wir_brand_{i}") or "").strip()
            item  = (st.session_state.get(f"wir_item_{i}") or "").strip()
            ph    = st.session_state.get(f"wir_ph_{i}")  # lista di UploadedFile

            if desc or brand or item or ph:
                if not desc:
                    errors.append(f"Descrizione richiesta {i}")
                richieste.append((i, desc, brand, item, ph))

        if not richieste:
            errors.append("Almeno una richiesta compilata")

        if errors:
            st.error("Compila i campi obbligatori: " + ", ".join(errors))
            st.stop()

        # Salvataggio nel DB: 1 riga per ogni richiesta
        now = dt.datetime.now().isoformat(timespec="seconds")
        saved_count = 0
        for i, desc, brand, item, ph in richieste:
            _save_uploaded_files(ph, UPLOADS, f"wir_{i}")  # salva foto
            run_sql(
                conn,
                """INSERT INTO wir(
                    created_at, dealer, boat, title, description, brand, serial,
                    full_name, email, phone, boat_model, hull_serial,
                    warranty_start, boat_location, onboard_contact
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                [
                    now,
                    dealer, "", f"Richiesta {i}", desc, brand, item,
                    fullname, email, phone, boat_model, hull,
                    str(wstart), (st.session_state.get("wir_loc") or ""),
                    (st.session_state.get("wir_onboard") or "")
                ],
            )
            saved_count += 1

        # Genera un semplice modulo HTML scaricabile
        rows_html = []
        for i, desc, brand, item, _ in richieste:
            rows_html.append(
                f"<tr><td style='padding:6px 8px;border:1px solid #ccc'>{i}</td>"
                f"<td style='padding:6px 8px;border:1px solid #ccc'>{brand or '-'}</td>"
                f"<td style='padding:6px 8px;border:1px solid #ccc'>{item or '-'}</td>"
                f"<td style='padding:6px 8px;border:1px solid #ccc'>{desc}</td></tr>"
            )
        html = f"""
        <html>
        <head><meta charset="utf-8" /><title>Modulo WIR</title></head>
        <body style="font-family:Arial,Helvetica,sans-serif">
          <h2 style="margin:0 0 8px">SESSA – Warranty Intervention Request</h2>
          <div style="margin:0 0 12px;color:#444">{now}</div>
          <h3 style="margin:16px 0 6px">Dati Cliente/Barca</h3>
          <table style="border-collapse:collapse;font-size:14px">
            <tr><td><b>Nome</b></td><td>{fullname}</td></tr>
            <tr><td><b>Dealer</b></td><td>{dealer}</td></tr>
            <tr><td><b>E-mail</b></td><td>{email}</td></tr>
            <tr><td><b>Cellulare</b></td><td>{phone}</td></tr>
            <tr><td><b>Modello barca</b></td><td>{boat_model}</td></tr>
            <tr><td><b>Matricola</b></td><td>{hull}</td></tr>
            <tr><td><b>Data garanzia</b></td><td>{wstart}</td></tr>
            <tr><td><b>Locazione</b></td><td>{st.session_state.get("wir_loc") or ""}</td></tr>
            <tr><td><b>Contatto a bordo</b></td><td>{st.session_state.get("wir_onboard") or ""}</td></tr>
          </table>

          <h3 style="margin:18px 0 6px">Richieste</h3>
          <table style="border-collapse:collapse;font-size:14px">
            <thead>
              <tr>
                <th style="padding:6px 8px;border:1px solid #ccc;text-align:left">#</th>
                <th style="padding:6px 8px;border:1px solid #ccc;text-align:left">Marchio</th>
                <th style="padding:6px 8px;border:1px solid #ccc;text-align:left">Articolo / N. Serie</th>
                <th style="padding:6px 8px;border:1px solid #ccc;text-align:left">Descrizione</th>
              </tr>
            </thead>
            <tbody>
              {''.join(rows_html)}
            </tbody>
          </table>
        </body>
        </html>
        """.encode("utf-8")

        st.success(f"✅ Salvate {saved_count} richieste su database.")
        st.download_button(
            "⬇️ Scarica Modulo WIR (HTML)",
            data=html,
            file_name=f"Modulo_WIR_{dt.date.today().isoformat()}.html",
            mime="text/html",
        )

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
    "WIR": section_wir, "SPR": section_spr, "CLIENTI": section_clienti, "DEALER": section_dealer,
    "DOCUMENTI GARANZIE": section_ddt033, "DOCUMENTI VENDITE": section_ddt006,
    "€ RIPARAZIONI": section_quotes_invoices, "TRASFERTE": section_trips,
    "BARCHE": section_boats, "STORICO PRATICHE": section_storico,
}

def get_current_page():
    keys = list(PAGES.keys())
    current = st.session_state.get("nav")
    try:
        qp = st.query_params
        if not current: current = qp.get("nav", keys[0])
        if isinstance(current, list): current = current[0]
    except Exception:
        try:
            qp = st.experimental_get_query_params()
            if not current: current = qp.get("nav", [keys[0]])[0]
        except Exception:
            current = keys[0]
    if current not in PAGES:
        current = keys[0]
        st.session_state.nav = current
        try: st.query_params.update({"nav": current})
        except Exception: st.experimental_set_query_params(nav=current)
    return current

def render_sidebar_menu(current):
    from urllib.parse import urlencode

    def _qp_dict():
        try: return dict(st.query_params)
        except Exception: return {k: (v[0] if isinstance(v, list) else v) for k,v in st.experimental_get_query_params().items()}

    def _href_for(page:str)->str:
        q = _qp_dict(); q["nav"] = page; return "?" + urlencode(q)

    with st.sidebar:
        sidebar_brand()
        st.markdown('<div class="sb-menu-wrap">', unsafe_allow_html=True)
        st.markdown('<div class="sb-title">MENU</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-menu">', unsafe_allow_html=True)
        for page in PAGES.keys():
            active = (page == current)
            style_active   = "font-weight:800;opacity:1;text-decoration:underline;text-decoration-thickness:3px;text-underline-offset:3px;"
            style_inactive = "font-weight:300;opacity:.70;text-decoration:none;"
            style = style_active if active else style_inactive
            st.markdown(
                f'<div class="nav-item"><a class="menu-item {"active" if active else ""}" href="{_href_for(page)}" target="_self" style="{style}">{page}</a></div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ───────────────────────────── Main ─────────────────────────────
def main():
    if not require_auth():
        st.info("Inserisci credenziali per accedere.")
        st.stop()

    current = get_current_page()
    render_sidebar_menu(current)

    header()
    conn = get_conn()
    try:
        ensure_schema(conn)
        PAGES[current](conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()



