import streamlit as st
import pandas as pd
import uuid

# ==========================================
# 1. CONFIGURAÇÃO INICIAL E ESTADO DA SESSÃO
# ==========================================
st.set_page_config(page_title="PPA - Precificador Arcano", page_icon="🎲", layout="wide")

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

if 'propriedades_item' not in st.session_state:
    st.session_state.propriedades_item = []

if 'const_base' not in st.session_state: st.session_state.const_base = 50.0
if 'const_exp' not in st.session_state: st.session_state.const_exp = 1.5

if 'mundo_sel' not in st.session_state: st.session_state.mundo_sel = "Fantasia Padrão (Mídia) - x2.0"
if 'req_sint' not in st.session_state: st.session_state.req_sint = "Não (x1.0)"
if 'tipo_consumo' not in st.session_state: st.session_state.tipo_consumo = "Permanente/Ilimitado (x1.0)"
if 'disruptivo' not in st.session_state: st.session_state.disruptivo = False

# ==========================================
# CALLBACKS (Ações rápidas de interface)
# ==========================================
def adicionar_poder(nome_poder):
    st.session_state.propriedades_item.append({"id": str(uuid.uuid4()), "nome": nome_poder})

def remover_poder(index):
    st.session_state.propriedades_item.pop(index)

# ==========================================
# 2. MENU LATERAL
# ==========================================
st.sidebar.title("🎲 Grimório PPA")
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Configuração do Mundo")

mundo_opcoes = {
    "Alta Magia (High Magic)": 1.0,
    "Fantasia Padrão (Mídia)": 2.0,
    "Baixa Magia (Low Magic)": 4.0
}
st.sidebar.radio("Nível de Magia da Campanha:", list(mundo_opcoes.keys()), key="mundo_sel")

st.sidebar.markdown("---")
st.sidebar.caption("Cálculo 100% reativo ao ambiente.")

# ==========================================
# 3. ABAS PRINCIPAIS
# ==========================================
aba1, aba2, aba3 = st.tabs(["⚒️ Forja de Itens", "📚 Tabela de Pontos", "⚙️ Fórmula & Configs"])

