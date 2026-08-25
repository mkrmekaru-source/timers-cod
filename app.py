import streamlit as st
import time
from datetime import datetime, timedelta
import streamlit.components.v1 as components

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

# 3. CSS PROFISSIONAL (Padroniza todos os botões no tema escuro)
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #0e1117; color: #ffffff; }
    .block-container { padding-top: 0rem; padding-bottom: 3rem; }
    
    /* Padroniza todos os botões do app com visual escuro profissional */
    .stButton > button { 
        background-color: #21262d !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        height: 40px !important;
        font-size: 14px !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
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
            minutos = int(conta["minutos"])
            
            h_ciclo, m_ciclo = divmod(minutos, 60)
            label_ciclo = f"{h_ciclo}h {m_ciclo:02d}m"
            
            with cols[idx % 5]:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size: 16px; font-weight: bold; color: #8b949e; text-align: center;'>{nome_conta}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 13px; color: #8b949e; text-align: center; margin-bottom: 2px;'>Ciclo: {label_ciclo}</div>", unsafe_allow_html=True)
                    
                    texto_timer = "00:00:00"
                    texto_termino = "Termina às: --:--" 
                    cor_timer = "#484f58"
                    
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
                                cor_timer = "#58a6ff" # Azul
                            elif segundos_restantes > 3600:
                                cor_timer = "#ffa500" # Laranja
                            else:
                                cor_timer = "#ff4b4b" # Vermelho
                        else:
                            texto_timer = "PRONTO!"
                            texto_termino = "Termina às: AGORA"
                            cor_timer = "#3fb950" # Verde
                            
                            if not st.session_state.beep_played.get(id_conta, False):
                                st.session_state.beep_played[id_conta] = True
                    
                    st.markdown(f"<div style='font-size: 12px; color: #58a6ff; font-style: italic; text-align: center; margin-bottom: 5px;'>{texto_termino}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 42px; font-weight: bold; font-family: monospace; text-align: center; color: {cor_timer}; margin: 10px 0;'>{texto_timer}</div>", unsafe_allow_html=True)
                    
                    if st.button(f"Iniciar", key=f"btn_{id_conta}", use_container_width=True):
                        st.session_state.global_timers[id_conta] = agora_br() + timedelta(minutes=minutos)
                        st.session_state.beep_played[id_conta] = False
                        st.rerun()
    else:
        st.info("Nenhum cronômetro cadastrado. Adicione um abaixo!")

render_timer_grid()

# ==========================================
# 6. PAINEL DE CONFIGURAÇÃO (Centralizado e Compacto)
# ==========================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

col_l, col_center, col_r = st.columns([1, 2.2, 1])

with col_center:
    st.subheader("⚙️ Adicionar Novo Cronômetro")
    
    with st.container(border=True):
        with st.form("form_adicionar", clear_on_submit=True):
            col_a1, col_a2 = st.columns([2, 1])
            with col_a1:
                novo_nome = st.text_input("Nome do Fazendeiro", placeholder="Ex: MKR 12")
            with col_a2:
                novos_minutos = st.number_input("Minutos", min_value=1, max_value=1440, value=180, step=1)
                
            btn_adicionar = st.form_submit_button("➕ Adicionar", use_container_width=True)
            if btn_adicionar:
                if novo_nome.strip():
                    novo_id = f"custom_{time.time()}"
                    st.session_state.lista_contas.append({
                        "id": novo_id,
                        "nome": novo_nome.strip(),
                        "minutos": int(novos_minutos)
                    })
                    st.success(f"'{novo_nome}' adicionado!")
                    st.rerun()
                else:
                    st.error("Digite um nome válido.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("✏️ Gerenciar / Deletar Existentes")

    with st.container(border=True):
        for idx, conta in enumerate(list(st.session_state.lista_contas)):
            id_c = conta["id"]
            
            c_nome, c_min, c_salvar, c_del = st.columns([3, 2, 1.2, 1.2])
            
            with c_nome:
                novo_nome_val = st.text_input("Nome", value=conta["nome"], key=f"edit_nome_{id_c}", label_visibility="collapsed")
            with c_min:
                novo_min_val = st.number_input("Min", min_value=1, max_value=1440, value=int(conta["minutos"]), step=1, key=f"edit_min_{id_c}", label_visibility="collapsed")
            with c_salvar:
                if st.button("💾", key=f"save_{id_c}", help="Salvar alterações", use_container_width=True):
                    conta["nome"] = novo_nome_val
                    conta["minutos"] = int(novo_min_val)
                    st.success("Salvo!")
                    st.rerun()
            with c_del:
                if st.button("🗑️", key=f"del_{id_c}", help="Deletar este cronômetro", use_container_width=True):
                    st.session_state.lista_contas = [c for c in st.session_state.lista_contas if c["id"] != id_c]
                    if id_c in st.session_state.global_timers:
                        del st.session_state.global_timers[id_c]
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
