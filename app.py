import streamlit as st
import datetime
import pandas as pd
import urllib.parse
import os

# --- CONFIGURAZIONE UFFICIALE v2.1 ---
st.set_page_config(page_title="Studio Manager v2.1", layout="centered")

# --- PASSWORD PERSISTENTE ---
password_segreta = "studio2024"

def check_password():
    if "auth" in st.query_params and st.query_params["auth"] == "true":
        return True
    if st.session_state.get("password_correct", False):
        return True
    st.markdown("### 🔒 Accesso Riservato")
    pwd = st.text_input("Password:", type="password")
    if st.button("Entra"):
        if pwd == password_segreta:
            st.session_state.password_correct = True
            st.query_params["auth"] = "true"
            st.rerun()
        else:
            st.error("Password errata")
    return False

if not check_password():
    st.stop()

# --- TASTO LOGOUT ---
with st.sidebar:
    if st.button("Esci (Logout)"):
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()

# --- MEMORIA CONDIVISA (ARCHIVIO) ---
@st.cache_resource
def get_archivio_condiviso():
    return []

def salva_in_memoria(record):
    archivio = get_archivio_condiviso()
    archivio.append(record)

# --- GESTIONE RESET INTELLIGENTE (MODIFICATO PER EVITARE L'ERRORE) ---

# 1. Reset TOTALE (Scatta solo dopo aver SALVATO il paziente)
if "reset_completo" in st.session_state and st.session_state.reset_completo:
    st.session_state.final_nome = ""
    st.session_state.final_oggi = ""
    st.session_state.final_acconto = 0.0
    st.session_state.reset_completo = False

# 2. Reset PARZIALE (Scatta dopo AGGIUNGI AL CARRELLO o SALVA)
if "reset_trigger" in st.session_state and st.session_state.reset_trigger:
    st.session_state.final_tratt_libero = ""
    st.session_state.final_prezzo_libero = 0.0
    st.session_state.final_freq = ""
    st.session_state.final_riduzione = 0.0
    st.session_state.final_omaggio_nome = ""
    st.session_state.final_omaggio_sedute = 1
    st.session_state.final_ideali = 0
    st.session_state.final_proposte = 0
    st.session_state.final_accettate = 0
    st.session_state.reset_trigger = False

# --- CARRELLO ---
if "carrello" not in st.session_state:
    st.session_state.carrello = []
if "msg_finale" not in st.session_state:
    st.session_state.msg_finale = None

# --- LISTINO ---
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

# --- FUNZIONE GRAFICA ---
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
st.markdown("### 🏥 Studio Medico & Estetico - v2.1")
scelta = st.radio("Menu:", ["📝 NUOVA SCHEDA", "📂 ARCHIVIO GIORNALIERO"], horizontal=True)
st.divider()

if st.session_state.msg_finale:
    st.success("✅ Registrato e Archiviato!")
    testo_encoded = urllib.parse.quote(st.session_state.msg_finale)
    link_wa = f"https://wa.me/?text={testo_encoded}"
    st.markdown(f"""
    <a href="{link_wa}" target="_blank">
        <button style="width: 100%; background-color: #25D366; color: white; padding: 15px; border: none; border-radius: 10px; font-size: 18px; font-weight: bold; cursor: pointer;">
            ✈️ CLICCA QUI PER INVIARE SU WHATSAPP
        </button>
    </a>
    """, unsafe_allow_html=True)
    st.caption("Oppure copia sotto:")
    st.code(st.session_state.msg_finale, language="markdown")
    if st.button("Chiudi e Nuovo Paziente"):
        st.session_state.msg_finale = None
        st.rerun()
    st.divider()

