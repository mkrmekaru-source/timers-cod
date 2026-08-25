import streamlit as st
import time
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="Timers COD", layout="wide")

# 2. CACHE PERSISTENTE V4 (Guarda os tempos finais e as durações customizadas no servidor)
@st.cache_resource
def get_global_data():
    return {
        "timers": {},
        "horas": {f"MKR {i}": 3 for i in range(2, 12)} # Padrão inicial: 3 horas para todos
    }

dados_globais = get_global_data()
global_timers = dados_globais["timers"]
config_horas = dados_globais["horas"]

# 3. Função de Tempo (Horário de Brasília)
def agora_br():
    return datetime.utcnow() - timedelta(hours=3)

# 4. CSS
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #0e1117; color: #ffffff; }
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    
    .timer-card {
        background-color: #161b22;
        padding: 20px 15px 85px 15px;
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
    
    .account-label { font-size: 18px; font-weight: bold; color: #8b949e; margin-bottom: 2px; }
    .cycle-label { font-size: 14px; color: #8b949e; margin-bottom: 2px; }
    .end-time-label { font-size: 13px; color: #58a6ff; margin-bottom: 8px; font-style: italic; }
    
    .timer-text { 
        font-size: 54px; 
        font-weight: bold; 
        margin: 10px 0; 
        font-family: 'Courier New', Courier, monospace; 
    }
    
    [data-testid="stButton"] {
        margin-top: -75px !important;
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

    .logo-spacer { margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 5. Logo e Cabeçalho
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    st.image("1679019533_0X730X6C0X6F0X67.png", use_container_width=True)

st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

# 6. PAINEL DE CONFIGURAÇÃO DE HORAS NO SITE
with st.expander("⚙️ Configurar Horas dos Ciclos (Clique para abrir/fechar)"):
    st.write("Ajuste quantas horas cada fazendeiro vai durar antes de dar o alarme:")
    
    # Criamos colunas dentro do painel para organizar os seletores
    cols_config = st.columns(5)
    for i in range(2, 12):
        id_conta = f"MKR {i}"
        with cols_config[(i - 2) % 5]:
            # Seletor de horas direto na tela
            config_horas[id_conta] = st.number_input(
                f"Fazendeiro MKR {i}", 
                min_value=1, 
                max_value=12, 
                value=config_horas.get(id_conta, 3), 
                step=1,
                key=f"cfg_{id_conta}"
            )

st.markdown("<hr style='border: 0.5px solid #30363d; margin-bottom: 30px;'>", unsafe_allow_html=True)

# 7. Lista de Contas baseada na configuração dinâmica do site
contas = []
for i in range(2, 12):
    id_conta = f"MKR {i}"
    horas = config_horas[id_conta]
    label = f"{horas}h 00m"
    contas.append({
        "id": id_conta, 
        "nome": f"Fazendeiro {id_conta}", 
        "duracao_seg": horas * 3600, 
        "label": label
    })

if 'beep_played' not in st.session_state:
    st.session_state.beep_played = {c["id"]: False for c in contas}

tocar_bip = False

# 8. Layout 5 colunas para os Timers
cols = st.columns(5)

for idx, conta in enumerate(contas):
    id_conta = conta["id"]
    
    with cols[idx % 5]:
        texto_timer = "00:00:00"
        texto_termino = "Termina às: --:--" 
        cor_timer = "#484f58"
        card_class = "timer-card"
        
        if id_conta in global_timers:
            tempo_fim = global_timers[id_conta]
            restante = tempo_fim - agora_br()
            segundos_restantes = restante.total_seconds()
            
            if segundos_restantes > 0:
                h, r = divmod(int(segundos_restantes), 3600)
                m, s = divmod(r, 60)
                texto_timer = f"{h:02d}:{m:02d}:{s:02d}"
                texto_termino = f"Termina às: {tempo_fim.strftime('%H:%M')}"
                
                # LÓGICA DE CORES DINÂMICA (Metade do tempo laranja, Menos de 1h vermelho)
                duracao_total = conta["duracao_seg"]
                if segundos_restantes > (duracao_total / 2):
                    cor_timer = "#58a6ff" # Azul
                elif segundos_restantes > 3600:
                    cor_timer = "#ffa500" # Laranja
                else:
                    cor_timer = "#ff4b4b" # Vermelho
            else:
                texto_timer = "PRONTO!"
                texto_termino = "Termina às: AGORA"
                cor_timer = "#3fb950" 
                card_class = "timer-card timer-ready" 
                
                if not st.session_state.beep_played.get(id_conta, False):
                    tocar_bip = True
                    st.session_state.beep_played[id_conta] = True
        
        st.markdown(f"""
            <div class="{card_class}">
                <div class="account-label">{conta["nome"]}</div>
                <div class="cycle-label">Ciclo: {conta["label"]}</div>
                <div class="end-time-label">{texto_termino}</div>
                <div class="timer-text" style="color: {cor_timer};">{texto_timer}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Iniciar {id_conta}", key=f"btn_{id_conta}", use_container_width=True):
            global_timers[id_conta] = agora_br() + timedelta(seconds=conta["duracao_seg"])
            st.session_state.beep_played[id_conta] = False
            st.rerun()

# 9. Sistema de Áudio (JavaScript)
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

# 10. Refresh
time.sleep(1)
st.rerun()
