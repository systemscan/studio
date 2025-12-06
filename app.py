import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE UFFICIALE v1.7 ---
st.set_page_config(page_title="Studio Manager v1.7", layout="centered")

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

if "carrello" not in st.session_state:
    st.session_state.carrello = []

# Variabile per mostrare il messaggio DOPO il reset
if "msg_finale" not in st.session_state:
    st.session_state.msg_finale = None

# --- LISTINO v1.7 ---
TRATTAMENTI_STANDARD = {
    "Vacuum Therapy (20 min)": 80.0,
    "Vacuum Therapy (50 min)": 120.0,
    "Vacuum Therapy + RFF (25 min)": 120.0,
    "Radiofrequenza Frazionata Viso": 200.0,
    "Radiofrequenza Mono e Bipolare": 100.0,
    "Biorivitalizzazione Oro 24K": 200.0,
    "PMP": 150.0,
    "Esosomi": 150.0,
    "Linfodrenaggio Manuale": 70.0,
    "Laser Epilazione (Gambe)": 150.0,
    "Pacchetto Dimagrimento Urto": 90.0,
    "Pulizia Viso Profonda": 60.0
}

# --- FUNZIONE GRAFICA: BARRA EMOZIONALE ---
def crea_barra_emozionale(percentuale):
    if percentuale < 50:
        colore = "#ff2b2b" # Rosso
        msg = "⚠️ RISULTATO INSUFFICIENTE"
    elif percentuale < 90:
        colore = "#ffa500" # Arancione
        msg = "⚖️ RISULTATO PARZIALE"
    else:
        colore = "#00c853" # Verde
        msg = "⭐ RISULTATO TOP (Protocollo Completo)"

    st.markdown(f"""
    <div style="margin-top: 10px; margin-bottom: 5px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-weight:bold; color:{colore};">
            <span>{msg}</span>
            <span>{percentuale}%</span>
        </div>
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 15px; height: 20px;">
            <div style="width: {percentuale}%; background-color: {colore}; height: 100%; border-radius: 15px; transition: width 0.5s ease-in-out; box-shadow: 0 0 10px {colore};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MENU PRINCIPALE ---
st.markdown("### 🏥 Studio Medico & Estetico - v1.7")
scelta = st.radio("Menu:", ["📝 NUOVA SCHEDA", "📂 ARCHIVIO GIORNALIERO"], horizontal=True)
st.divider()

if scelta == "📝 NUOVA SCHEDA":

    # --- STEP 1: ANAGRAFICA ---
    st.markdown("#### 1. Anagrafica Paziente")
    col1, col2 = st.columns(2)
    with col1:
        # Chiave per reset
        nome_paziente = st.text_input("Nome e Cognome", key="input_nome")
    with col2:
        # Chiave per reset
        trattamento_oggi = st.text_input("Trattamento fatto OGGI", placeholder="Es. Igiene", key="input_oggi")

    st.markdown("---")

    # --- STEP 2: COSTRUZIONE PACCHETTO ---
    st.markdown("#### 2. Costruzione Pacchetto")
    
    with st.container(border=True):
        
        # A. TRATTAMENTO
        modo_inserimento = st.radio("Sorgente:", ["Da Listino", "Scrittura Libera"], horizontal=True, label_visibility="collapsed")
        prezzo_singolo_base = 0.0

        if modo_inserimento == "Da Listino":
            c1, c2 = st.columns([2, 1])
            with c1:
                trattamento_scelto = st.selectbox("Trattamento:", list(TRATTAMENTI_STANDARD.keys()), key="sel_tratt")
            with c2:
                valore_listino = TRATTAMENTI_STANDARD[trattamento_scelto]
                st.metric(label="Prezzo Listino", value=f"€ {valore_listino}")
                prezzo_singolo_base = valore_listino
        else:
            c1, c2 = st.columns([2, 1])
            with c1:
                # Chiave per reset
                trattamento_scelto = st.text_input("Trattamento (Libero):", placeholder="Es. Trattamento Speciale", key="input_tratt_libero")
            with c2:
                # Chiave per reset
                valore_manuale = st.number_input("Prezzo 1 Seduta:", value=0.0, step=10.0, key="input_prezzo_libero")
                if valore_manuale > 0:
                    st.metric(label="Prezzo Impostato", value=f"€ {valore_manuale}")
                prezzo_singolo_base = valore_manuale

        # B. PROTOCOLLO E FREQUENZA
        st.write("")
        st.caption("B. PROTOCOLLO E FREQUENZA")
        
        # Chiave per reset
        frequenza_sedute = st.text_input("Frequenza Sedute:", placeholder="Es. 1 a settimana", key="input_freq")

        col_ideali, col_proposte = st.columns(2)
        with col_ideali:
            n_ideali = st.number_input("Sedute IDEALI:", value=10, min_value=1, key="num_ideali")
        with col_proposte:
            n_proposte = st.number_input("Sedute PROPOSTE:", value=8, min_value=1, key="num_proposte")

        st.divider()

        # C. CONFERMA E PREZZO
        st.caption("C. CONFERMA PAZIENTE & TOTALE")
        
        col_conferma, col_totale = st.columns([1, 1])
        
        with col_conferma:
            n_accettate = st.number_input("Sedute ACCETTATE (Reali):", value=n_proposte, min_value=1, key="num_accettate")
            
            # Calcolo Pieno
            totale_pieno_reale = prezzo_singolo_base * n_accettate
            
            # Opzione Segreta
            riduzione_applicata = 0.0
            with st.expander("⚙️ Opzioni"):
                st.caption(f"Totale listino attuale: € {totale_pieno_reale:.2f}")
                # Chiave per reset
                riduzione_applicata = st.number_input("Riduzione (€):", min_value=0.0, max_value=totale_pieno_reale, step=10.0, label_visibility="collapsed", key="input_riduzione")

        # Calcolo Finale
        totale_riga_finale = totale_pieno_reale - riduzione_applicata

        with col_totale:
            if riduzione_applicata > 0:
                st.markdown(f"<div style='text-align: right; color: gray; font-size: 14px; text-decoration: line-through;'>€ {totale_pieno_reale:.2f}</div>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='text-align: right; font-size: 28px; font-weight: bold; color: #31333F;'>€ {totale_riga_finale:.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: right; font-size: 12px; color: gray;'>Totale Pacchetto</div>", unsafe_allow_html=True)

        # BARRA EMOZIONALE
        if n_ideali > 0:
            efficacia = min(int((n_accettate / n_ideali) * 100), 100)
        else:
            efficacia = 0
        crea_barra_emozionale(efficacia)

        # Bottone Aggiungi
        st.write("")
        if st.button("➕ AGGIUNGI AL CARRELLO", use_container_width=True):
            if prezzo_singolo_base > 0:
                nome_display = trattamento_scelto if trattamento_scelto else "Trattamento Personalizzato"
                
                txt_dettaglio = f"{n_accettate}x {nome_display}"
                
                # Aggiungiamo Frequenza e Promo al dettaglio
                note_extra = []
                if frequenza_sedute:
                    note_extra.append(f"Freq: {frequenza_sedute}")
                if riduzione_applicata > 0:
                    note_extra.append("Promo")
                
                if note_extra:
                    txt_dettaglio += f" ({', '.join(note_extra)})"

                item = {
                    "Trattamento": nome_display,
                    "Sedute": n_accettate,
                    "Frequenza": frequenza_sedute,
                    "Totale": totale_riga_finale,      
                    "PrezzoPieno": totale_pieno_reale, 
                    "Dettaglio": f"{txt_dettaglio} - € {totale_riga_finale:.2f}"
                }
                st.session_state.carrello.append(item)
                
                # --- PULIZIA AUTOMATICA CAMPI PACCHETTO ---
                st.session_state["input_tratt_libero"] = ""
                st.session_state["input_prezzo_libero"] = 0.0
                st.session_state["input_freq"] = ""
                st.session_state["input_riduzione"] = 0.0
                # Reimpostiamo i numeri sedute a valori default
                st.session_state["num_ideali"] = 10
                st.session_state["num_proposte"] = 8
                st.session_state["num_accettate"] = 8
                
                st.rerun()
            else:
                st.error("Prezzo non valido.")

    # --- CARRELLO ---
    st.markdown("##### 📦 Carrello Attuale")
    totale_preventivo = 0.0
    totale_preventivo_pieno = 0.0
    
    if len(st.session_state.carrello) > 0:
        for i, item in enumerate(st.session_state.carrello):
            c_text, c_del = st.columns([5, 1])
            with c_text:
                st.text(f"{i+1}. {item['Dettaglio']}")
            with c_del:
                # Tasto rosso cancellazione singola
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.carrello.pop(i)
                    st.rerun()

            totale_preventivo += item['Totale']
            totale_preventivo_pieno += item.get('PrezzoPieno', item['Totale'])
        
        if st.button("🗑️ Svuota Tutto"):
            st.session_state.carrello = []
            st.rerun()
    else:
        st.caption("Vuoto.")

    st.markdown("---")

    # --- STEP 3: CASSA FINALE ---
    st.markdown("#### 3. Cassa Finale")
    
    prezzo_finale_cassa = totale_preventivo

    st.markdown(f"### Totale da Pagare: € {prezzo_finale_cassa:.2f}")

    # ACCONTO
    acconto = 0.0
    saldo = prezzo_finale_cassa
    
    st.markdown("##### 🔒 Acconto / Blocca Prezzo")
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        acconto = st.number_input("Versa Oggi (€):", min_value=0.0, max_value=prezzo_finale_cassa if prezzo_finale_cassa > 0 else 0.0, step=10.0, key="input_acconto")
    
    saldo = prezzo_finale_cassa - acconto
    with col_acc2:
         if acconto > 0:
             st.metric("DA SALDARE", f"€ {saldo:.2f}")
             st.success("✅ BLOCCATO")
         elif totale_preventivo < totale_preventivo_pieno:
             st.warning("⚠️ Per confermare lo sconto serve un acconto!")

    st.markdown("---")

    # --- SALVATAGGIO ---
    if st.button("💾 REGISTRA E COPIA PER RECEPTION", type="primary"):
        # Logica Sconto/Acconto
        ha_sconto = totale_preventivo < totale_preventivo_pieno
        
        if nome_paziente and len(st.session_state.carrello) > 0:
            
            # BLOCCO: Se c'è sconto ma acconto è 0 -> ERRORE
            if ha_sconto and acconto <= 0:
                st.error("⛔ ERRORE: Hai applicato uno sconto ma non hai inserito un Acconto! Inserisci un acconto per procedere.")
                st.session_state.msg_finale = None # Pulisci eventuali vecchi messaggi
            else:
                # CREAZIONE MESSAGGIO
                lista_str = ""
                for item in st.session_state.carrello:
                    lista_str += f"- {item['Dettaglio']}\n"

                if ha_sconto:
                    blocco_totali = f"*TOTALE LISTINO:* € {totale_preventivo_pieno:.2f}\n*TOTALE SCONTATO:* € {totale_preventivo:.2f}"
                else:
                    blocco_totali = f"*TOTALE:* € {totale_preventivo:.2f}"

                if acconto > 0:
                    dett = f"🔒 ACCONTO: € {acconto:.2f}\n⏳ SALDO: € {saldo:.2f}"
                else:
                    dett = "(Saldo completo o pagamento standard)"

                # Salva nello storico
                st.session_state.pazienti.append({
                    "Ora": datetime.datetime.now().strftime("%H:%M"),
                    "Paziente": nome_paziente,
                    "Totale": f"€ {prezzo_finale_cassa:.2f}",
                    "Acconto": f"€ {acconto:.2f}"
                })
                
                # Messaggio Finale
                msg = f"""*PAZIENTE:* {nome_paziente}
*OGGI:* {trattamento_oggi}
----------------
*ACQUISTA:*
{lista_str}
----------------
{blocco_totali}
{dett}"""
                
                # RESETTA TUTTO E SALVA IL MESSAGGIO DA MOSTRARE
                st.session_state.carrello = []
                st.session_state.msg_finale = msg
                
                # PULIZIA CAMPI PAZIENTE
                st.session_state["input_nome"] = ""
                st.session_state["input_oggi"] = ""
                st.session_state["input_acconto"] = 0.0
                
                st.rerun()
        else:
            st.error("Dati mancanti! Inserisci nome e almeno un pacchetto.")

    # MOSTRA MESSAGGIO SE PRESENTE (SOTTO IL PULSANTE)
    if st.session_state.msg_finale:
        st.success("✅ Registrato! Copia il messaggio qui sotto:")
        st.code(st.session_state.msg_finale, language="markdown")
        if st.button("Chiudi Messaggio"):
            st.session_state.msg_finale = None
            st.rerun()

elif scelta == "📂 ARCHIVIO GIORNALIERO":
    st.markdown("#### Storico di oggi")
    if st.session_state.pazienti:
        st.dataframe(pd.DataFrame(st.session_state.pazienti), use_container_width=True)
    else:
        st.info("Nessun dato.")
