import math
import re
from datetime import date, datetime, timedelta
from html import escape as esc
import uuid

import streamlit as st
import streamlit.components.v1 as components

import json
import gspread
from google.oauth2.service_account import Credentials

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def init_gsheets():
    try:
        credenciales_dict = json.loads(st.secrets["google_sheets_cred"])
        alcance = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciales = Credentials.from_service_account_info(credenciales_dict, scopes=alcance)
        cliente = gspread.authorize(credenciales)
        return cliente.open_by_key("1mfFWfyTRnwBkavxfD_nUDZch1S9bnA8ODmAoXmMnUfo").sheet1
    except Exception as e:
        st.error("Error conectando a la base de datos. Verifica los Secrets.")
        return None

hoja_db = init_gsheets()
# --------------------------------

st.set_page_config(page_title="Sinergia", page_icon="🧭", layout="centered",
                   initial_sidebar_state="collapsed")

TODAY, NOW = date.today(), datetime.now()
META_EFICIENCIA = 85

# ───────────────────────── CSS ─────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=Public+Sans:wght@400;500;600;700&display=swap');
:root{--navy:#0B2545;--blue:#1B5FAA;--sky:#E6EEF8;--bg:#F2F5FA;--ink:#14213D;--mut:#64748B;
--green:#16996B;--gbg:#DDF4EA;--orange:#E8820C;--obg:#FFEBD2;--line:#E3E9F2}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--bg)!important;font-family:'Public Sans',sans-serif;color:var(--ink)}
#MainMenu,header[data-testid="stHeader"],footer,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stElementContainer"]:has(iframe[height="0"]){display:none}
.block-container{max-width:460px!important;padding:max(.8rem,env(safe-area-inset-top)) .8rem 5rem!important}
[data-testid="stVerticalBlock"]{gap:.65rem}
@media(min-width:620px){.stApp{background:radial-gradient(circle at 20% 0%,#16407a,#071a33 70%)!important}
.block-container{background:var(--bg);border-radius:34px;margin:1.4rem auto;min-height:92vh;box-shadow:0 30px 80px rgba(0,0,0,.45)}}
h1,h2,h3,.sn-h{font-family:'Sora',sans-serif!important;letter-spacing:-.02em}

/* barra de marca */
.sn-top{display:flex;align-items:center;gap:.65rem}
.sn-logo{width:38px;height:38px;border-radius:12px;background:linear-gradient(140deg,#1B5FAA,#0B2545);color:#fff;display:grid;place-items:center;font:800 1.15rem 'Sora';box-shadow:0 6px 14px rgba(11,37,69,.3)}
.sn-top b{font:700 1.05rem 'Sora';display:block;line-height:1.1}
.sn-top small{color:var(--mut);font-size:.72rem}
.sn-av{margin-left:auto;width:38px;height:38px;border-radius:50%;background:var(--sky);color:var(--blue);display:grid;place-items:center;font:700 .8rem 'Sora';border:2px solid #fff;box-shadow:0 2px 8px rgba(11,37,69,.15)}

/* selector de rol (radio → control segmentado) */
div[data-testid="stRadio"] [role="radiogroup"]{display:flex;width:100%;gap:0;background:#fff;padding:4px;border-radius:16px;box-shadow:0 4px 14px rgba(11,37,69,.08)}
div[data-testid="stRadio"] label{flex:1;margin:0!important;padding:10px 6px;justify-content:center;border-radius:12px;cursor:pointer;transition:background .2s}
div[data-testid="stRadio"] label>div:first-child{display:none}
div[data-testid="stRadio"] label p{font:700 .88rem 'Sora';margin:0;color:var(--mut)}
div[data-testid="stRadio"] label:has(input:checked){background:var(--navy);box-shadow:0 6px 14px rgba(11,37,69,.3)}
div[data-testid="stRadio"] label:has(input:checked) p{color:#fff}

/* tabs */
[data-baseweb="tab-list"]{gap:2px;overflow-x:auto}
button[data-baseweb="tab"]{padding:.6rem .7rem;height:auto;flex:1}
button[data-baseweb="tab"] p{font:700 .82rem 'Sora';color:var(--mut)}
button[data-baseweb="tab"][aria-selected="true"] p{color:var(--navy)}
[data-baseweb="tab-highlight"]{background:var(--navy)!important;height:3px;border-radius:3px}
[data-baseweb="tab-border"]{background:var(--line)!important}

/* hero */
.sn-hero{background:linear-gradient(145deg,#0B2545 0%,#13407c 100%);color:#fff;border-radius:26px;padding:1.15rem 1.1rem;box-shadow:0 16px 34px rgba(11,37,69,.32);position:relative;overflow:hidden}
.sn-hero:after{content:"";position:absolute;right:-50px;top:-50px;width:170px;height:170px;border-radius:50%;background:rgba(255,255,255,.06)}
.sn-hero h2{font:700 1.3rem 'Sora';margin:0;color:#fff;padding:0}
.sn-hero p{margin:.25rem 0 0;font-size:.84rem;color:#BFD0E8;line-height:1.35}
.sn-cnt{display:flex;gap:.5rem;margin-top:.9rem;position:relative;z-index:1}
.sn-cnt div{flex:1;background:rgba(255,255,255,.1);border-radius:14px;padding:.55rem .6rem}
.sn-cnt b{font:800 1.4rem 'Sora';display:block;line-height:1}
.sn-cnt span{font-size:.7rem;color:#BFD0E8}
.sn-cnt .w b{color:#FFB661}
.sn-gauge{display:flex;align-items:center;gap:.9rem;position:relative;z-index:1}
.sn-gauge svg{flex:none;overflow:visible}
.sn-gauge circle.f{animation:sn-draw 1.2s cubic-bezier(.2,.8,.2,1)}
@keyframes sn-draw{from{stroke-dashoffset:var(--c)}}
.sn-dn{font:800 27px 'Sora';fill:#fff}.sn-ds{font:500 9.5px 'Public Sans';fill:#BFD0E8}
.sn-streak b{font:800 2.5rem 'Sora';line-height:1;color:#fff}
.sn-streak small{display:block;font-size:.76rem;color:#BFD0E8;margin:.15rem 0 .55rem}
.sn-wk{display:flex;gap:4px}
.sn-wk i{width:11px;height:11px;border-radius:4px;background:#3DDC97}
.sn-wk i.x{background:#FFB661}.sn-wk i.cur{outline:2px solid #fff;outline-offset:1px}
.sn-wk i.risk{background:transparent;border:2px dashed #FFB661}
.sn-meta{margin-top:.85rem;font-size:.76rem;color:#BFD0E8;position:relative;z-index:1}
.sn-meta b{color:#fff}

/* KPIs */
.sn-kpis{display:flex;gap:.55rem}
.sn-kpi{flex:1;background:#fff;border-radius:18px;padding:.7rem .75rem;box-shadow:0 4px 14px rgba(11,37,69,.07)}
.sn-kpi b{font:800 1.5rem 'Sora';display:block;line-height:1.1}
.sn-kpi span{font-size:.7rem;color:var(--mut)}
.sn-kpi.o b{color:var(--orange)}.sn-kpi.g b{color:var(--green)}.sn-kpi.b b{color:var(--blue)}

/* tarjetas de tarea */
div[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:0!important;border-radius:22px!important;box-shadow:0 6px 20px rgba(11,37,69,.09);padding:.2rem .15rem}
.sn-row{display:flex;justify-content:space-between;align-items:center;gap:.5rem}
.sn-cat{font-size:.74rem;color:var(--mut);font-weight:600;display:flex;align-items:center;gap:.4rem}
.sn-pd{width:8px;height:8px;border-radius:50%;background:#9AA9BD}.sn-pd.Alta{background:var(--orange)}.sn-pd.Media{background:var(--blue)}
.sn-title{font:600 .98rem/1.3 'Sora';margin:.45rem 0 .2rem;color:var(--ink)}
.sn-sub{font-size:.76rem;color:var(--mut)}
.sn-pill{font-size:.7rem;font-weight:700;padding:.22rem .6rem;border-radius:99px;white-space:nowrap}
.sn-pill.o{background:var(--obg);color:#B35F00}.sn-pill.g{background:var(--gbg);color:#0E7A53}.sn-pill.b{background:var(--sky);color:var(--blue)}
.sn-stepper{display:flex;margin:.85rem 0 .3rem}
.sn-st{flex:1;text-align:center;position:relative;font-size:.63rem;color:#9AA9BD;font-weight:600}
.sn-st i{display:block;width:11px;height:11px;border-radius:50%;background:#D5DEEA;margin:0 auto .3rem;position:relative;z-index:1}
.sn-st+.sn-st:before{content:"";position:absolute;top:4px;left:-50%;width:100%;height:3px;background:#D5DEEA;border-radius:3px}
.sn-st.done{color:var(--navy)}.sn-st.done i,.sn-st.done:before{background:var(--navy)!important}
.sn-st.now{color:var(--blue)}.sn-st.now i{background:#fff;border:3px solid var(--blue);width:13px;height:13px;margin-top:-1px}
.sn-st.now:before{background:var(--navy)!important}
.sn-st.ok{color:var(--green)}.sn-st.ok i,.sn-st.ok:before{background:var(--green)!important}
.sn-note{border-radius:12px;padding:.5rem .65rem;font-size:.76rem;line-height:1.35;margin-top:.5rem}
.sn-note.o{background:var(--obg);color:#8A4A00}.sn-note.b{background:var(--sky);color:#164A85}
.sn-ev{border:1.5px dashed #BCCBE0;border-radius:14px;padding:.55rem .7rem;margin-top:.6rem;font-size:.78rem;background:#F8FAFD}
.sn-ev a{color:var(--blue);font-weight:700;text-decoration:none;word-break:break-all}
.sn-ev small{display:block;color:var(--mut);margin-top:.25rem;font-size:.68rem}
.sn-box{background:#fff;border-radius:22px;padding:.4rem .9rem;box-shadow:0 6px 20px rgba(11,37,69,.09)}
.sn-li{display:flex;justify-content:space-between;align-items:center;gap:.6rem;padding:.7rem 0;border-bottom:1px solid var(--line);font-size:.82rem;font-weight:500}
.sn-li:last-child{border:0}
.sn-sec{font:700 .9rem 'Sora';margin:.5rem 0 0}
.sn-empty{text-align:center;padding:2rem 1rem;color:var(--mut);font-size:.85rem}
.sn-empty b{display:block;font:700 1rem 'Sora';color:var(--navy);margin-bottom:.2rem}
.sn-dlg-t{font:600 .95rem 'Sora'}.sn-dlg-s{font-size:.78rem;color:var(--mut);margin:.2rem 0 .4rem}

/* botones */
.stButton>button,.stFormSubmitButton>button{width:100%;min-height:48px;border-radius:14px;font:700 .9rem 'Sora';border:1.5px solid #D5DEEA;background:#fff;color:var(--navy);transition:transform .08s}
.stButton>button:active,.stFormSubmitButton>button:active{transform:scale(.97)}
button[kind^="primary"],button[data-testid^="stBaseButton-primary"]{background:linear-gradient(135deg,#0B2E5C,#1B5FAA)!important;color:#fff!important;border:0!important;box-shadow:0 8px 18px rgba(11,46,92,.28)}
[class*="st-key-ap_"] button{background:linear-gradient(135deg,#128A60,#22B07D)!important;box-shadow:0 8px 18px rgba(18,138,96,.3)!important}
[class*="st-key-dev_"] button{color:#B35F00;border-color:#F3C58D}
[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.5rem}
[data-testid="stColumn"],[data-testid="column"]{min-width:0!important;flex:1 1 0!important;width:auto!important}
input,textarea{font-size:16px!important}
div[data-baseweb="input"],div[data-baseweb="textarea"],div[data-baseweb="select"]>div{border-radius:12px!important}
div[role="dialog"]{border-radius:26px!important}
[data-testid="stForm"]{border:0;background:#fff;border-radius:22px;padding:1rem;box-shadow:0 6px 20px rgba(11,37,69,.09)}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# Metas PWA
components.html("""<script>
const d=window.parent.document,h=d.head;
[["theme-color","#0B2545"],["apple-mobile-web-app-capable","yes"],["mobile-web-app-capable","yes"],
["apple-mobile-web-app-status-bar-style","black-translucent"],
["viewport","width=device-width,initial-scale=1,viewport-fit=cover"]].forEach(([n,c])=>{
let m=h.querySelector('meta[name="'+n+'"]');if(!m){m=d.createElement('meta');m.name=n;h.appendChild(m)}m.content=c});
</script>""", height=0)

def md(html: str):
    """Renderiza HTML sin que Markdown lo interprete como bloque de código."""
    st.markdown(re.sub(r"\n\s*", "", html), unsafe_allow_html=True)

# ───────────────────────── LÓGICA DE BASE DE DATOS ─────────────────────────
@st.cache_data(ttl=5) # Refresca datos cada 5 seg de Google Sheets para no saturar la API
def obtener_datos_db():
    if hoja_db is None: return []
    try:
        registros = hoja_db.get_all_records()
    except:
        return []
    
    parsed = []
    for r in registros:
        # Formatear la fecha límite
        try: 
            fecha_lim = datetime.strptime(str(r["due"]), "%Y-%m-%d").date()
        except: 
            fecha_lim = TODAY
            
        # Función para castear fechas con hora
        def cast_dt(val):
            if not val: return None
            try: return datetime.strptime(str(val), "%Y-%m-%d %H:%M")
            except: return None
            
        parsed.append({
            "id": str(r["id"]),
            "title": str(r["title"]),
            "cat": str(r["cat"]),
            "prio": str(r["prio"]),
            "due": fecha_lim,
            "status": str(r["status"]) or "pendiente",
            "submitted_at": cast_dt(r.get("submitted_at")),
            "closed_at": cast_dt(r.get("closed_at")),
            "link": str(r.get("link", "")),
            "note": str(r.get("note", "")),
            "jefe_msg": str(r.get("jefe_msg", ""))
        })
    return parsed

def agregar_bd(titulo, cat, prio, due):
    new_id = str(uuid.uuid4())[:8]
    try:
        hoja_db.append_row([new_id, titulo, cat, prio, due.strftime("%Y-%m-%d"), "pendiente", "", "", "", "", ""])
        obtener_datos_db.clear() # Fuerza a recargar la tabla nueva
    except Exception as e:
        st.error(f"Error guardando: {e}")

def actualizar_bd(tid, updates):
    try:
        registros = hoja_db.get_all_records()
        row_idx = next((i + 2 for i, r in enumerate(registros) if str(r["id"]) == str(tid)), None)
        if not row_idx: return
        
        # Mapeo de columnas exactas de Google Sheets
        col_map = {"status": 6, "submitted_at": 7, "closed_at": 8, "link": 9, "note": 10, "jefe_msg": 11}
        for k, v in updates.items():
            if k in col_map:
                hoja_db.update_cell(row_idx, col_map[k], v)
        obtener_datos_db.clear()
    except Exception as e:
        st.error(f"Error actualizando: {e}")


# --- INICIALIZACIÓN ---
if "weeks" not in st.session_state:
    st.session_state.weeks = [True] # Racha para la UI

S = st.session_state
tasks = obtener_datos_db()

by = lambda s: [t for t in tasks if t["status"] == s]
get = lambda i: next(t for t in tasks if t["id"] == i)
days_left = lambda t: (t["due"] - TODAY).days
on_time = lambda t: t["submitted_at"].date() <= t["due"]

def eficiencia():
    sub = [t for t in tasks if t["submitted_at"]]
    return round(100 * sum(on_time(t) for t in sub) / len(sub)) if sub else 100

def racha():
    pendientes = by("pendiente")
    cur_ok = True
    if pendientes:
        cur_ok = not any(days_left(t) < 0 for t in pendientes)
    n = 0
    for w in reversed(S.weeks):
        if not w: break
        n += 1
    return n + (1 if cur_ok else 0), cur_ok

# ───────────────────────── Componentes HTML ─────────────────────────
def due_pill(t):
    d = days_left(t)
    if d < 0: return f'<span class="sn-pill o">Vencido hace {-d} d</span>'
    if d <= 1: return f'<span class="sn-pill o">{"Vence hoy" if d == 0 else "Vence mañana"}</span>'
    return f'<span class="sn-pill b">Vence en {d} días</span>'

def stepper(status):
    step = {"pendiente": 1, "revision": 2, "cerrado": 4}[status]
    out = ""
    for i, l in enumerate(["Asignado", "Pendiente", "En revisión", "Aprobado"]):
        cls = ("ok" if status == "cerrado" else "done") if i < step else ("now" if i == step else "")
        out += f'<div class="sn-st {cls}"><i></i>{l}</div>'
    return f'<div class="sn-stepper">{out}</div>'

def evidence(t):
    if not (t["link"] or t["note"]): return ""
    link = f'<a href="{esc(t["link"])}" target="_blank" rel="noopener">Abrir evidencia</a>' if t["link"] else ""
    note = f'<div style="margin-top:.2rem">{esc(t["note"])}</div>' if t["note"] else ""
    stamp = t["submitted_at"].strftime("%d/%m/%Y %H:%M") if t["submitted_at"] else ""
    return f'<div class="sn-ev">{link}{note}<small>Registrado el {stamp}. Respaldo para ambas partes.</small></div>'

def card(t, boss=False):
    s = t["status"]
    if s == "pendiente":
        pill = due_pill(t)
    else:
        pill = '<span class="sn-pill g">A tiempo</span>' if on_time(t) else '<span class="sn-pill o">Con retraso</span>'
    
    extra = ""
    if s == "pendiente" and t["jefe_msg"]:
        extra = f'<div class="sn-note o"><b>Jefatura devolvió:</b> {esc(t["jefe_msg"])} El reloj sigue corriendo.</div>'
    if s == "revision" and not boss:
        extra = '<div class="sn-note b">Reloj detenido. Jefatura está revisando tu evidencia.</div>'
        
    sub = f'Compromiso al {t["due"].strftime("%d/%m")}'
    if boss: sub = f'Dickson Medina. {sub}'
    
    md(f"""<div class="sn-row"><span class="sn-cat"><i class="sn-pd {t['prio']}"></i>{esc(t['cat'])}</span>{pill}</div>
    <div class="sn-title">{esc(t['title'])}</div><div class="sn-sub">{sub}</div>
    {stepper(s)}{extra}{evidence(t) if s != 'pendiente' else ''}""")

def empty(title, text):
    md(f'<div class="sn-empty"><b>{title}</b>{text}</div>')

def donut(pct):
    r = 46
    c = 2 * math.pi * r
    col = "#3DDC97" if pct >= META_EFICIENCIA else "#FFB661"
    return (f'<svg viewBox="0 0 120 120" width="118" height="118"><circle cx="60" cy="60" r="{r}" fill="none" '
            f'stroke="rgba(255,255,255,.15)" stroke-width="12"/><circle class="f" cx="60" cy="60" r="{r}" fill="none" '
            f'stroke="{col}" stroke-width="12" stroke-linecap="round" stroke-dasharray="{c:.1f}" '
            f'stroke-dashoffset="{c * (1 - pct / 100):.1f}" style="--c:{c:.1f}" transform="rotate(-90 60 60)"/>'
            f'<text x="60" y="63" text-anchor="middle" class="sn-dn">{pct}%</text>'
            f'<text x="60" y="80" text-anchor="middle" class="sn-ds">oportuna</text></svg>')

# ───────────────────────── Diálogos ─────────────────────────
_dialog = getattr(st, "dialog", None) or getattr(st, "experimental_dialog")

@_dialog("Cumplir compromiso")
def dlg_cumplir(tid):
    t = get(tid)
    md(f'<div class="sn-dlg-t">{esc(t["title"])}</div>'
       '<div class="sn-dlg-s">Al enviar, el reloj se detiene y Jefatura recibe tu evidencia con sello de fecha y hora.</div>')
    link = st.text_input("Enlace de evidencia (SharePoint o Drive)", placeholder="https://...", key=f"lnk_{tid}")
    note = st.text_area("Nota breve", max_chars=280, height=90, key=f"nt_{tid}", placeholder="Qué se hizo, hallazgos o pendientes.")
    
    if st.button("Enviar a revisión", type="primary", key=f"send_{tid}"):
        link, note = link.strip(), note.strip()
        if not link and not note:
            st.error("Adjunta un enlace o escribe una nota breve.")
        elif link and not link.lower().startswith(("http://", "https://")):
            st.error("El enlace debe comenzar con https://")
        else:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            actualizar_bd(tid, {"status": "revision", "link": link, "note": note, "submitted_at": now_str, "jefe_msg": ""})
            S.toast = ("Enviado a revisión. El reloj quedó detenido.", "📨")
            st.rerun()

@_dialog("Devolver al funcionario")
def dlg_devolver(tid):
    t = get(tid)
    md(f'<div class="sn-dlg-t">{esc(t["title"])}</div>'
       '<div class="sn-dlg-s">El compromiso vuelve a Pendiente y el reloj se reanuda.</div>')
    msg = st.text_area("¿Qué debe corregir?", max_chars=240, height=100, key=f"msg_{tid}")
    
    if st.button("Devolver con comentario", type="primary", key=f"devok_{tid}"):
        if not msg.strip():
            st.error("Indica qué debe corregirse.")
        else:
            actualizar_bd(tid, {"status": "pendiente", "jefe_msg": msg.strip(), "submitted_at": "", "link": "", "note": ""})
            S.toast = ("Devuelto al funcionario con tu comentario.", "↩️")
            st.rerun()

# ───────────────────────── Vistas ─────────────────────────
def vista_funcionario():
    pend = sorted(by("pendiente"), key=lambda t: t["due"])
    rev, cer = by("revision"), by("cerrado")
    venc = sum(days_left(t) < 0 for t in pend)
    pronto = sum(0 <= days_left(t) <= 3 for t in pend)
    msg = (f"Tienes <b>{venc}</b> vencido y <b>{pronto}</b> por vencer esta semana." if venc or pronto else "Estás al día. Buen trabajo.")
    
    md(f"""<div class="sn-hero"><h2>Hola, Dickson</h2><p>{msg}</p>
    <div class="sn-cnt"><div class="{'w' if venc else ''}"><b>{len(pend)}</b><span>Por cumplir</span></div>
    <div><b>{len(rev)}</b><span>En revisión</span></div><div><b>{len(cer)}</b><span>Cerrados</span></div></div></div>""")

    t1, t2, t3 = st.tabs([f"Por cumplir ({len(pend)})", f"En revisión ({len(rev)})", f"Cerrados ({len(cer)})"])
    with t1:
        if not pend: empty("Sin pendientes", "Todo está en revisión o cerrado.")
        for t in pend:
            with st.container(border=True):
                card(t)
                if st.button("Cumplir", type="primary", key=f"cum_{t['id']}"):
                    dlg_cumplir(t["id"])
    with t2:
        if not rev: empty("Nada en revisión", "Cuando reportes un cumplimiento aparecerá aquí.")
        for t in sorted(rev, key=lambda t: t["submitted_at"], reverse=True):
            with st.container(border=True):
                card(t)
    with t3:
        if not cer: empty("Aún sin cierres", "Los compromisos aprobados se archivan aquí.")
        for t in sorted(cer, key=lambda t: t["closed_at"], reverse=True):
            with st.container(border=True):
                card(t)

def vista_jefatura():
    pct = eficiencia()
    n, cur_ok = racha()
    dots = "".join(f'<i class="{"" if w else "x"}"></i>' for w in S.weeks)
    dots += f'<i class="cur {"" if cur_ok else "risk"}"></i>'
    gap = pct - META_EFICIENCIA
    meta = (f"Superas la meta de {META_EFICIENCIA}% por <b>{gap} pts</b>" if gap >= 0 else f"Faltan <b>{-gap} pts</b> para la meta de {META_EFICIENCIA}%")
    riesgo = "" if cur_ok else " La semana actual está en riesgo por un compromiso vencido."
    
    md(f"""<div class="sn-hero"><div class="sn-gauge">{donut(pct)}
    <div class="sn-streak"><b>{n} 🔥</b><small>semanas en racha</small><div class="sn-wk">{dots}</div></div></div>
    <div class="sn-meta">Eficiencia oportuna de Dickson Medina. {meta}.{riesgo}</div></div>""")

    rev, pend, cer = by("revision"), by("pendiente"), by("cerrado")
    venc = sum(days_left(t) < 0 for t in pend)
    
    md(f"""<div class="sn-kpis"><div class="sn-kpi b"><b>{len(rev)}</b><span>Por validar</span></div>
    <div class="sn-kpi o"><b>{venc}</b><span>Vencidos</span></div>
    <div class="sn-kpi g"><b>{len(cer)}</b><span>Aprobados</span></div></div>""")

    t1, t2, t3 = st.tabs([f"Por validar ({len(rev)})", "Seguimiento", "Asignar"])
    with t1:
        if not rev: empty("Bandeja vacía", "No hay evidencia pendiente de tu validación.")
        for t in sorted(rev, key=lambda t: t["submitted_at"]):
            with st.container(border=True):
                card(t, boss=True)
                c1, c2 = st.columns(2)
                if c1.button("Devolver", key=f"dev_{t['id']}"):
                    dlg_devolver(t["id"])
                if c2.button("Aprobar", type="primary", key=f"ap_{t['id']}"):
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                    actualizar_bd(t["id"], {"status": "cerrado", "closed_at": now_str})
                    S.toast = ("Compromiso aprobado y cerrado.", "✅")
                    st.rerun()
    with t2:
        md('<div class="sn-sec">En la cancha del funcionario</div>')
        rows = "".join(f'<div class="sn-li"><span>{esc(t["title"])}</span>{due_pill(t)}</div>' for t in sorted(pend, key=lambda t: t["due"]))
        md(f'<div class="sn-box">{rows or "<div class=sn-empty>Sin pendientes.</div>"}</div>')
        
        md('<div class="sn-sec">Cerrados recientemente</div>')
        rows = "".join(f'<div class="sn-li"><span>{esc(t["title"])}</span>'
                       f'<span class="sn-pill {"g" if on_time(t) else "o"}">{"A tiempo" if on_time(t) else "Tarde"}</span></div>'
                       for t in sorted(cer, key=lambda t: t["closed_at"], reverse=True))
        md(f'<div class="sn-box">{rows or "<div class=sn-empty>No hay cerrados aún.</div>"}</div>')
    with t3:
        with st.form("nuevo", clear_on_submit=True):
            titulo = st.text_input("Compromiso", placeholder="Ej: Informe de cierre, Constructora Pacífico")
            
            # Usando las 7 categorías exactas que pediste antes
            cat = st.selectbox("Categoría", [
                "Fiscalización", "Administrativas", "Gestión Documental", 
                "Compromisos personales", "Acciones de Control", "Función Liquidadora", "Otros"
            ])
            prio = st.selectbox("Prioridad", ["Alta", "Media", "Baja"], index=1)
            due = st.date_input("Fecha comprometida", value=TODAY + timedelta(days=7), min_value=TODAY)
            
            if st.form_submit_button("Asignar compromiso", type="primary"):
                if not titulo.strip():
                    st.error("Escribe el compromiso.")
                else:
                    agregar_bd(titulo.strip(), cat, prio, due)
                    S.toast = ("Compromiso asignado a Dickson.", "📌")
                    st.rerun()

# ───────────────────────── App ─────────────────────────
if S.get("toast"):
    msg, icon = S.pop("toast")
    st.toast(msg, icon=icon)

md('<div class="sn-top"><div class="sn-logo">S</div><div><b>Sinergia</b><small>Fiscalización Intensiva</small></div>'
   '<div class="sn-av">DM</div></div>')
rol = st.radio("Vista", ["Vista Funcionario", "Vista Jefatura"], horizontal=True,
               label_visibility="collapsed", key="rol")
vista_funcionario() if rol == "Vista Funcionario" else vista_jefatura()
