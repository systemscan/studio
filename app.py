import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURAZIONE UFFICIALE v1.4 ---
st.set_page_config(page_title="Studio Manager v1.4", layout="centered")

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

# --- LISTINO v1.4 ---
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
st.markdown("### 🏥 Studio Medico & Estetico - v1.4")
scelta = st.radio("Menu:", ["📝 NUOVA SCHEDA", "📂 ARCHIVIO GIORNALIERO"], horizontal=True)
st.divider()

if scelta == "📝 NUOVA SCHEDA":

    # --- STEP 1: ANAGRAFICA ---
    st.markdown("#### 1. Anagrafica Paziente")
    col1, col2 = st.columns(2)
    with col1:
        nome_paziente = st.text_input("Nome e Cognome")
    with col2:
        trattamento_oggi = st.text_input("Trattamento fatto OGGI", placeholder="Es. Igiene")

    st.markdown("---")

    # --- STEP 2: COSTRUZIONE PACCHETTO ---
    st.markdown("#### 2. Costruzione Pacchetto")
    st.info("Configura il pacchetto (lo sconto è nascosto nell'ingranaggio).")

    with st.container(border=True):
        
        # A. SCELTA E DIAGNOSI
        st.caption("A. TRATTAMENTO E PROTOCOLLO")
        
        modo_inserimento = st.radio("Sorgente:", ["Da Listino", "Scrittura Libera"], horizontal=True, label_visibility="collapsed")
        prezzo_singolo_base = 0.0

        if modo_inserimento == "Da Listino":
            c1, c2 = st.columns([2, 1])
            with c1:
                trattamento_scelto = st.selectbox("Trattamento:", list(TRATTAMENTI_STANDARD.keys()))
            with c2:
                valore_listino = TRATTAMENTI_STANDARD[trattamento_scelto]
                st.metric(label="Prezzo Listino", value=f"€ {valore_listino}")
                prezzo_singolo_base = valore_listino
        else:
            c1, c2 = st.columns([2, 1])
            with c1:
                trattamento_scelto = st.text_input("Trattamento (Libero):", placeholder="Es. Trattamento Speciale")
            with c2:
                valore_manuale = st.number_input("Prezzo 1 Seduta:", value=0.0, step=10.0)
                if valore_manuale > 0:
                    st.metric(label="Prezzo Impostato", value=f"€ {valore_manuale}")
                prezzo_singolo_base = valore_manuale

        # PROTOCOLLO MEDICO
        st.write("")
        col_ideali, col_proposte = st.columns(2)
        with col_ideali:
            n_ideali = st.number_input("Sedute IDEALI (Protocollo):", value=10, min_value=1)
        with col_proposte:
            n_proposte = st.number_input("Sedute che PROPONI:", value=8, min_value=1)

        # B. PREZZO E SCONTO (STEALTH MODE)
        # Calcoliamo il totale della proposta iniziale
        totale_proposta_listino = prezzo_singolo_base * n_proposte
        
        # Sconto Nascosto
        sconto_applicato = 0.0
        with st.expander("⚙️ Opzioni (Sconto)"): # Qui è nascosto
            st.caption(f"Totale listino per {n_proposte} sedute: € {totale_proposta_listino:.2f}")
            sconto_applicato = st.number_input("Sconto Extra (€):", min_value=0.0, max_value=totale_proposta_listino, step=10.0)
        
        # Calcolo del prezzo seduta effettivo (scontato o no)
        totale_dopo_sconto = totale_proposta_listino - sconto_applicato
        prezzo_effettivo_seduta = totale_dopo_sconto / n_proposte if n_proposte > 0 else 0

        # Mostra prezzo solo se scontato, altrimenti mostra quello base
        if sconto_applicato > 0:
            st.write(f"Prezzo Listino: <strike style='color:red'>€ {totale_proposta_listino:.2f}</strike>", unsafe_allow_html=True)
            st.write(f"**Prezzo Scontato: € {totale_dopo_sconto:.2f}**")
        
        st.divider()

        # C. COSA ACQUISTA (BARRA E CONFERMA)
        st.markdown("##### B. CONFERMA PAZIENTE")
        st.caption("Quante ne confermiamo a questo prezzo?")

        col_acc, col_tot = st.columns([1, 1])
        with col_acc:
            n_accettate = st.number_input("Sedute ACCETTATE (Reali):", value=n_proposte, min_value=1)
        
        # Calcolo Totale Riga Finale (Prezzo effettivo x Numero accettato)
        totale_riga_finale = prezzo_effettivo_seduta * n_accettate

        with col_tot:
            st.metric(label="Totale Pacchetto", value=f"€ {totale_riga_finale:.2f}")

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
                if sconto_applicato > 0:
                    txt_dettaglio += " (Promo)"

                item = {
                    "Trattamento": nome_display,
                    "Sedute": n_accettate,
                    "Totale": totale_riga_finale,
                    "Dettaglio": f"{txt_dettaglio} - € {totale_riga_finale:.2f}"
                }
                st.session_state.carrello.append(item)
                st.rerun()
            else:
                st.error("Prezzo non valido.")

    # --- CARRELLO ---
    st.markdown("##### 📦 Carrello Attuale")
    totale_preventivo = 0.0
    if len(st.session_state.carrello) > 0:
        for i, item in enumerate(st.session_state.carrello):
            st.text(f"{i+1}. {item['Dettaglio']}")
            totale_preventivo += item['Totale']
        
        if st.button("🗑️ Svuota Carrello"):
            st.session_state.carrello = []
            st.rerun()
    else:
        st.caption("Vuoto.")

    st.markdown("---")

    # --- STEP 3: CASSA FINALE ---
    st.markdown("#### 3. Cassa Finale")
    
    # Sconto Finale Nascosto
    sconto_finale = 0.0
    with st.expander("⚙️ Sconto Cassa (Opzionale)"):
        st.caption("Sconto ulteriore sul totale complessivo.")
        sconto_finale = st.number_input("Sconto Cassa (€):", min_value=0.0, max_value=totale_preventivo, step=10.0)

    prezzo_finale_cassa = totale_preventivo - sconto_finale

    if sconto_finale > 0:
        st.caption("Totale:")
        st.markdown(f"#### <strike style='color:red'>€ {totale_preventivo:.2f}</strike>", unsafe_allow_html=True)
        st.markdown(f"## € {prezzo_finale_cassa:.2f}")
    else:
        st.markdown(f"### Totale da Pagare: € {prezzo_finale_cassa:.2f}")

    # ACCONTO
    acconto = 0.0
    saldo = prezzo_finale_cassa
    
    # L'acconto appare SOLO se c'è uno sconto (o se lo apri manualmente)
    # Ma per sicurezza lo lasciamo visibile per chiudere la vendita
    st.markdown("##### 🔒 Acconto / Blocca Prezzo")
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        acconto = st.number_input("Versa Oggi (€):", min_value=0.0, max_value=prezzo_finale_cassa if prezzo_finale_cassa > 0 else 0.0, step=10.0)
    
    saldo = prezzo_finale_cassa - acconto
    with col_acc2:
         if acconto > 0:
             st.metric("DA SALDARE", f"€ {saldo:.2f}")
             st.success("✅ BLOCCATO")

    st.markdown("---")

    # --- SALVATAGGIO ---
    if st.button("💾 REGISTRA E COPIA PER RECEPTION", type="primary"):
        if nome_paziente and len(st.session_state.carrello) > 0:
            
            lista_str = ""
            for item in st.session_state.carrello:
                lista_str += f"- {item['Dettaglio']}\n"

            if acconto > 0:
                dett = f"🔒 ACCONTO: € {acconto:.2f}\n⏳ SALDO: € {saldo:.2f}"
            else:
                dett = f"💰 TOTALE: € {prezzo_finale_cassa:.2f}"

            st.session_state.pazienti.append({
                "Ora": datetime.datetime.now().strftime("%H:%M"),
                "Paziente": nome_paziente,
                "Fatto Oggi": trattamento_oggi,
                "Totale": f"€ {prezzo_finale_cassa:.2f}",
                "Acconto": f"€ {acconto:.2f}"
            })
            st.toast("Salvato!")
            
            msg = f"""*PAZIENTE:* {nome_paziente}
*OGGI:* {trattamento_oggi}
----------------
*ACQUISTA:*
{lista_str}
----------------
*TOTALE:* € {prezzo_finale_cassa:.2f}
{dett}"""
            st.code(msg, language="markdown")
            st.caption("👆 Copia e invia su WhatsApp")
        else:
            st.error("Dati mancanti!")

elif scelta == "📂 ARCHIVIO GIORNALIERO":
    st.markdown("#### Storico di oggi")
    if st.session_state.pazienti:
        st.dataframe(pd.DataFrame(st.session_state.pazienti), use_container_width=True)
    else:
        st.info("Nessun dato.")
