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

# Itens adicionados (Agora guardamos apenas o nome, para buscar o preço atualizado na tabela)
if 'propriedades_item' not in st.session_state:
    st.session_state.propriedades_item = []

# Constantes da Fórmula
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
    "Alta Magia (High Magic) - x1.0": 1.0,
    "Fantasia Padrão (Mídia) - x2.0": 2.0,
    "Baixa Magia (Low Magic) - x4.0": 4.0
}
mundo_selecionado = st.sidebar.radio(
    "Nível de Magia da Campanha:",
    list(mundo_opcoes.keys()),
    index=1
)
mod_mundo = mundo_opcoes[mundo_selecionado]

st.sidebar.markdown("---")
st.sidebar.caption("O cálculo se atualiza automaticamente com o ambiente.")

# ==========================================
# 3. ABAS PRINCIPAIS
# ==========================================
aba1, aba2, aba3 = st.tabs(["⚒️ Forja de Itens", "📚 Tabela de Pontos", "⚙️ Fórmula & Configs"])

# --- ABA 1: CALCULADORA PRINCIPAL ---
with aba1:
    st.header("Forja de Itens Mágicos")
    
    # CONTAINER MÁGICO DO TOPO (Reservando espaço para o Preço Final)
    # Tudo escrito aqui dentro só será renderizado no final do código desta aba.
    container_resumo = st.empty() 
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # SEÇÃO DO MEIO: Modificadores A e C
    # ----------------------------------------------------
    col_a, col_c = st.columns(2)
    with col_a:
        st.subheader("Modificador A (Sintonização)")
        req_sint = st.radio("O item exige sintonização?", ["Não (x1.0)", "Sim (x0.75)", "Amaldiçoado (x0.5)"], index=0, horizontal=True)
        if "Não" in req_sint: mod_a = 1.0
        elif "Sim" in req_sint: mod_a = 0.75
        else: mod_a = 0.5

    with col_c:
        st.subheader("Modificador C (Consumo)")
        tipo_consumo = st.radio("Frequência de Uso:", ["Permanente/Ilimitado (x1.0)", "Cargas Diárias (x0.9)", "Consumível (x0.1)"], index=0, horizontal=True)
        if "Permanente" in tipo_consumo: mod_c = 1.0
        elif "Cargas" in tipo_consumo: mod_c = 0.9
        else: mod_c = 0.1
        
        disruptivo = st.checkbox("⚠️ Item Disruptivo (Ignora consumo, dobra preço base)")
        if disruptivo: mod_c = 1.0

    st.markdown("---")
    
    # ----------------------------------------------------
    # SEÇÃO INFERIOR: Adição e Lista de Propriedades
    # ----------------------------------------------------
    st.subheader("Propriedades do Item")
    
    # Alinhamento perfeito do botão com a caixa de texto usando vertical_alignment
    col_sel, col_btn = st.columns([4, 1], vertical_alignment="bottom")
    with col_sel:
        opcoes_lista = st.session_state.tabela_regras["Propriedade Mágica"].tolist()
        prop_selecionada = st.selectbox("Selecione um poder para adicionar à forja:", opcoes_lista)
    with col_btn:
        if st.button("➕ Adicionar Poder", use_container_width=True):
            st.session_state.propriedades_item.append({
                "id": str(uuid.uuid4()), 
                "nome": prop_selecionada,
                "multiplicador": 1 # Valor default
            })
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    pontos_totais = 0
    
    # Renderiza os itens adicionados lendo os valores atualizados da Tabela
    if not st.session_state.propriedades_item:
        st.info("Nenhuma propriedade adicionada ainda. Use a caixa acima para começar.")
    else:
        for index, item in enumerate(st.session_state.propriedades_item):
            # Busca o custo e tipo sempre na tabela atualizada (Reatividade Total!)
            linha_atual = st.session_state.tabela_regras[st.session_state.tabela_regras["Propriedade Mágica"] == item["nome"]]
            
            if linha_atual.empty:
                st.error(f"Propriedade '{item['nome']}' foi removida da tabela principal.")
                continue
                
            custo_base = float(linha_atual.iloc[0]["Custo (P)"])
            tipo_prop = str(linha_atual.iloc[0]["Tipo"])
            
            # Layout da linha de propriedade
            c1, c2, c3, c4 = st.columns([4, 2, 2, 1], vertical_alignment="center")
            with c1:
                st.markdown(f"**{item['nome']}**")
                st.caption(f"Custo Base: {int(custo_base)} pts")
            
            with c2:
                # LÓGICA DE TEXTO INTELIGENTE (Dynamic Labels)
                if "Por +1" in tipo_prop: label_texto = "Valor do modificador"
                elif "Por Dado" in tipo_prop: label_texto = "Quantidade de dados"
                elif "Por Nível" in tipo_prop: label_texto = "Nível"
                else: label_texto = "Quantidade"

                if "Multiplicador" in tipo_prop:
                    item["multiplicador"] = st.number_input(
                        label_texto, 
                        min_value=1, value=item["multiplicador"], 
                        key=f"mult_{item['id']}"
                    )
                else:
                    st.write("*(Custo Fixo)*")
                    item["multiplicador"] = 1
            
            pontos_calc = custo_base * item["multiplicador"]
            pontos_totais += pontos_calc
            
            with c3:
                st.markdown(f"<h4 style='text-align: center; color: #ff4b4b; margin: 0;'>{int(pontos_calc)} pts</h4>", unsafe_allow_html=True)
            with c4:
                if st.button("🗑️", key=f"del_{item['id']}", help="Remover propriedade"):
                    st.session_state.propriedades_item.pop(index)
                    st.rerun()

    # ----------------------------------------------------
    # CÁLCULO FINAL E RENDERIZAÇÃO NO TOPO
    # ----------------------------------------------------
    preco_base = (pontos_totais ** st.session_state.const_exp) * mod_a * mod_c * mod_mundo * st.session_state.const_base
    if disruptivo: preco_base *= 2
    preco_final = int(preco_base)
    
    # Preenchemos a "caixa vazia" que criamos lá em cima!
    with container_resumo.container():
        st.markdown("## 💰 Valor de Mercado")
        st.info(f"**Matemática:** {pontos_totais} Pontos de Poder × [A({mod_a}) × C({mod_c}) × Mundo({mod_mundo})]")
        st.markdown(f"<h1 style='text-align: center; color: gold; font-size: 55px; margin-top: 0;'>{preco_final:,} PO</h1>".replace(',', '.'), unsafe_allow_html=True)

