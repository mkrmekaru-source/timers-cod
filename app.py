import streamlit as st
import time
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="Timers COD", layout="wide")

# 2. CACHE PERSISTENTE (Mantém os dados no servidor)
@st.cache_resource
def get_global_timers():
    return {}

global_timers = get_global_timers()

# 3. CSS com Fontes Equilibradas
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #0e1117; color: #ffffff; }
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    
    /* Card Ajustado */
    .timer-card {
        background-color: #161b22;
        padding: 20px 15px 75px 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
        transition: 0.3s;
    }
    
    .timer-ready {
        border: 2px solid #3fb950 !important;
        box-shadow: 0 0 15px rgba(63, 185, 80, 0.3);
        background-color: rgba(63, 185, 80, 0.05) !important;
    }
    
    /* FONTES AJUSTADAS */
    .account-label { font-size: 18px; font-weight: bold; color: #8b949e; margin-bottom: 2px; }
    .cycle-label { font-size: 14px; color: #8b949e; margin-bottom: 8px; }
    .timer-text { 
        font-size: 36px; 
        font-weight: bold; 
        margin: 10px 0; 
        font-family: 'Courier New', Courier, monospace; 
    }
    
    /* Botão Centralizado */
    [data-testid="stButton"] {
        margin-top: -65px !important;
        padding: 0 15% !important;
        position: relative;
        z-index: 10;
        display: flex;
        justify-content: center;
    }

    [data-testid="stButton"] button { 
        background-color: #21262d !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        height: 40px !important;
        font-size: 14px !important;
        width: 100% !important;
    }
    
    [data-testid="stButton"] button:hover {
        border-color: #58a6ff !important;
        color: #58a6ff !important;
        background-color: #30363d !important;
    }

    .logo-spacer { margin-bottom: 40px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Logo
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    st.image("1679019533_0X730X6C0X6F0X67.png", use_container_width=True)
st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

# 5. Lista de Contas (Restaurado para "Fazendeiro MKR X")
contas = []
for i in range(2, 12):
    duracao_min = 210 if i >= 9 else 180
    label = "3h 30m" if i >= 9 else "3h 00m"
    contas.append({"id": f"MKR {i}", "nome": f"Fazendeiro MKR {i}", "duracao_seg": duracao_min * 60, "label": label})

if 'beep_played' not in st.session_state:
    st.session_state.beep_played = {c["id"]: False for c in contas}

tocar_bip = False

# 6. Layout 5 colunas
cols = st.columns(5)

for idx, conta in enumerate(contas):
    id_conta = conta["id"]
    
    with cols[idx % 5]:
        texto_timer = "00:00:00"
        cor_timer = "#484f58"
        card_class = "timer-card"
        
        if id_conta in global_timers:
            tempo_fim = global_timers[id_conta]
            restante = tempo_fim - datetime.now()
            
            if restante.total_seconds() > 0:
                h, r = divmod(int(restante.total_seconds()), 3600)
                m, s = divmod(r, 60)
                texto_timer = f"{h:02d}:{m:02d}:{s:02d}"
                cor_timer = "#58a6ff" 
            else:
                texto_timer = "PRONTO!"
                cor_timer = "#3fb950" 
                card_class = "timer-card timer-ready" 
                
                if not st.session_state.beep_played.get(id_conta, False):
                    tocar_bip = True
                    st.session_state.beep_played[id_conta] = True
        
        st.markdown(f"""
            <div class="{card_class}">
                <div class="account-label">{conta["nome"]}</div>
                <div class="cycle-label">Ciclo: {conta["label"]}</div>
                <div class="timer-text" style="color: {cor_timer};">{texto_timer}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Iniciar {id_conta}", key=f"btn_{id_conta}", use_container_width=True):
            global_timers[id_conta] = datetime.now() + timedelta(seconds=conta["duracao_seg"])
            st.session_state.beep_played[id_conta] = False
            st.rerun()

# 7. Sistema de Áudio (JavaScript)
if tocar_bip:
    uid = time.time()
    codigo_js = f"""
    <script>
        var url_som = "https://actions.google.com/sounds/v1/alarms/beep_short.ogg";
        for (var i = 0; i < 4; i++) {{
            var audio = new Audio(url_som);
            audio.play();
        }}
    </script>
    """
    components.html(codigo_js, height=0, width=0)

# 8. Refresh
time.sleep(1)
st.rerun()
