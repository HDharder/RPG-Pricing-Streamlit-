import streamlit as st
import pandas as pd
import uuid

# ==========================================
# 1. CONFIGURAÇÃO INICIAL E ESTADO DA SESSÃO
# ==========================================
st.set_page_config(page_title="PPA - Precificador Arcano", page_icon="🎲", layout="wide")

# Tabela Padrão de Regras
if 'tabela_regras' not in st.session_state:
    st.session_state.tabela_regras = pd.DataFrame([
        {"Propriedade Mágica": "Bônus de Ataque/Dano", "Custo (P)": 3, "Tipo": "Multiplicador (Por +1)", "Exemplo": "Espada +1 (3 pts)"},
        {"Propriedade Mágica": "Dano Extra (Dados)", "Custo (P)": 4, "Tipo": "Multiplicador (Por Dado)", "Exemplo": "Língua de Fogo (+1d6)"},
        {"Propriedade Mágica": "Bônus na CA", "Custo (P)": 5, "Tipo": "Multiplicador (Por +1)", "Exemplo": "Escudo +2 (10 pts)"},
        {"Propriedade Mágica": "Resistência a Dano", "Custo (P)": 10, "Tipo": "Fixo", "Exemplo": "Anel de Resistência a Fogo"},
        {"Propriedade Mágica": "Voo (Ilimitado)", "Custo (P)": 15, "Tipo": "Fixo", "Exemplo": "Botas Aladas"},
        {"Propriedade Mágica": "Magia (Níveis 1 a 3)", "Custo (P)": 2, "Tipo": "Multiplicador (Por Nível)", "Exemplo": "Magia Nv 2 = 4 pts"},
        {"Propriedade Mágica": "Magia (Níveis 4 a 6)", "Custo (P)": 4, "Tipo": "Multiplicador (Por Nível)", "Exemplo": "Magia Nv 5 = 20 pts"},
        {"Propriedade Mágica": "Magia (Níveis 7 a 9)", "Custo (P)": 8, "Tipo": "Multiplicador (Por Nível)", "Exemplo": "Magia Nv 9 = 72 pts"},
    ])

# Itens adicionados na calculadora (Aba 1)
if 'propriedades_item' not in st.session_state:
    st.session_state.propriedades_item = []

# Constantes da Fórmula (Aba 3)
if 'const_base' not in st.session_state:
    st.session_state.const_base = 50.0
if 'const_exp' not in st.session_state:
    st.session_state.const_exp = 1.5

# ==========================================
# 2. MENU LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("🎲 Grimório PPA")
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Configuração do Mundo")

mundo_opcoes = {
    "Alta Magia (High Magic)": 1.0,
    "Fantasia Padrão (Mídia)": 2.0,
    "Baixa Magia (Low Magic)": 4.0
}
mundo_selecionado = st.sidebar.radio(
    "Nível de Magia da Campanha:",
    list(mundo_opcoes.keys()),
    index=1
)
mod_mundo = mundo_opcoes[mundo_selecionado]

st.sidebar.markdown("---")
st.sidebar.caption("Desenvolvido para Mestres de RPG")

# ==========================================
# 3. ABAS PRINCIPAIS
# ==========================================
aba1, aba2, aba3 = st.tabs(["⚒️ Forja de Itens (Principal)", "📚 Tabela de Pontos", "⚙️ Fórmula & Configs"])

# --- ABA 1: CALCULADORA PRINCIPAL ---
with aba1:
    st.header("Forja de Itens Mágicos")
    
    # Seleção de Propriedade
    col_sel, col_btn = st.columns([4, 1])
    with col_sel:
        opcoes_lista = st.session_state.tabela_regras["Propriedade Mágica"].tolist()
        prop_selecionada = st.selectbox("Selecione um poder para adicionar:", opcoes_lista)
    with col_btn:
        st.write("") # Espaçamento
        if st.button("➕ Adicionar", use_container_width=True):
            # Busca as infos na tabela base
            linha = st.session_state.tabela_regras[st.session_state.tabela_regras["Propriedade Mágica"] == prop_selecionada].iloc[0]
            st.session_state.propriedades_item.append({
                "id": str(uuid.uuid4()), # ID único para o Streamlit não bugar os botões
                "nome": linha["Propriedade Mágica"],
                "custo_base": linha["Custo (P)"],
                "tipo": linha