# --- ABA 2: TABELA DE REGRAS ---
with aba2:
    st.header("Biblioteca de Poderes")
    st.write("Edite os valores livremente. Qualquer alteração aqui refletirá instantaneamente nos itens que já estão na sua Forja!")
    
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
            ),
            "Custo (P)": st.column_config.NumberColumn(
                "Custo em Pontos (P)",
                min_value=1,
                required=True
            )
        },
        key="editor_tabela" # Chave nativa garante a reatividade
    )
    st.session_state.tabela_regras = df_editado

# --- ABA 3: FÓRMULA & CONFIGS ---
with aba3:
    st.header("Matemática do Sistema")
    st.latex(r"Custo = \left( \sum P \right)^{Exponente} \times A \times C \times M \times Base")
    st.write("- **P:** Soma dos Pontos das Propriedades Mágicas")
    st.write("- **A:** Modificador de Sintonização")
    st.write("- **C:** Modificador de Consumo")
    st.write("- **M:** Modificador do Mundo (Lateral)")
    
    st.markdown("---")
    st.subheader("Ajustar Constantes do Universo")
    st.write("Altere a economia global do seu jogo aqui. Afeta tudo instantaneamente.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.const_base = st.number_input(
            "Constante Base (Ouro):", 
            value=st.session_state.const_base, 
            help="Aumente para inflacionar a economia (ex: peças de platina), diminua para deflacionar."
        )
    with col_c2:
        st.session_state.const_exp = st.number_input(
            "Constante Exponencial (Escala de Poder):", 
            value=st.session_state.const_exp, 
            min_value=1.0, max_value=2.5, step=0.1,
            help="CUIDADO! Limite máximo de 2.5."
        )