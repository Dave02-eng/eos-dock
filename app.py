"""
EOS Report App — Streamlit Cloud
==================================
App guidata per compilazione EOS (End of Shift) report.
3 template: DOCK, TSO, TSO-ITK1.
Traduzione automatica IT→EN integrata.
Genera link mailto per aprire Outlook con email pre-compilata.
"""

import streamlit as st
from datetime import date
from deep_translator import GoogleTranslator
import urllib.parse

# ─── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(page_title="EOS Report", page_icon="📝", layout="wide")

# Destinatari email
DEFAULT_RECIPIENTS = ["mxp5-dockobam@amazon.com", "mxp5-ob-flow@amazon.com"]


# ─── Traduttore ──────────────────────────────────────────────────────────────

def translate_to_english(text: str) -> str:
    """Traduce testo italiano in inglese. Se già inglese o vuoto, ritorna così."""
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
        padding: 12px 24px;
        border-radius: 6px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        margin: 10px 0;
    }
    .mailto-btn:hover {
        background-color: #005a9e;
        color: white !important;
    }
    .copy-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 6px;
        padding: 12px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ──────────────────────────────────────────────────────
if "failed_exsd_entries" not in st.session_state:
    st.session_state.failed_exsd_entries = []
if "true_dock_miss_entries" not in st.session_state:
    st.session_state.true_dock_miss_entries = []


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class='eos-header'>
    <h2 style='margin:0;color:white;'>📝 EOS Report Generator</h2>
    <p style='margin:5px 0 0 0;opacity:0.8;'>Compilazione guidata End of Shift Report — MXP5</p>
