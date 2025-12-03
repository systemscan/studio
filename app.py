import streamlit as st
import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Sales Closer", layout="centered")

# --- PASSWORD DI PROTEZIONE ---
# Cambia "studio2024" con la password che vuoi tu
password_segreta = "studio2024"

# Funzione per verificare la password
def check_password():
    """Ritorna True se l'utente ha la password corretta."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.markdown("### 🔒 Accesso Riservato Staff")
    pwd = st.text_input("Inserisci Password:", type="password")
    
    if st.button("Accedi"):
        if pwd == password_segreta:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Password errata")
    return False

if not check_password():
    st.stop()

# --- APP VERA E PROPRIA ---

# LISTINO PREZZI (Puoi modificarli qui)
TRATTAMENTI = {
    "Vacuum Therapy (20 min)": 80.0,
    "Radiofrequenza Viso": 120.0,
    "Linfodrenaggio Manuale": 70.0,
    "Laser Epilazione (Gambe)": 150.0,
    "Pacchetto Dimagrimento Urto": 90.0
}

def main():
    # Intestazione carina per cellulare
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966334.png", width=50) # Icona generica
    st.markdown("### 💎 Protocol Builder")
    st.caption("Configuratore Offerta per Paziente")
    
    st.divider()
    
    # 1. INPUT DATI
    st.write("📋 **Configurazione**")
    trattamento = st.selectbox("Trattamento:", list(TRATTAMENTI.keys()))
    prezzo_unitario = TRATTAMENTI[trattamento]
    
    n_sedute = st.number_input("Numero Sedute:", min_value=1, value=6, step=1)

    # Logica Barra Efficacia
    ciclo_ideale = 6
    efficacia = min(int((n_sedute / ciclo_ideale) * 100), 100)
    
    if efficacia < 80:
        st.progress(efficacia)
        st.warning("⚠️ Risultato parziale (Ciclo incompleto)")
    else:
        st.progress(efficacia)
        st.success("✅ Risultato ottimale garantito")

    st.divider()

    # 2. PREZZO E SCONTO
    prezzo_totale_listino = prezzo_unitario * n_sedute
    
    st.write("💰 **Proposta Economica**")
    st.caption(f"Listino: {n_sedute} sedute x €{prezzo_unitario}")
    
    # Prezzo Barrato Visivo
    st.markdown(f"### <strike style='color:red'>€ {prezzo_totale_listino:.2f}</strike>", unsafe_allow_html=True)
    
    # Checkbox per attivare la modalità "Chiusura Vendita"
    applica_sconto = st.checkbox("Applica Sconto 'Solo Oggi'")
    
    if applica_sconto:
        perc_sconto = st.slider("Sconto (%)", 5, 30, 15)
        
        risparmio = prezzo_totale_listino * (perc_sconto / 100)
        prezzo_finale = prezzo_totale_listino - risparmio
        
        st.markdown("---")
        st.metric(label="PREZZO BLOCCATO", value=f"€ {prezzo_finale:.2f}", delta=f"Risparmi € {risparmio:.2f}")
        
        st.warning(f"🔥 Offerta valida solo oggi: {datetime.date.today().strftime('%d/%m')}")
        
        if st.button("CONFIRMA E BLOCCA PREZZO", use_container_width=True):
            st.balloons()
            st.success("✅ Offerta salvata! Procedere in reception.")
            st.caption("Fai uno screenshot di questa schermata per la reception.")

if __name__ == "__main__":
    main()