if scelta == "📝 NUOVA SCHEDA":
    st.markdown("#### 1. Anagrafica Paziente")
    col1, col2 = st.columns(2)
    with col1:
        nome_paziente = st.text_input("Nome e Cognome", key="final_nome")
    with col2:
        trattamento_oggi = st.text_input("Trattamento fatto OGGI", placeholder="Es. Igiene", key="final_oggi")
    st.markdown("---")

    st.markdown("#### 2. Costruzione Pacchetto")
    with st.container(border=True):
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
                trattamento_scelto = st.text_input("Trattamento (Libero):", placeholder="Es. Trattamento Speciale", key="final_tratt_libero")
            with c2:
                valore_manuale = st.number_input("Prezzo 1 Seduta:", value=0.0, step=10.0, key="final_prezzo_libero")
                if valore_manuale > 0: st.metric(label="Prezzo Impostato", value=f"€ {valore_manuale}")
                prezzo_singolo_base = valore_manuale

        st.write("")
        st.caption("B. PROTOCOLLO")
        col_ideali, col_proposte = st.columns(2)
        with col_ideali:
            n_ideali = st.number_input("Sedute IDEALI:", value=0, min_value=0, key="final_ideali")
        with col_proposte:
            n_proposte = st.number_input("Sedute PROPOSTE:", value=0, min_value=0, key="final_proposte")
        frequenza_sedute = st.text_input("Frequenza Sedute:", placeholder="Es. 1 a settimana", key="final_freq")
        
        st.divider()
        st.caption("C. CONFERMA PAZIENTE & TOTALE")
        col_conferma, col_totale = st.columns([1, 1])
        with col_conferma:
            n_accettate = st.number_input("Sedute ACCETTATE (Reali):", value=0, min_value=0, key="final_accettate")
            
            # --- PROTEZIONE MATEMATICA ---
            totale_pieno_reale = prezzo_singolo_base * n_accettate
            if "final_riduzione" in st.session_state and st.session_state.final_riduzione > totale_pieno_reale:
                st.session_state.final_riduzione = float(totale_pieno_reale)
            
            riduzione_applicata = 0.0
            omaggio_nome = ""
            omaggio_sedute = 1
            
            with st.expander("⚙️ Opzioni"):
                st.markdown("**💰 RIDUZIONE PREZZO**")
                st.caption(f"Totale attuale: € {totale_pieno_reale:.2f}")
                riduzione_applicata = st.number_input("Sconto in Euro (€):", min_value=0.0, max_value=float(totale_pieno_reale), step=10.0, key="final_riduzione")
                
                st.markdown("---")
                st.markdown("**🎁 AGGIUNGI OMAGGIO**")
                omaggio_nome = st.text_input("Nome del Regalo:", placeholder="Es. Pressoterapia", key="final_omaggio_nome")
                omaggio_sedute = st.number_input("Numero Sedute Regalo:", min_value=1, value=1, key="final_omaggio_sedute")

        totale_riga_finale = totale_pieno_reale - riduzione_applicata
        with col_totale:
            if riduzione_applicata > 0:
                st.markdown(f"<div style='text-align: right; color: gray; font-size: 14px; text-decoration: line-through;'>€ {totale_pieno_reale:.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: right; font-size: 28px; font-weight: bold; color: #31333F;'>€ {totale_riga_finale:.2f}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: right; font-size: 12px; color: gray;'>Totale Pacchetto</div>", unsafe_allow_html=True)

        if n_ideali > 0: efficacia = min(int((n_accettate / n_ideali) * 100), 100)
        else: efficacia = 0
        crea_barra_emozionale(efficacia)

        st.write("")
        if st.button("➕ AGGIUNGI AL CARRELLO", use_container_width=True):
            if prezzo_singolo_base > 0:
                nome_display = trattamento_scelto if trattamento_scelto else "Trattamento Personalizzato"
                txt_dettaglio = f"{n_accettate}x {nome_display}"
                note_extra = []
                if frequenza_sedute: note_extra.append(f"Freq: {frequenza_sedute}")
                if riduzione_applicata > 0: note_extra.append("Promo")
                if note_extra: txt_dettaglio += f" ({', '.join(note_extra)})"
                if omaggio_nome: txt_dettaglio += f"\n   + 🎁 OMAGGIO: {omaggio_sedute}x {omaggio_nome}"
                
                item = {
                    "Trattamento": nome_display,
                    "Sedute": n_accettate,
                    "Frequenza": frequenza_sedute,
                    "Totale": totale_riga_finale,      
                    "PrezzoPieno": totale_pieno_reale, 
                    "Dettaglio": f"{txt_dettaglio} - € {totale_riga_finale:.2f}"
                }
                st.session_state.carrello.append(item)
                # Attiva SOLO il reset del pacchetto, NON quello completo
                st.session_state.reset_trigger = True 
                st.rerun()
            else:
                st.error("Prezzo non valido.")

    st.markdown("##### 📦 Carrello Attuale")
    totale_preventivo = 0.0
    totale_preventivo_pieno = 0.0
    ha_omaggio_nel_carrello = False 
    if len(st.session_state.carrello) > 0:
        for i, item in enumerate(st.session_state.carrello):
            c_text, c_del = st.columns([5, 1])
            with c_text:
                st.text(f"{i+1}. {item['Dettaglio']}")
                if "🎁 OMAGGIO" in item['Dettaglio']: ha_omaggio_nel_carrello = True
            with c_del:
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
    st.markdown("#### 3. Cassa Finale")
    prezzo_finale_cassa = totale_preventivo
    st.markdown(f"### Totale da Pagare: € {prezzo_finale_cassa:.2f}")

    acconto = 0.0
    saldo = prezzo_finale_cassa
    ha_sconto = totale_preventivo < totale_preventivo_pieno
    acconto_obbligatorio = ha_sconto or ha_omaggio_nel_carrello

    st.markdown("##### 🔒 Acconto / Blocca Prezzo")
    
    # --- PROTEZIONE MATEMATICA ACCONTO ---
    if "final_acconto" in st.session_state and st.session_state.final_acconto > prezzo_finale_cassa:
        st.session_state.final_acconto = float(prezzo_finale_cassa)

    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        acconto = st.number_input("Versa Oggi (€):", min_value=0.0, max_value=float(prezzo_finale_cassa), step=10.0, key="final_acconto")
    
    saldo = prezzo_finale_cassa - acconto
    with col_acc2:
         if acconto > 0:
             st.metric("DA SALDARE", f"€ {saldo:.2f}")
             st.success("✅ BLOCCATO")
         elif acconto_obbligatorio:
             st.warning("⚠️ Per confermare Omaggi o Sconti serve un acconto!")

    st.markdown("---")
    
    # --- SALVATAGGIO FINALE ---
    if st.button("💾 REGISTRA E COPIA PER RECEPTION", type="primary"):
        
        # 1. Controllo NOME
        if not nome_paziente:
            st.error("⚠️ ERRORE: Hai dimenticato di scrivere il NOME del paziente in alto!")
            
        # 2. Controllo CARRELLO
        elif len(st.session_state.carrello) == 0:
            st.error("⚠️ ERRORE: Il Carrello è vuoto! Devi premere il tasto '➕ AGGIUNGI AL CARRELLO' prima di salvare.")
            
        # 3. Controllo ACCONTO
        elif acconto_obbligatorio and acconto <= 0:
            st.error("⛔ ERRORE: Hai applicato uno Sconto o un Omaggio. Inserisci un Acconto per procedere!")
            
        # 4. TUTTO OK -> SALVA
        else:
            lista_str = ""
            for item in st.session_state.carrello:
                lista_str += f"- {item['Dettaglio']}\n"
            
            if ha_sconto:
                blocco_totali = f"*TOTALE LISTINO:* € {totale_preventivo_pieno:.2f}\n*TOTALE SCONTATO:* € {totale_preventivo:.2f}"
            else:
                blocco_totali = f"*TOTALE:* € {totale_preventivo:.2f}"
            
            if acconto > 0: dett = f"🔒 ACCONTO: € {acconto:.2f}\n⏳ SALDO: € {saldo:.2f}"
            else: dett = "(Saldo completo o pagamento standard)"

            record = {
                "Ora": datetime.datetime.now().strftime("%H:%M"),
                "Paziente": nome_paziente,
                "Trattamento": trattamento_oggi,
                "Totale": f"€ {prezzo_finale_cassa:.2f}",
                "Acconto": f"€ {acconto:.2f}"
            }
            salva_in_memoria(record)
            
            msg = f"""*PAZIENTE:* {nome_paziente}
*OGGI:* {trattamento_oggi}
----------------
*ACQUISTA:*
{lista_str}
----------------
{blocco_totali}
{dett}"""
            
            st.session_state.carrello = []
            st.session_state.msg_finale = msg
            
            # ATTIVIAMO IL RESET TOTALE (che pulisce il nome) E IL PARZIALE (che pulisce il pacchetto)
            st.session_state.reset_completo = True
            st.session_state.reset_trigger = True
            
            st.rerun()

elif scelta == "📂 ARCHIVIO GIORNALIERO":
    st.markdown("#### Storico di oggi (Memoria Server)")
    archivio = get_archivio_condiviso()
    if len(archivio) > 0:
        df = pd.DataFrame(archivio)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nessuna vendita registrata in questa sessione server.")
