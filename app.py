import streamlit as st
import time
from datetime import datetime, timedelta

# 1. Configuração da Página
st.set_page_config(page_title="Timers COD", layout="wide")

# 2. ESTADO GLOBAL NA SESSÃO
if "global_timers" not in st.session_state:
    st.session_state.global_timers = {}

if "lista_contas" not in st.session_state:
    contas_iniciais = []
    for i in range(2, 12):
        contas_iniciais.append({
            "id": f"mkr_{i}",
            "nome": f"Fazendeiro MKR {i}",
            "minutos": 180
        })
    st.session_state.lista_contas = contas_iniciais

# Função de Tempo (Horário de Brasília)
def agora_br():
    return datetime.utcnow() - timedelta(hours=3)

# 3. CSS ORGANIZADO (Com escopo isolado para não afetar os botões de baixo)
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #0e1117; color: #ffffff; }
    .block-container { padding-top: 0rem; padding-bottom: 3rem; }
    
    .timer-card {
        background-color: #161b22;
        padding: 20px 15px 85px 15px;
        border-radius: 12px;
        border: 1px solid #30363d;
        text-align: center;
        transition: 0.3s;
        margin-bottom: 20px;
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
    
    /* ESTILO APLICADO APENAS AOS BOTÕES DO TOPO (Dentro dos cards) */
    .timer-btn-wrapper [data-testid="stButton"] {
        margin-top: -75px !important;
        padding: 0 15% !important;
        position: relative;
        z-index: 10;
        display: flex;
        justify-content: center;
    }

    .timer-btn-wrapper [data-testid="stButton"] button { 
        background-color: #21262d !important;
        color: white !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        height: 40px !important;
        font-size: 14px !important;
        width: 100% !important;
    }
    
    .timer-btn-wrapper [data-testid="stButton"] button:hover {
        border-color: #58a6ff !important;
        color: #58a6ff !important;
        background-color: #30363d !important;
    }

    .logo-spacer { margin-bottom: 40px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Logo e Cabeçalho
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    st.image("1679019533_0X730X6C0X6F0X67.png", use_container_width=True)

st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

if 'beep_played' not in st.session_state:
    st.session_state.beep_played = {}

tocar_bip = False

# 5. FRAGMENTO DOS TIMERS
@st.fragment(run_every=1)
def render_timer_grid():
    if len(st.session_state.lista_contas) > 0:
        cols = st.columns(5)
        for idx, conta in enumerate(st.session_state.lista_contas):
            id_conta = conta["id"]
            nome_conta = conta["nome"]
            minutos = conta["minutos"]
            
            h_ciclo, m_ciclo = divmod(minutos, 60)
            label_ciclo = f"{h_ciclo}h {m_ciclo:02d}m"
            
            with cols[idx % 5]:
                texto_timer = "00:00:00"
                texto_termino = "Termina às: --:--" 
                cor_timer = "#484f58"
                card_class = "timer-card"
                
                if id_conta in st.session_state.global_timers:
                    tempo_fim = st.session_state.global_timers[id_conta]
                    restante = tempo_fim - agora_br()
                    segundos_restantes = restante.total_seconds()
                    
                    duracao_seg = minutos * 60
                    if segundos_restantes > 0:
                        h, r = divmod(int(segundos_restantes), 3600)
                        m, s = divmod(r, 60)
                        texto_timer = f"{h:02d}:{m:02d}:{s:02d}"
                        texto_termino = f"Termina às: {tempo_fim.strftime('%H:%M')}"
                        
                        if segundos_restantes > (duracao_seg / 2):
                            cor_timer = "#58a6ff" 
                        elif segundos_restantes > 3600:
                            cor_timer = "#ffa500" 
                        else:
                            cor_timer = "#ff4b4b" 
                    else:
                        texto_timer = "PRONTO!"
                        texto_termino = "Termina às: AGORA"
                        cor_timer = "#3fb950" 
                        card_class = "timer-card timer-ready" 
                        
                        if not st.session_state.beep_played.get(id_conta, False):
                            st.session_state.beep_played[id_conta] = True
                
                st.markdown(f"""
                    <div class="{card_class}">
                        <div class="account-label">{nome_conta}</div>
                        <div class="cycle-label">Ciclo: {label_ciclo}</div>
                        <div class="end-time-label">{texto_termino}</div>
                        <div class="timer-text" style="color: {cor_timer};">{texto_timer}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="timer-btn-wrapper">', unsafe_allow_html=True)
                if st.button(f"Iniciar {nome_conta}", key=f"btn_{id_conta}", use_container_width=True):
                    st.session_state.global_timers[id_conta] = agora_br() + timedelta(minutes=minutos)
                    st.session_state.beep_played[id_conta] = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum cronômetro cadastrado. Adicione um abaixo!")

render_timer_grid()

# ==========================================
# 6. PAINEL DE CONFIGURAÇÃO (Alinhado à Esquerda)
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("⚙️ Adicionar Novo Cronômetro")

with st.form("form_adicionar", clear_on_submit=True):
    col_add1, col_add2, col_add3 = st.columns([2, 2, 1])
    with col_add1:
        novo_nome = st.text_input("Nome do Personagem / Fazendeiro", placeholder="Ex: Fazendeiro MKR 12")
    with col_add2:
         novos_minutos = st.number_input("Duração em Minutos", min_value=1, max_value=1440, value=180, step=1)
    with col_add3:
        st.write("")
        btn_adicionar = st.form_submit_button("➕ Adicionar", use_container_width=True)
        
    if btn_adicionar:
        if novo_nome.strip():
            novo_id = f"custom_{time.time()}"
            st.session_state.lista_contas.append({
                "id": novo_id,
                "nome": novo_nome.strip(),
                "minutos": int(novos_minutos)
            })
            st.success(f"'{novo_nome}' adicionado com sucesso!")
            st.rerun()
        else:
            st.error("Digite um nome válido.")

st.markdown("---")
st.subheader("✏️ Gerenciar e Deletar Cronômetros Existentes")

for idx, conta in enumerate(list(st.session_state.lista_contas)):
    id_c = conta["id"]
    # Ordem exata nas colunas: [Salvar] [Deletar] [Nome] [Minutos]
    col_e1, col_e2, col_e3, col_e4 = st.columns([1, 1, 3, 2])
    
    with col_e1:
        btn_salvar = st.button("💾 Salvar", key=f"save_{id_c}", use_container_width=True)
    with col_e2:
        btn_deletar = st.button("🗑️ Deletar", key=f"del_{id_c}", use_container_width=True)
    with col_e3:
        novo_nome_val = st.text_input("Nome", value=conta["nome"], key=f"edit_nome_{id_c}", label_visibility="collapsed")
    with col_e4:
        novo_min_val = st.number_input("Minutos", min_value=1, max_value=1440, value=conta["minutos"], step=1, key=f"edit_min_{id_c}", label_visibility="collapsed")
        
    if btn_salvar:
        conta["nome"] = novo_nome_val
        conta["minutos"] = int(novo_min_val)
        st.success("Atualizado!")
        st.rerun()
        
    if btn_deletar:
        st.session_state.lista_contas = [c for c in st.session_state.lista_contas if c["id"] != id_c]
        if id_c in st.session_state.global_timers:
            del st.session_state.global_timers[id_c]
        st.rerun()
