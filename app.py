"""
EOS DOCK Report App — Streamlit Cloud
=======================================
App guidata per compilazione EOS DOCK report.
Sezioni: Missing, True Dock Miss, Late Departure, Dock Assets Count.
Traduzione automatica IT→EN per Root Cause.
Genera mailto per apertura diretta in Outlook.
"""

import streamlit as st
from datetime import date
from deep_translator import GoogleTranslator
import urllib.parse

# ─── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="EOS DOCK", page_icon="🚛", layout="wide")

DEFAULT_RECIPIENTS = ["mxp5-dockobam@amazon.com", "mxp5-ob-flow@amazon.com"]

# CPT per turno
CPT_AM = ["10:00", "12:30"]
CPT_PM = ["17:30", "20:30", "21:30"]
CPT_DOMENICA = ["18:15", "19:15"]


# ─── Traduttore ──────────────────────────────────────────────────────────────

def translate_to_english(text: str) -> str:
    """Traduce e riformula testo in inglese professionale."""
    if not text or not text.strip():
        return text
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated if translated else text
    except Exception:
        return text


# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { font-family: 'Segoe UI', sans-serif; }
    .eos-header {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .section-title {
        background-color: #f0f2f6;
        padding: 8px 12px;
        border-radius: 4px;
        border-left: 4px solid #495057;
        font-weight: 600;
        margin: 10px 0;
    }
    .preview-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        white-space: pre-wrap;
    }
    .mailto-btn {
        display: inline-block;
        background-color: #0078d4;
        color: white !important;
        padding: 14px 28px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 15px 0;
    }
    .mailto-btn:hover {
        background-color: #005a9e;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class='eos-header'>
    <h2 style='margin:0;color:white;'>🚛 EOS DOCK Report</h2>
    <p style='margin:5px 0 0 0;opacity:0.8;'>Compilazione guidata — MXP5</p>
</div>
""", unsafe_allow_html=True)

# ─── Data e Turno ────────────────────────────────────────────────────────────
col_date, col_shift, col_name = st.columns(3)

with col_date:
    eos_date = st.date_input("📅 Data", value=date.today(), key="eos_date")

with col_shift:
    is_sunday = eos_date.weekday() == 6
    if is_sunday:
        turno = st.selectbox("⏰ Turno", ["DOMENICA"], key="turno")
        cpt_options = CPT_DOMENICA
    else:
        turno = st.selectbox("⏰ Turno", ["AM", "PM"], key="turno")
        cpt_options = CPT_AM if turno == "AM" else CPT_PM

with col_name:
    sender_name = st.text_input("👤 Il tuo nome", key="sender_name", placeholder="es. Mario Rossi")

st.divider()


# ─── Funzione sezione eventi ─────────────────────────────────────────────────

def render_event_section(section_key: str, section_title: str, icon: str):
    """
    Renderizza una sezione.
    Di default i campi sono APERTI. Spuntando NTR si chiude tutto.
    Ogni evento ha: lista shipment (ID + units), CPT, Lane, Root Cause.
    """
    st.markdown(f"<div class='section-title'>{icon} {section_title}</div>", unsafe_allow_html=True)

    # NTR checkbox — di default NON spuntato (campi visibili)
    ntr = st.checkbox("Nothing to report", value=False, key=f"{section_key}_ntr")

    entries = []

    if not ntr:
        # Gestione numero eventi con bottone +
        count_key = f"{section_key}_count"
        if count_key not in st.session_state:
            st.session_state[count_key] = 1

        for i in range(st.session_state[count_key]):
            with st.expander(f"{section_title} #{i+1}", expanded=True):
                # CPT e Lane
                col1, col2 = st.columns(2)
                with col1:
                    cpt = st.selectbox(
                        "CPT",
                        options=cpt_options,
                        key=f"{section_key}_cpt_{i}"
                    )
                with col2:
                    lane = st.text_input(
                        "Lane",
                        key=f"{section_key}_lane_{i}",
                        placeholder="es. MXP5 -> MXP6"
                    )

                # Shipments
                st.markdown("**Shipments:**")
                num_ship = st.number_input(
                    "Numero shipment",
                    min_value=1, max_value=20, value=1,
                    key=f"{section_key}_numship_{i}"
                )

                shipments = []
                for s in range(num_ship):
                    cs1, cs2 = st.columns([2, 1])
                    with cs1:
                        ship_id = st.text_input(
                            f"Shipment ID #{s+1}",
                            key=f"{section_key}_shipid_{i}_{s}",
                            placeholder="es. VRID o tracking"
                        )
                    with cs2:
                        ship_units = st.number_input(
                            f"Units #{s+1}",
                            min_value=0, value=1,
                            key=f"{section_key}_units_{i}_{s}"
                        )
                    shipments.append({"id": ship_id, "units": ship_units})

                # Root Cause
                rc = st.text_area(
                    "Root Cause (puoi scrivere in italiano)",
                    key=f"{section_key}_rc_{i}",
                    height=68,
                    placeholder="Descrivi la causa..."
                )

                # Totale units
                total_units = sum(sh["units"] for sh in shipments)

                entries.append({
                    "cpt": cpt,
                    "lane": lane,
                    "shipments": shipments,
                    "total_units": total_units,
                    "num_shipments": len(shipments),
                    "rc": rc,
                })

        # Bottone per aggiungere evento
        if st.button(f"➕ Aggiungi {section_title}", key=f"{section_key}_add"):
            st.session_state[count_key] += 1
            st.rerun()

    return ntr, entries


# ═══════════════════════════════════════════════════════════════════════════════
# SEZIONI
# ═══════════════════════════════════════════════════════════════════════════════

# 1. MISSING
missing_ntr, missing_entries = render_event_section("missing", "MISSING", "📦")

# 2. TRUE DOCK MISS
tdm_ntr, tdm_entries = render_event_section("tdm", "TRUE DOCK MISS", "🚛")

# 3. LATE DEPARTURE
ld_ntr, ld_entries = render_event_section("ld", "LATE DEPARTURE", "⚠️")

# 4. DOCK ASSETS COUNT
st.markdown("<div class='section-title'>📊 DOCK ASSETS COUNT</div>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    epal = st.number_input("EPAL", min_value=0, value=0, key="epal")
    epal_tso = st.number_input("EPAL (di cui TSO)", min_value=0, value=0, key="epal_tso")
    epal_yard = st.number_input("EPAL YARD", min_value=0, value=0, key="epal_yard")
with col2:
    light_pallets = st.number_input("Light Pallets", min_value=0, value=0, key="light_pallets")
    jp_carts = st.number_input("JP Carts", min_value=0, value=0, key="jp_carts")


# ═══════════════════════════════════════════════════════════════════════════════
# GENERAZIONE REPORT & MAILTO
# ═══════════════════════════════════════════════════════════════════════════════
st.divider()
st.markdown("### 👁️ Anteprima & Invio")


def build_section_text(title: str, ntr: bool, entries: list, date_str: str) -> str:
    """Costruisce il testo di una sezione."""
    lines = [f"{title}:"]
    if ntr:
        lines.append("Nothing to report")
    else:
        for entry in entries:
            lines.append(
                f"CPT {entry['cpt']} {date_str} | "
                f"Lane: {entry['lane']} | "
                f"Shipments: {entry['num_shipments']} | "
                f"Total Units: {entry['total_units']}"
            )
            # Lista shipment
            for sh in entry["shipments"]:
                if sh["id"]:
                    lines.append(f"  - {sh['id']}: {sh['units']} units")
            # Root Cause tradotta
            rc_translated = translate_to_english(entry['rc'])
            lines.append(f"Root Cause: {rc_translated}")
            lines.append("")
    return "\n".join(lines)


def build_eos_dock():
    """Costruisce il testo EOS DOCK completo."""
    date_str = eos_date.strftime("%d/%m/%Y")
    lines = []

    lines.append(f"EOS DOCK  {date_str}")
    lines.append("")
    lines.append("Hi all,")
    lines.append("Below the daily report:")
    lines.append("")

    # Missing
    lines.append(build_section_text("MISSING", missing_ntr, missing_entries, date_str))
    lines.append("")

    # True Dock Miss
    lines.append(build_section_text("TRUE DOCK MISS", tdm_ntr, tdm_entries, date_str))
    lines.append("")

    # Late Departure
    lines.append(build_section_text("LATE DEPARTURE", ld_ntr, ld_entries, date_str))
    lines.append("")

    # Dock Assets Count
    lines.append("DOCK ASSETS COUNT:")
    lines.append(f"EPAL:              {epal} ( {epal_tso} TSO )")
    lines.append(f"EPAL YARD:         {epal_yard}")
    lines.append(f"Light Pallets:     {light_pallets}")
    lines.append(f"JP Carts:          {jp_carts}")

    return "\n".join(lines)


if st.button("🔄 Genera Anteprima & Email", type="primary", use_container_width=True):
    if not sender_name:
        st.error("⚠️ Inserisci il tuo nome in alto.")
    else:
        with st.spinner("Generazione in corso (traduzione testi)..."):
            preview = build_eos_dock()
        st.session_state.eos_preview = preview

if "eos_preview" in st.session_state and st.session_state.eos_preview:
    st.markdown(f"<div class='preview-box'>{st.session_state.eos_preview}</div>",
               unsafe_allow_html=True)

    st.divider()

    # Costruisci mailto
    date_str = eos_date.strftime("%d/%m/%Y")
    subject = f"EOS DOCK - {date_str}"
    body = st.session_state.eos_preview
    if sender_name:
        body += f"\n\nBest regards,\n{sender_name}"

    to_str = ";".join(DEFAULT_RECIPIENTS)
    mailto_url = (
        f"mailto:{to_str}"
        f"?subject={urllib.parse.quote(subject)}"
        f"&body={urllib.parse.quote(body)}"
    )

    st.markdown(
        f'<a href="{mailto_url}" class="mailto-btn">📧 Apri in Outlook — Premi solo Invia</a>',
        unsafe_allow_html=True
    )
    st.caption("Si apre Outlook con email già compilata. Basta cliccare Invia.")
