import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Studio Manager", layout="centered")

# --- PASSWORD ---
password_segreta = "studio2024"

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    st.markdown("### 🔒 Accesso Riservato")
    pwd = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if pwd == password_segreta:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Password errata")
    return False

if not check_password():
    st.stop()

# --- MEMORIA DATI ---
if "pazienti" not in st.session_state:
    st.session_state.pazienti = []

# --- LISTINO PREZZI ---
TRATTAMENTI = {
    "Vacuum Therapy (20 min)": 80.0,
    "Radiofrequenza Viso": 120.0,
    "Linfodrenaggio Manuale": 70.0,
    "Laser Epilazione (Gambe)": 150.0,
    "Pacchetto Dimagrimento Urto": 90.0,
    "Pulizia Viso Profonda": 60.0
}

# --- MENU PRINCIPALE ---
st.markdown("### 🏥 Studio Medico & Estetico")
scelta = st.radio("Menu:", ["📝 NUOVA SCHEDA", "📂 ARCHIVIO GIORNALIERO"], horizontal=True)
st.divider()

# ==========================================
# SEZIONE 1: VENDITA / SCHEDA
# ==========================================
if scelta == "📝 NUOVA SCHEDA":

    # --- STEP 1: ANAGRAFICA ---
    st.markdown("#### 1. Anagrafica Paziente")
    col1, col2 = st.columns(2)
    with col1:
        nome_paziente = st.text_input("Nome e Cognome")
    with col2:
        trattamento_oggi = st.text_input("Trattamento fatto OGGI", placeholder="Es. Igiene")

    st.markdown("---")

    # --- STEP 2: PROTOCOLLO ---
    st.markdown("#### 2. Configurazione Protocollo")
    
    # Selezione del trattamento
    trattamento_scelto = st.selectbox("Seleziona Trattamento da proporre:", list(TRATTAMENTI.keys()))
    prezzo_singolo = TRATTAMENTI[trattamento_scelto]
    
    # Definizione Sedute
    col_a, col_b = st.columns(2)
    with col_a:
        # Modificato come richiesto (Via "Consiglio Medico")
        n_ideali = st.number_input("Sedute IDEALI (Protocollo):", value=8, min_value=1)
    with col_b:
        n_vendute = st.number_input("Sedute PROPOSTE:", value=6, min_value=1)

    # --- BARRA MIGLIORATA E ACCATTIVANTE ---
    st.write("") # Spazio vuoto
    efficacia = min(int((n_vendute / n_ideali) * 100), 100)
    
    # Visualizzazione barra
    st.progress(efficacia)
    
    # Messaggio dinamico sotto la barra
    if efficacia < 50:
        st.error(f"🔴 Copertura Protocollo: {efficacia}% - Efficacia Insufficiente")
    elif efficacia < 100:
        st.warning(f"🟠 Copertura Protocollo: {efficacia}% - Risultato Parziale (Mantenimento ridotto)")
    else:
        st.success(f"🟢 Copertura Protocollo: {efficacia}% - Risultato Massimizzato (Top)")

    st.markdown("---")

    # --- STEP 3: ECONOMICO ---
    st.markdown("#### 3. Proposta Economica")
    
    # Calcolo automatico
    prezzo_totale = prezzo_singolo * n_vendute
    
    # Checkbox per attivare la modalità sconto
    usa_sconto = st.checkbox("Applica Sconto Paziente (€)")
    
    if usa_sconto:
        sconto_euro = st.number_input("Sconto da applicare (€):", value=50.0, step=10.0)
        prezzo_finale = prezzo_totale - sconto_euro
        
        # Visualizzazione Prezzi
        st.write(f"Prezzo Listino: <strike style='color:red'>€ {prezzo_totale:.2f}</strike>", unsafe_allow_html=True)
        st.markdown(f"# € {prezzo_finale:.2f}")
        # Modificato "Cliente" in "Paziente"
        st.success(f"Risparmio Paziente: € {sconto_euro:.2f}")
    else:
        prezzo_finale = prezzo_totale
        st.markdown(f"# € {prezzo_finale:.2f}")

    st.markdown("---")

    # --- SALVATAGGIO ---
    if st.button("💾 REGISTRA E COPIA PER RECEPTION", type="primary"):
        if nome_paziente:
            # 1. Salviamo nell'archivio dell'app
            record = {
                "Ora": datetime.datetime.now().strftime("%H:%M"),
                "Paziente": nome_paziente,
                "Fatto Oggi": trattamento_oggi,
                "Pacchetto Venduto": f"{n_vendute}x {trattamento_scelto}",
                "Incasso Previsto": f"€ {prezzo_finale:.2f}"
            }
            st.session_state.pazienti.append(record)
            st.toast("Salvato!", icon="✅")
            
            # 2. Generiamo testo per WhatsApp (Modificato CLIENTE in PAZIENTE)
            msg = f"""*PAZIENTE:* {nome_paziente}
*OGGI:* {trattamento_oggi}
*PACCHETTO:* {n_vendute}x {trattamento_scelto}
*TOTALE:* € {prezzo_finale:.2f}"""
            
            st.code(msg, language="markdown")
            st.caption("👆 Tieni premuto il testo grigio, fai COPIA e incollalo su WhatsApp.")
        else:
            st.error("Inserisci il nome del paziente!")

# ==========================================
# SEZIONE 2: ARCHIVIO
# ==========================================
elif scelta == "📂 ARCHIVIO GIORNALIERO":
    st.markdown("#### Pazienti registrati in questa sessione")
    if st.session_state.pazienti:
        df = pd.DataFrame(st.session_state.pazienti)
        st.dataframe(df, use_container_width=True)
        st.info("💡 Nota: Se chiudi o ricarichi la pagina, questa lista si azzera.")
    else:
        st.warning("Nessuna vendita registrata oggi.")
