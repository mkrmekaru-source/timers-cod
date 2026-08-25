import streamlit as st
import time
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_config(page_title="Timers COD", layout="wide")

# 2. CACHE PERSISTENTE V9 (Estrutura limpa e organizada)
@st.cache_resource
def get_global_data_v9():
    contas_iniciais = []
    for i in range(2, 12):
        contas_iniciais.append({
            "id": f"mkr_{i}",
            "nome": f"Fazendeiro MKR {i}",
            "minutos": 180
        })
    return {
        "timers": {},
        "contas": contas_iniciais
    }

dados_globais = get_global_data_v9()
global_timers = dados_globais.setdefault("timers", {})
lista_contas = dados_globais.setdefault("contas", [])

# 3. Função de Tempo (Horário de Brasília)
def agora_br():
    return datetime.utcnow() - timedelta(hours=3)

# 4. CSS Customizado para ajustar detalhes visuais e deixar a lixeira compacta
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #0e1117; color: #ffffff; }
    .block-container { padding-top: 0rem; padding-bottom: 2rem; }
    
    /* Estilo sutil para o botão de deletar dentro do card */
    div[data-testid="column"] button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        color: #8b949e !important;
        font-size: 14px !important;
        padding: 0px !important;
        min-height: 24px !important;
        height: 24px !important;
        width: 24px !important;
        box-shadow: none !important;
    }
    div[data-testid="column"] button[kind="secondary"]:hover {
        color: #ff4b4b !important;
        background-color: rgba(255, 75, 75, 0.1) !important;
        border-radius: 4px !important;
    }

    .logo-spacer { margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 5. Logo e Cabeçalho
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    st.image("1679019533_0X730X6C0X6F0X67.png", use_container_width=True)

st.markdown('<div class="logo-spacer"></div>', unsafe_allow_html=True)

if 'beep_played' not in st.session_state:
    st.session_state.beep_played = {}

tocar_bip = False

# 6. Layout Dinâmico em 5 colunas para os Timers Atuais
if len(lista_contas) > 0:
    cols = st.columns(5)
    for idx, conta in enumerate(lista_contas):
        id_conta = conta["id"]
        nome_conta = conta["nome"]
        minutos = conta["minutos"]
        
        h_ciclo, m_ciclo = divmod(minutos, 60)
        label_ciclo = f"{h_ciclo}h {m_ciclo:02d}m"
        
        with cols[idx % 5]:
            # Usando container nativo com borda para manter tudo perfeitamente alinhado na caixa
            with st.container(border=True):
                # Cabeçalho do Card: Nome e Lixeira vermelha compacta
                c_tit, c_del = st.columns([5, 1])
                with c_tit:
                    st.markdown(f"**{nome_conta}**")
                with c_del:
                    if st.button("🗑️", key=f"card_del_{id_conta}", help="Deletar este cronômetro"):
                        lista_contas.remove(conta)
                        if id_conta in global_timers:
                            del global_timers[id_conta]
                        st.rerun()
                
                st.markdown(f"<div style='font-size: 13px; color: #8b949e;'>Ciclo: {label_ciclo}</div>", unsafe_allow_html=True)
                
                texto_timer = "00:00:00"
                texto_termino = "Termina às: --:--" 
                cor_timer = "#484f58"
                
                if id_conta in global_timers:
                    tempo_fim = global_timers[id_conta]
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
                            tocar_bip = True
                            st.session_state.beep_played[id_conta] = True
                
                st.markdown(f"<div style='font-size: 13px; color: #58a6ff; font-style: italic; margin-bottom: 5px;'>{texto_termino}</div>", unsafe_allow_html=True)
                
                # Cronômetro Grande Centralizado
                st.markdown(f"<div style='font-size: 42px; font-weight: bold; font-family: monospace; text-align: center; color: {cor_timer}; margin: 10px 0;'>{texto_timer}</div>", unsafe_allow_html=True)
                
                # Botão Iniciar dentro do card
                if st.button(f"Iniciar", key=f"btn_{id_conta}", use_container_width=True):
                    global_timers[id_conta] = agora_br() + timedelta(minutes=minutos)
                    st.session_state.beep_played[id_conta] = False
                    st.rerun()
else:
    st.info("Nenhum cronômetro cadastrado. Adicione um abaixo!")

# ==========================================
# 7. PAINEL DE CONFIGURAÇÃO NA PARTE DE BAIXO
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
        st.write("")
        btn_adicionar = st.form_submit_button("➕ Adicionar")
        
    if btn_adicionar:
        if novo_nome.strip():
            novo_id = f"custom_{time.time()}"
            lista_contas.append({
                "id": novo_id,
                "nome": novo_nome.strip(),
                "minutos": int(novos_minutos)
            })
            st.success(f"'{novo_nome}' adicionado com sucesso!")
            st.rerun()
        else:
            st.error("Digite um nome válido.")

st.markdown("---")
st.subheader("✏️ Editar Cronômetros Existentes")

for idx, conta in enumerate(list(lista_contas)):
    id_c = conta["id"]
    col_e1, col_e2, col_e3, col_e4 = st.columns([3, 2, 1, 1])
    
    with col_e1:
        novo_nome_val = st.text_input("Nome", value=conta["nome"], key=f"edit_nome_{id_c}", label_visibility="collapsed")
    with col_e2:
        novo_min_val = st.number_input("Minutos", min_value=1, max_value=1440, value=conta["minutos"], step=1, key=f"edit_min_{id_c}", label_visibility="collapsed")
    with col_e3:
        if st.button("💾 Salvar", key=f"save_{id_c}", use_container_width=True):
            conta["nome"] = novo_nome_val
            conta["minutos"] = int(novo_min_val)
            st.success("Atualizado!")
            st.rerun()
    with col_e4:
        if st.button("🗑️ Deletar", key=f"del_{id_c}", use_container_width=True):
            lista_contas.remove(conta)
            if id_c in global_timers:
                del global_timers[id_c]
            st.warning("Removido.")
            st.rerun()

# 8. Sistema de Áudio (JavaScript)
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

# 9. Refresh
time.sleep(1)
st.rerun()