</div>
""", unsafe_allow_html=True)


# ─── Selezione Tipo EOS ─────────────────────────────────────────────────────
col_type, col_date = st.columns([2, 1])

with col_type:
    eos_type = st.selectbox(
        "📋 Tipo EOS",
        ["DOCK", "TSO", "TSO-ITK1"],
        key="eos_type_select"
    )

with col_date:
    eos_date = st.date_input("📅 Data", value=date.today(), key="eos_date")

st.divider()

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab_form, tab_translate, tab_preview = st.tabs(
    ["📝 Compila EOS", "🌐 Traduttore", "👁️ Anteprima & Invio"]
)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — COMPILAZIONE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_form:

    # ─── SEZIONE MISSING ─────────────────────────────────────────────────
    st.markdown("<div class='section-title'>📦 MISSING</div>", unsafe_allow_html=True)
    missing_ntr = st.checkbox("Nothing to report", value=True, key="missing_ntr")
    if not missing_ntr:
        missing_text = st.text_area(
            "Dettagli Missing (puoi scrivere in italiano)",
            key="missing_text",
            height=100,
            placeholder="Descrivi i missing..."
        )
    else:
        missing_text = "Nothing to report"

    # ─── SEZIONE TRUE DOCK MISS ──────────────────────────────────────────
    st.markdown("<div class='section-title'>🚛 TRUE DOCK MISS</div>", unsafe_allow_html=True)
    tdm_ntr = st.checkbox("Nothing to report", value=True, key="tdm_ntr")

    if not tdm_ntr:
        st.markdown("**Aggiungi True Dock Miss:**")
        num_tdm = st.number_input("Quanti True Dock Miss?", min_value=1, max_value=10, value=1, key="num_tdm")

        tdm_entries = []
        for i in range(num_tdm):
            with st.expander(f"True Dock Miss #{i+1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    tdm_cpt = st.text_input("CPT", key=f"tdm_cpt_{i}", placeholder="es. 20:30")
                    tdm_lane = st.text_input("Lane", key=f"tdm_lane_{i}", placeholder="es. ITK1 -> MXP6")
                with col2:
                    tdm_vrid = st.text_input("VRID", key=f"tdm_vrid_{i}", placeholder="es. 115463NH3")
                    tdm_root_cause = st.text_area(
                        "Root Cause (puoi scrivere in italiano)",
                        key=f"tdm_cause_{i}",
                        height=68,
                        placeholder="Causa del miss..."
                    )
                tdm_entries.append({
                    "cpt": tdm_cpt,
                    "lane": tdm_lane,
                    "vrid": tdm_vrid,
                    "root_cause": tdm_root_cause
                })
        st.session_state.true_dock_miss_entries = tdm_entries
    else:
        st.session_state.true_dock_miss_entries = []

    # ─── SEZIONE SPECIFICA PER TIPO ──────────────────────────────────────

    # === DOCK ===
    if eos_type == "DOCK":
        st.markdown("<div class='section-title'>📊 DOCK ASSETS COUNT</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            epal_dock = st.number_input("EPAL", min_value=0, value=0, key="epal_dock")
            epal_tso = st.number_input("EPAL (di cui TSO)", min_value=0, value=0, key="epal_tso")
            epal_yard = st.number_input("EPAL YARD", min_value=0, value=0, key="epal_yard")
        with col2:
            light_pallets = st.number_input("Light Pallets", min_value=0, value=0, key="light_pallets")
            jp_carts = st.number_input("JP Carts", min_value=0, value=0, key="jp_carts")

    # === TSO ===
    elif eos_type == "TSO":
        st.markdown("<div class='section-title'>📊 CONTA FINE TURNO</div>", unsafe_allow_html=True)
        epal_buffer_tso = st.number_input("EPAL - Buffer TSO", min_value=0, value=0, key="epal_buffer_tso")

        st.markdown("<div class='section-title'>📦 BUFFER PER DESTINAZIONE</div>", unsafe_allow_html=True)
        st.caption("Aggiungi le destinazioni e i carrelli buffer accumulati")

        num_buffer = st.number_input("Numero destinazioni", min_value=1, max_value=20, value=1, key="num_buffer_tso")
        buffer_rows_tso = []
        for i in range(num_buffer):
            col1, col2 = st.columns([2, 1])
            with col1:
                dest = st.text_input(f"Destinazione {i+1}", key=f"buf_dest_tso_{i}", placeholder="es. MXP6")
            with col2:
                carts = st.number_input(f"Carrelli {i+1}", min_value=0, value=0, key=f"buf_carts_tso_{i}")
            buffer_rows_tso.append({"destination": dest, "carts": carts})

    # === TSO-ITK1 ===
    elif eos_type == "TSO-ITK1":
        # Failed ExSD
        st.markdown("<div class='section-title'>⚠️ FAILED ExSD - LATE DEPARTURE</div>", unsafe_allow_html=True)
        has_failed = st.checkbox("Ci sono Failed ExSD?", value=False, key="has_failed_exsd")

        failed_entries = []
        if has_failed:
            num_failed = st.number_input("Quanti Failed ExSD?", min_value=1, max_value=10, value=1, key="num_failed")

            for i in range(num_failed):
                with st.expander(f"Failed ExSD #{i+1}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        f_lane = st.text_input("Lane", key=f"fexsd_lane_{i}", placeholder="es. MXP5 -> MXP6")
                        f_cause = st.text_area(
                            "Cause (puoi scrivere in italiano)",
                            key=f"fexsd_cause_{i}",
                            height=68,
                            placeholder="Descrivi la causa del ritardo..."
                        )
                    with col2:
                        f_vrid = st.text_input("VRID", key=f"fexsd_vrid_{i}", placeholder="es. 11379Y772")
                        f_carrier = st.text_input("Carrier", key=f"fexsd_carrier_{i}", placeholder="es. ACRIX")

                    col3, col4 = st.columns(2)
                    with col3:
                        f_load_start = st.text_input("Loading started", key=f"fexsd_ls_{i}", placeholder="es. Aug 6, 2026 7:02:44 PM")
                        f_planned_dep = st.text_input("Planned departure", key=f"fexsd_pd_{i}", placeholder="es. Aug 6, 2026 18:55:00 PM")
                    with col4:
                        f_load_finish = st.text_input("Loading finish", key=f"fexsd_lf_{i}", placeholder="es. Aug 6, 2026 7:39:42 PM")
                        f_actual_dep = st.text_input("Actual departure", key=f"fexsd_ad_{i}", placeholder="es. Aug 6, 2026 8:03:50 PM")

                    f_cx_impact = st.selectbox("CX Impact", ["No", "Yes"], key=f"fexsd_cx_{i}")

                    failed_entries.append({
                        "date": eos_date.strftime("%d/%m/%Y"),
                        "lane": f_lane,
                        "cause": f_cause,
                        "vrid": f_vrid,
                        "carrier": f_carrier,
                        "cx_impact": f_cx_impact,
                        "load_start": f_load_start,
                        "load_finish": f_load_finish,
                        "planned_dep": f_planned_dep,
                        "actual_dep": f_actual_dep,
                    })

        st.session_state.failed_exsd_entries = failed_entries

        # Buffer per destinazione
        st.markdown("<div class='section-title'>📦 BUFFER PER DESTINAZIONE</div>", unsafe_allow_html=True)
        st.caption("Carrelli dock ancora da pallettizzare per cella/destinazione")

        num_buffer_itk = st.number_input("Numero destinazioni", min_value=1, max_value=20, value=2, key="num_buffer_itk")
        buffer_rows_itk = []
        for i in range(num_buffer_itk):
            col1, col2 = st.columns([2, 1])
            with col1:
                dest = st.text_input(
                    f"Cella/Destinazione {i+1}",
                    key=f"buf_dest_itk_{i}",
                    placeholder="es. Cella B, Cella G, MXP6..."
                )
            with col2:
                carts = st.number_input(f"Carrelli {i+1}", min_value=0, value=0, key=f"buf_carts_itk_{i}")
            buffer_rows_itk.append({"destination": dest, "carts": carts})

        # EPAL
        st.markdown("<div class='section-title'>📊 EPAL COUNT</div>", unsafe_allow_html=True)
        epal_itk = st.number_input("EPAL", min_value=0, value=0, key="epal_itk")

    # ─── Note aggiuntive ─────────────────────────────────────────────────
    st.markdown("<div class='section-title'>📝 NOTE AGGIUNTIVE</div>", unsafe_allow_html=True)
    additional_notes = st.text_area(
        "Note extra (puoi scrivere in italiano, verranno tradotte)",
        key="additional_notes",
        height=100,
        placeholder="Eventuali note aggiuntive..."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — TRADUTTORE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_translate:
    st.markdown("### 🌐 Traduttore Italiano → Inglese")
    st.markdown("Scrivi un testo in italiano e verrà tradotto automaticamente in inglese corretto.")

    input_text = st.text_area(
        "Testo in italiano",
        height=150,
        key="translate_input",
        placeholder="Scrivi qui il testo da tradurre..."
    )

    if st.button("🔄 Traduci", type="primary"):
        if input_text.strip():
            with st.spinner("Traduzione in corso..."):
                translated = translate_to_english(input_text)
            st.markdown("**Traduzione:**")
            st.code(translated, language=None)
            st.caption("Puoi copiare il testo tradotto e incollarlo nei campi del form.")
        else:
            st.warning("Inserisci un testo da tradurre.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANTEPRIMA & INVIO
# ═══════════════════════════════════════════════════════════════════════════════
with tab_preview:
    st.markdown("### 👁️ Anteprima & Invio EOS")

    # Nome clerk
    sender_name = st.text_input("Il tuo nome", key="sender_name", placeholder="es. Mario Rossi")

    st.divider()

    def build_eos_text():
        """Costruisce il testo EOS completo, traducendo i campi liberi."""
        lines = []
        date_str = eos_date.strftime("%d/%m/%Y")

        lines.append(f"EOS {eos_type} - {date_str}")
        lines.append("")

        # MISSING
        lines.append("MISSING:")
        if missing_ntr:
            lines.append("Nothing to report")
        else:
            lines.append(translate_to_english(missing_text))
        lines.append("")

        # TRUE DOCK MISS
        lines.append("TRUE DOCK MISS:")
        if tdm_ntr:
            lines.append("Nothing to report")
        else:
            for entry in st.session_state.true_dock_miss_entries:
                lines.append(f"CPT {entry['cpt']} {date_str}")
                lines.append(f"Lane: {entry['lane']}")
                lines.append(f"VRID: {entry['vrid']}")
                lines.append(f"Root Cause: {translate_to_english(entry['root_cause'])}")
                lines.append("")
        lines.append("")

        # Sezione specifica
        if eos_type == "DOCK":
            lines.append("DOCK ASSETS COUNT:")
            lines.append(f"EPAL:              {epal_dock} ( {epal_tso} TSO )")
            lines.append(f"EPAL YARD:         {epal_yard}")
            lines.append(f"Light Pallets:     {light_pallets}")
            lines.append(f"JP Carts:          {jp_carts}")

        elif eos_type == "TSO":
            lines.append("Conta fine turno:")
            lines.append(f"EPAL - Buffer TSO:  {epal_buffer_tso}")
            lines.append("")
            if buffer_rows_tso:
                lines.append("Buffer per destinazione:")
                for row in buffer_rows_tso:
                    if row["destination"]:
                        lines.append(f"  {row['destination']}: {row['carts']} carrelli")

        elif eos_type == "TSO-ITK1":
            # Failed ExSD
            if st.session_state.failed_exsd_entries:
                lines.append("Failed ExSD - Late Departure")
                for entry in st.session_state.failed_exsd_entries:
                    lines.append(f"{entry['date']} Lane {entry['lane']}")
                    lines.append(f"Cause: {translate_to_english(entry['cause'])}")
                    lines.append(f"VRID:  {entry['vrid']}")
                    lines.append(f"CARRIER: {entry['carrier']}")
                    lines.append(f"Loading started: {entry['load_start']}")
                    lines.append(f"Loading finish: {entry['load_finish']}")
                    lines.append(f"Planned departure:  {entry['planned_dep']}")
                    lines.append(f"Actual departure: {entry['actual_dep']}")
                    lines.append(f"CX Impact: {entry['cx_impact']}")
                    lines.append("")
            else:
                lines.append("Failed ExSD - Late Departure")
                lines.append("Nothing to report")
                lines.append("")

            # Buffer
            if buffer_rows_itk:
                has_data = any(r["destination"] for r in buffer_rows_itk)
                if has_data:
                    for row in buffer_rows_itk:
                        if row["destination"]:
                            lines.append(f"Numero carrelli dock {row['destination']} ancora da pallettizzare: {row['carts']}")
                    lines.append("")

            lines.append(f"EPAL:   {epal_itk}")

        # Note aggiuntive
        if additional_notes and additional_notes.strip():
            lines.append("")
            lines.append("Additional Notes:")
            lines.append(translate_to_english(additional_notes))

        return "\n".join(lines)

    if st.button("🔄 Genera Anteprima", type="primary"):
        with st.spinner("Generazione in corso (traduzione testi)..."):
            preview_text = build_eos_text()
        st.session_state.eos_preview = preview_text

    if "eos_preview" in st.session_state and st.session_state.eos_preview:
        st.markdown("**Anteprima email:**")
        st.markdown(f"<div class='preview-box'>{st.session_state.eos_preview}</div>",
                   unsafe_allow_html=True)

        st.divider()

        # ─── Bottone "Apri in Outlook" (mailto link) ─────────────────────
        date_str = eos_date.strftime("%d/%m/%Y")
        subject = f"EOS {eos_type} - {date_str}"
        body = f"Hi all,\n\nBelow the daily report:\n\n{st.session_state.eos_preview}"
        if sender_name:
            body += f"\n\nBest regards,\n{sender_name}"

        # Costruisci mailto
        to_str = ";".join(DEFAULT_RECIPIENTS)
        mailto_url = (
            f"mailto:{to_str}"
            f"?subject={urllib.parse.quote(subject)}"
            f"&body={urllib.parse.quote(body)}"
        )

        st.markdown("**📧 Apri email in Outlook:**")
        st.markdown(
            f'<a href="{mailto_url}" class="mailto-btn">📧 Apri in Outlook</a>',
            unsafe_allow_html=True
        )
        st.caption("Cliccando si apre Outlook con destinatari, oggetto e testo già compilati. Controlla e premi Invia.")

        st.divider()

        # ─── Alternativa: Copia testo ────────────────────────────────────
        st.markdown("**📋 Oppure copia il testo manualmente:**")
        st.code(body, language=None)
        st.caption(f"Destinatari: {'; '.join(DEFAULT_RECIPIENTS)}")
        st.caption(f"Oggetto: {subject}")

    else:
        st.info("👆 Compila il form nella prima tab, poi clicca 'Genera Anteprima' per vedere il report e inviarlo.")