with aba1:
    st.header("Forja de Itens Mágicos")
    
    # ----------------------------------------------------
    # MATEMÁTICA ARCANA (Calculada invisível antes de desenhar)
    # ----------------------------------------------------
    mod_mundo = mundo_opcoes[st.session_state.mundo_sel]
    
    if "Não" in st.session_state.req_sint: mod_a = 1.0
    elif "Sim" in st.session_state.req_sint: mod_a = 0.75
    else: mod_a = 0.5
    
    if "Permanente" in st.session_state.tipo_consumo: mod_c = 1.0
    elif "Cargas" in st.session_state.tipo_consumo: mod_c = 0.9
    else: mod_c = 0.1
    
    if st.session_state.disruptivo: mod_c = 1.0
    
    mod_total = mod_a * mod_c * mod_mundo
    if st.session_state.disruptivo: mod_total *= 2 
    
    pontos_totais = 0
    for item in st.session_state.propriedades_item:
        linha_atual = st.session_state.tabela_regras[st.session_state.tabela_regras["Propriedade Mágica"] == item["nome"]]
        if not linha_atual.empty:
            custo_base = float(linha_atual.iloc[0]["Custo (P)"])
            mult = st.session_state.get(f"mult_{item['id']}", 1)
            pontos_totais += custo_base * mult
            
    preco_base = (pontos_totais ** st.session_state.const_exp) * mod_total * st.session_state.const_base
    preco_final = int(preco_base)

    # ----------------------------------------------------
    # RENDERIZAÇÃO LINEAR DA INTERFACE
    # ----------------------------------------------------
    st.markdown("## 💰 Valor de Mercado")
    
    st.info(f"**Ponto:** {int(pontos_totais)} Pontos de Poder\n\n**Multiplicador:** {mod_total}")
    st.markdown(f"<h1 style='text-align: center; color: gold; font-size: 55px; margin-top: 0;'>{preco_final:,} PO</h1>".replace(',', '.'), unsafe_allow_html=True)
    st.markdown("---")
    
    col_a, col_c = st.columns(2)
    with col_a:
        st.subheader("Modificador A (Sintonização)")
        st.radio("Exige sintonização?", ["Não (x1.0)", "Sim (x0.75)", "Amaldiçoado (x0.5)"], key="req_sint", horizontal=True)

    with col_c:
        st.subheader("Modificador C (Consumo)")
        st.radio("Frequência de Uso:", ["Permanente/Ilimitado (x1.0)", "Cargas Diárias (x0.9)", "Consumível (x0.1)"], key="tipo_consumo", horizontal=True)
        st.checkbox("⚠️ Item Disruptivo (Ignora consumo, dobra multiplicador)", key="disruptivo")

    st.markdown("---")
    st.subheader("Propriedades do Item")
    
    col_sel, col_btn = st.columns([4, 1], vertical_alignment="bottom")
    with col_sel:
        opcoes_lista = st.session_state.tabela_regras["Propriedade Mágica"].tolist()
        prop_selecionada = st.selectbox("Selecione um poder:", opcoes_lista)
    with col_btn:
        st.button("➕ Adicionar", on_click=adicionar_poder, args=(prop_selecionada,), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.propriedades_item:
        st.info("Nenhuma propriedade adicionada ainda.")
    else:
        for index, item in enumerate(st.session_state.propriedades_item):
            linha_atual = st.session_state.tabela_regras[st.session_state.tabela_regras["Propriedade Mágica"] == item["nome"]]
            if linha_atual.empty: continue
                
            custo_base = float(linha_atual.iloc[0]["Custo (P)"])
            tipo_prop = str(linha_atual.iloc[0]["Tipo"])
            
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1], vertical_alignment="center")
            with c1:
                st.markdown(f"**{item['nome']}**")
                st.caption(f"Custo Base: {int(custo_base)} pts")
            
            with c2:
                if "Por +1" in tipo_prop: label_texto = "Valor do modificador"
                elif "Por Dado" in tipo_prop: label_texto = "Quantidade de dados"
                elif "Por Nível" in tipo_prop: label_texto = "Nível"
                else: label_texto = "Quantidade"

                if "Multiplicador" in tipo_prop:
                    st.number_input(label_texto, min_value=1, key=f"mult_{item['id']}")
                else:
                    st.write("*(Custo Fixo)*")
                    st.session_state[f"mult_{item['id']}"] = 1 
            
            pontos_calc = custo_base * st.session_state.get(f"mult_{item['id']}", 1)
            
            with c3:
                st.markdown(f"<h4 style='text-align: center; color: #ff4b4b; margin: 0;'>{int(pontos_calc)} pts</h4>", unsafe_allow_html=True)
            with c4:
                st.button("🗑️", key=f"del_{item['id']}", on_click=remover_poder, args=(index,))

with aba2:
    st.header("Biblioteca de Poderes")
    df_editado = st.data_editor(
        st.session_state.tabela_regras, 
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Tipo": st.column_config.SelectboxColumn("Tipo de Cálculo", options=["Fixo", "Multiplicador (Por +1)", "Multiplicador (Por Dado)", "Multiplicador (Por Nível)"], required=True),
            "Custo (P)": st.column_config.NumberColumn("Custo em Pontos (P)", min_value=1, required=True)
        },
        key="editor_tabela"
    )
    st.session_state.tabela_regras = df_editado

with aba3:
    st.header("Matemática do Sistema")
    st.latex(r"Custo = \left( \sum P \right)^{Exponente} \times A \times C \times M \times Base")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.const_base = st.number_input("Constante Base (Ouro):", value=st.session_state.const_base)
    with col_c2:
        st.session_state.const_exp = st.number_input("Constante Exponencial:", value=st.session_state.const_exp, min_value=1.0, max_value=2.5, step=0.1)