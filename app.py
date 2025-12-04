import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE UFFICIALE v1.0 ---
st.set_page_config(page_title="Studio Manager v1.0", layout="centered")

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

# --- MEMORIA DATI E CARRELLO ---
if "pazienti" not in st.session_state:
    st.session_state.pazienti = []

if "carrello" not in st.session_state:
    st.session_state.carrello = []

# --- LISTINO PREDEFINITO ---
TRATTAMENTI_STANDARD = {
    "Vacuum Therapy (20 min)": 80.0,
    "Vacuum Therapy (50 min)": 120.0,
    "Vacuum Therapy + RFF  (25 min)": 120.0,
    "Radiofrequenza Frazionata Viso": 200.0,
    "Radiofrequenza Mono e Bipolare": 100.0,
    "Biorivitalizzazione Oro 24K": 200.0,
    "PMP": 150.0,
    "Esosomi": 150.0,
}

# --- FUNZIONE GRAFICA: BARRA EMOZIONALE ---
def crea_barra_emozionale(percentuale):
    """Crea una barra di progresso colorata e accattivante in HTML"""
    
    # Definizione colori e messaggi
    if percentuale < 50:
        colore = "#ff2b2b" # Rosso acceso
        msg = "⚠️ RISULTATO INSUFFICIENTE"
    elif percentuale < 90:
        colore = "#ffa500" # Arancione
        msg = "⚖️ RISULTATO BUONO (MA PARZIALE)"
    else:
        colore = "#00c853" # Verde Smeraldo
        msg = "⭐ RISULTATO ECCELLENTE (TOP)"

    # HTML/CSS per la barra
    st.markdown(f"""
    <div style="margin-top: 10px; margin-bottom: 5px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-weight:bold; color:{colore};">
            <span>{msg}</span>
            <span>{percentuale}%</span>
        </div>
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 15px; height: 20px;">
            <div style="width: {percentuale}%; background-color: {colore}; height: 100%; border-radius: 15px; transition: width 0.5s ease-in-out; box-shadow: 0 0 10px {colore};"></div>
        </div>
        <div style="font-size: 12px; color: gray; margin-top: 5px; font-style: italic;">
            Maggiore è la copertura, più duraturo sarà l'effetto estetico.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MENU PRINCIPALE ---
st.markdown("### 🏥 Studio Medico & Estetico - v1.0")
scelta = st.radio("Menu:", ["📝 NUOVA SCHEDA", "📂 ARCHIVIO GIORNALIERO"], horizontal=True)
st.divider()

# ==========================================
# SEZIONE 1: VENDITA
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

    # --- STEP 2: AGGIUNGI TRATTAMENTI (LOOP) ---
    st.markdown("#### 2. Costruzione Preventivo")
    st.info("Configura un pacchetto e premi 'Aggiungi' per inserirlo nel preventivo.")

    # Box Grigio per l'inserimento
    with st.container(border=True):
        modo_inserimento = st.radio("Sorgente:", ["Da Listino", "Scrittura Libera"], horizontal=True)
        
        prezzo_singolo = 0.0

        if modo_inserimento == "Da Listino":
            c1, c2 = st.columns([2, 1])
            with c1:
                trattamento_scelto = st.selectbox("Trattamento:", list(TRATTAMENTI_STANDARD.keys()))
            with c2:
                valore_listino = TRATTAMENTI_STANDARD[trattamento_scelto]
                st.metric(label="Prezzo Singolo", value=f"€ {valore_listino}")
                prezzo_singolo = valore_listino
        else:
            # Scrittura Libera
            c1, c2 = st.columns([2, 1])
            with c1:
                trattamento_scelto = st.text_input("Trattamento (Libero):", placeholder="Es. Protocollo Sposa")
            with c2:
                valore_manuale = st.number_input("Prezzo 1 Seduta:", value=0.0, step=10.0, min_value=0.0)
                # Mostra Prezzo Grande anche qui
                if valore_manuale > 0:
                    st.metric(label="Prezzo Impostato", value=f"€ {valore_manuale}")
                prezzo_singolo = valore_manuale

        st.write("") 
        col_a, col_b = st.columns(2)
        with col_a:
            n_ideali = st.number_input("Sedute IDEALI:", value=8, min_value=1, key="ideal")
        with col_b:
            n_vendute = st.number_input("Sedute PROPOSTE:", value=6, min_value=1, key="real")

        # Calcolo percentuale
        if n_ideali > 0:
            efficacia = min(int((n_vendute / n_ideali) * 100), 100)
        else:
            efficacia = 0
        
        # --- BARRA EMOZIONALE ---
        crea_barra_emozionale(efficacia)

        st.write("")
        # Tasto per aggiungere al carrello
        if st.button("➕ AGGIUNGI AL PREVENTIVO"):
            if prezzo_singolo > 0:
                nome_display = trattamento_scelto if trattamento_scelto else "Trattamento Personalizzato"
                totale_riga = prezzo_singolo * n_vendute
                item = {
                    "Trattamento": nome_display,
                    "Sedute": n_vendute,
                    "Totale": totale_riga,
                    "Dettaglio": f"{n_vendute}x {nome_display} (€{totale_riga:.0f})"
                }
                st.session_state.carrello.append(item)
                st.rerun()
            else:
                st.error("Inserisci un prezzo valido!")

    # --- VISUALIZZAZIONE CARRELLO ---
    st.markdown("##### 📦 Riepilogo Pacchetti Inseriti")
    
    totale_preventivo = 0.0
    
    if len(st.session_state.carrello) > 0:
        for i, item in enumerate(st.session_state.carrello):
            st.text(f"{i+1}. {item['Dettaglio']}")
            totale_preventivo += item['Totale']
        
        if st.button("🗑️ Svuota tutto e ricomincia"):
            st.session_state.carrello = []
            st.rerun()
    else:
        st.caption("Nessun trattamento ancora aggiunto.")

    st.markdown("---")

    # --- STEP 3: TOTALE E CHIUSURA ---
    st.markdown("#### 3. Proposta Finale")
    
    # Sconto
    with st.expander("⚙️ Opzioni Amministrative (Clicca per modificare)"):
        st.caption("Inserisci qui un importo per ricalcolare il totale.")
        sconto_euro = st.number_input("Riduzione Importo (€):", 
                                     value=0.0, 
                                     step=10.0, 
                                     min_value=0.0, 
                                     max_value=float(totale_preventivo) if totale_preventivo > 0 else 0.0)

    prezzo_finale = totale_preventivo - sconto_euro

    # Visualizzazione Prezzi
    if sconto_euro > 0:
        st.caption("Totale Listino:")
        st.markdown(f"#### <strike style='color:red'>€ {totale_preventivo:.2f}</strike>", unsafe_allow_html=True)
    
    st.caption("Totale da Pagare:")
    st.markdown(f"## € {prezzo_finale:.2f}")

    # LOGICA ACCONTO
    acconto = 0.0
    saldo = prezzo_finale
    
    if sconto_euro > 0:
        st.markdown("---")
        st.markdown("##### 🔒 Blocca Prezzo (Richiesto Acconto)")
        col_acc1, col_acc2 = st.columns(2)
        
        with col_acc1:
            acconto = st.number_input("Versa Oggi (€):", min_value=0.0, max_value=prezzo_finale, step=10.0)
        
        saldo = prezzo_finale - acconto
        
        with col_acc2:
            if acconto > 0:
                st.metric(label="DA SALDARE (Futuro)", value=f"€ {saldo:.2f}")

        if acconto > 0:
            st.success(f"✅ OFFERTA BLOCCATA! Versa Oggi € {acconto}")
    
    st.markdown("---")

    # --- SALVATAGGIO ---
    if st.button("💾 REGISTRA E COPIA PER RECEPTION", type="primary"):
        if nome_paziente and len(st.session_state.carrello) > 0:
            
            # Creiamo la lista dei pacchetti per il messaggio
            lista_pacchetti_str = ""
            for item in st.session_state.carrello:
                lista_pacchetti_str += f"- {item['Dettaglio']}\n"

            if acconto > 0:
                dettaglio_pagamento = f"🔒 ACCONTO: € {acconto:.2f}\n⏳ SALDO: € {saldo:.2f}"
            else:
                dettaglio_pagamento = f"💰 TOTALE: € {prezzo_finale:.2f}"

            record = {
                "Ora": datetime.datetime.now().strftime("%H:%M"),
                "Paziente": nome_paziente,
                "Fatto Oggi": trattamento_oggi,
                "Pacchetto": "Multiplo (vedi dettaglio)",
                "Totale": f"€ {prezzo_finale:.2f}",
                "Acconto": f"€ {acconto:.2f}"
            }
            st.session_state.pazienti.append(record)
            
            # Reset del carrello dopo il salvataggio
            st.session_state.carrello = []
            
            st.toast("Salvato!", icon="✅")
            
            msg = f"""*PAZIENTE:* {nome_paziente}
*OGGI:* {trattamento_oggi}
----------------
*PREVENTIVO:*
{lista_pacchetti_str}
----------------
*TOTALE FINALE:* € {prezzo_finale:.2f}
{dettaglio_pagamento}"""
            
            st.code(msg, language="markdown")
            st.caption("👆 Tieni premuto, COPIA e manda su WhatsApp.")
        else:
            if len(st.session_state.carrello) == 0:
                st.error("Inserisci almeno un pacchetto prima di salvare!")
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
    else:
        st.warning("Nessuna vendita registrata oggi.")
