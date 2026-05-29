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
                "tipo": linha["Tipo"],
                "multiplicador": 1 # Valor default do input do usuário
            })
            st.rerun()

    st.markdown("### Propriedades do Item Atual")
    
    pontos_totais = 0
    
    # Renderiza os itens adicionados modularmente
    if not st.session_state.propriedades_item:
        st.info("Nenhuma propriedade adicionada ainda. Use a caixa acima para começar a forjar.")
    else:
        for index, item in enumerate(st.session_state.propriedades_item):
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
            with c1:
                st.markdown(f"**{item['nome']}**")
                st.caption(f"Base: {item['custo_base']} pts | {item['tipo']}")
            with c2:
                if "Multiplicador" in item["tipo"]:
                    item["multiplicador"] = st.number_input(
                        "Quantidade/Nível", 
                        min_value=1, value=item["multiplicador"], 
                        key=f"mult_{item['id']}"
                    )
                else:
                    st.write("*(Custo Fixo)*")
                    item["multiplicador"] = 1
            
            pontos_calc = item["custo_base"] * item["multiplicador"]
            pontos_totais += pontos_calc
            
            with c3:
                st.markdown(f"<h4 style='text-align: center; color: #ff4b4b;'>{pontos_calc} pts</h4>", unsafe_allow_html=True)
            with c4:
                if st.button("🗑️", key=f"del_{item['id']}"):
                    st.session_state.propriedades_item.pop(index)
                    st.rerun()

    st.markdown("---")
    
    # Variáveis A (Sintonização) e C (Consumo)
    col_a, col_c = st.columns(2)
    with col_a:
        st.subheader("Modificador A (Sintonização)")
        req_sint = st.radio("O item exige sintonização?", ["Não (x1.0)", "Sim (x0.75)", "Amaldiçoado (x0.5)"], index=0)
        if "Não" in req_sint: mod_a = 1.0
        elif "Sim" in req_sint: mod_a = 0.75
        else: mod_a = 0.5

    with col_c:
        st.subheader("Modificador C (Consumo)")
        tipo_consumo = st.radio("Frequência de Uso:", ["Permanente/Ilimitado (x1.0)", "Cargas Diárias (x0.9)", "Uso Único/Consumível (x0.1)"], index=0)
        if "Permanente" in tipo_consumo: mod_c = 1.0
        elif "Cargas" in tipo_consumo: mod_c = 0.9
        else: mod_c = 0.1
        
        disruptivo = st.checkbox("⚠️ Item Disruptivo (Ignora consumo, dobra preço)")
        if disruptivo:
            mod_c = 1.0

    # CÁLCULO FINAL
    st.markdown("---")
    st.markdown("## 💰 Resumo Financeiro")
    
    preco_base = (pontos_totais ** st.session_state.const_exp) * mod_a * mod_c * mod_mundo * st.session_state.const_base
    
    if disruptivo:
        preco_base *= 2

    preco_final = int(preco_base) # Arredonda o valor
    
    st.success(f"**Pontuação Total de Poder (P):** {pontos_totais}")
    st.markdown(f"<h1 style='text-align: center; color: gold; font-size: 50px;'>{preco_final:,} PO</h1>".replace(',', '.'), unsafe_allow_html=True)

# --- ABA 2: TABELA DE REGRAS ---
with aba2:
    st.header("Biblioteca de Poderes")
    st.write("Você pode editar os valores clicando nas células, ou adicionar/remover linhas usando a interface abaixo.")
    
    # Data Editor nativo do Streamlit, permite add/delete rows facilmente!
    df_editado = st.data_editor(
        st.session_state.tabela_regras, 
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Tipo": st.column_config.SelectboxColumn(
                "Tipo de Cálculo",
                help="Se é cobrado uma vez ou por quantidade",
                options=["Fixo", "Multiplicador (Por +1)", "Multiplicador (Por Dado)", "Multiplicador (Por Nível)"],
                required=True
            )
        }
    )
    
    # Salva as alterações feitas no editor de volta no session_state
    st.session_state.tabela_regras = df_editado

# --- ABA 3: FÓRMULA & CONFIGS ---
with aba3:
    st.header("Matemática do Sistema")
    st.latex(r"Custo = \left( \sum P \right)^{Exponente} \times A \times C \times M \times Base")
    st.write("- **P:** Soma dos Pontos das Propriedades Mágicas")
    st.write("- **A:** Sintonização | **C:** Consumo | **M:** Modificador do Mundo (Lateral)")
    
    st.markdown("---")
    st.subheader("Ajustar Constantes do Universo")
    
    st.session_state.const_base = st.number_input(
        "Constante Base (Ouro):", 
        value=st.session_state.const_base, 
        help="Aumente para inflacionar a economia, diminua para deflacionar."
    )
    
    st.session_state.const_exp = st.number_input(
        "Constante Exponencial (Escala de Poder):", 
        value=st.session_state.const_exp, 
        min_value=1.0, max_value=2.5, step=0.1,
        help="CUIDADO! Limite máximo de 2.5. Acima disso, os preços explodem matematicamente."
    )