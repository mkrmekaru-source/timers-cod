import streamlit as st
import time
from datetime import datetime, timedelta
import streamlit.components.v1 as components

# 1. Configuração da Página
st.set_page_configDá para resolver os dois pontos de forma simples e deixar o visual muito mais profissional:

---

### 1. Como separar a tela de Cronômetros da Edição

A melhor forma no **Streamlit** para não poluir a tela principal é usar **Abas (`st.tabs`)** ou um **Menu Retrátil (`st.expander`)**:

* **Opção Recomendada (Abas):** Cria uma visualização limpa só para monitorar os tempos e outra exclusiva para gerenciar/adicionar contas.

```python
# Criando as abas principais
tab_painel, tab_config = st.tabs(
    ["⏱️ Painel de Cronômetros", "⚙️ Gerenciar Fazendeiros"]
)

with tab_painel:
  # Aqui fica todo o seu código do grid de cronômetros (cards com as contas)
  pass

with tab_config:
  # Aqui fica a parte de Adicionar e Gerenciar/Deletar
  pass
