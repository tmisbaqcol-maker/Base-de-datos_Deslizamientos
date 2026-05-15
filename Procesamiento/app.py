import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="Ladera Occidental – Sectores",
    page_icon="🗺️",
    initial_sidebar_state="collapsed",
)

# ── Estilos CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Ocultar menú hamburguesa y footer de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Título principal de cada slide */
    .sector-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
        color: #1a3c5e;
        letter-spacing: 0.02em;
    }
    .sector-counter {
        text-align: center;
        color: #888;
        font-size: 0.95rem;
        margin-top: 2px;
        margin-bottom: 0;
    }
    .divider-line {
        border: none;
        border-top: 2px solid #d0d8e4;
        margin: 12px 0 18px 0;
    }
    /* Subtítulos de sección */
    .section-label {
        font-size: 1.05rem;
        font-weight: 600;
        color: #2c5f8a;
        margin-bottom: 4px;
        border-left: 4px solid #2c5f8a;
        padding-left: 8px;
    }
    /* Botones de navegación */
    div[data-testid="column"] button {
        width: 100%;
        height: 46px;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos: escanear carpetas ────────────────────────────────────────
BASE = Path(__file__).parent

EXCLUIDOS = {"__pycache__", ".git", ".streamlit", "node_modules"}


def hallar_archivos(carpeta: Path, patrones: list[str]) -> list[Path]:
    """Devuelve lista de archivos que coincidan con algún patrón glob."""
    resultado = set()
    for p in patrones:
        resultado.update(carpeta.glob(p))
    return sorted(resultado)


sectores = []
for carpeta in sorted(BASE.iterdir()):
    if not carpeta.is_dir() or carpeta.name in EXCLUIDOS:
        continue

    html_files   = hallar_archivos(carpeta, ["*.html"])
    informe_files = hallar_archivos(carpeta, ["informe_final*.png"])
    cut_files    = hallar_archivos(carpeta, ["*cut*.png", "*cut2*.png"])

    if html_files or informe_files or cut_files:
        sectores.append({
            "nombre":   carpeta.name,
            "html":     html_files,
            "informe":  informe_files,
            "corte":    cut_files,
        })

if not sectores:
    st.error("⚠️ No se encontraron sectores con contenido en esta carpeta.")
    st.stop()

# ── Estado de sesión ─────────────────────────────────────────────────────────
if "idx" not in st.session_state:
    st.session_state.idx = 0

idx = st.session_state.idx
sector = sectores[idx]

# ── Barra de progreso ────────────────────────────────────────────────────────
st.progress((idx + 1) / len(sectores))

# ── Cabecera + navegación ────────────────────────────────────────────────────
col_prev, col_titulo, col_next = st.columns([1, 6, 1])

with col_prev:
    st.write("")  # espaciado vertical
    if st.button("◀  Anterior", use_container_width=True,
                 disabled=(idx == 0)):
        st.session_state.idx -= 1
        st.rerun()

with col_titulo:
    st.markdown(
        f"<p class='sector-title'>{sector['nombre']}</p>"
        f"<p class='sector-counter'>Sector {idx + 1} de {len(sectores)}</p>",
        unsafe_allow_html=True,
    )

with col_next:
    st.write("")
    if st.button("Siguiente  ▶", use_container_width=True,
                 disabled=(idx == len(sectores) - 1)):
        st.session_state.idx += 1
        st.rerun()

st.markdown("<hr class='divider-line'>", unsafe_allow_html=True)

# ── Vista 3D ─────────────────────────────────────────────────────────────────
if sector["html"]:
    st.markdown("<p class='section-label'>🌐 Vista 3D Interactiva</p>",
                unsafe_allow_html=True)

    if len(sector["html"]) == 1:
        html_content = sector["html"][0].read_text(encoding="utf-8", errors="ignore")
        components.html(html_content, height=530, scrolling=False)
    else:
        # Varios archivos HTML → pestañas internas
        nombres_tabs = [f.stem.replace("_", " ").title() for f in sector["html"]]
        tabs = st.tabs(nombres_tabs)
        for tab, html_path in zip(tabs, sector["html"]):
            with tab:
                html_content = html_path.read_text(encoding="utf-8", errors="ignore")
                components.html(html_content, height=530, scrolling=False)

    st.write("")

# ── Informe final + Corte del terreno (en dos columnas) ──────────────────────
tiene_informe = bool(sector["informe"])
tiene_corte   = bool(sector["corte"])

if tiene_informe or tiene_corte:
    col_inf, col_corte = st.columns(2)

    with col_inf:
        if tiene_informe:
            st.markdown("<p class='section-label'>📋 Informe Final</p>",
                        unsafe_allow_html=True)
            for img in sector["informe"]:
                st.image(str(img), use_container_width=True)

    with col_corte:
        if tiene_corte:
            st.markdown("<p class='section-label'>⛰️ Corte del Terreno</p>",
                        unsafe_allow_html=True)
            for img in sector["corte"]:
                st.image(str(img), use_container_width=True)
        else:
            st.info("No hay imagen de corte disponible para este sector.")

# ── Sidebar: índice de sectores ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🗺️ Sectores")
    for i, s in enumerate(sectores):
        etiqueta = f"{'▶ ' if i == idx else ''}{s['nombre']}"
        if st.button(etiqueta, key=f"sidebar_{i}", use_container_width=True):
            st.session_state.idx = i
            st.rerun()
