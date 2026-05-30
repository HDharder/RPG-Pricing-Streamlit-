import streamlit as st
import pandas as pd
import uuid
import json

# ==========================================
# 1. CONFIGURAÇÃO INICIAL E ESTADO DA SESSÃO
# ==========================================
st.set_page_config(page_title="PPA - Precificador Arcano", page_icon="🎲", layout="wide")

if 'tabela_regras' not in st.session_state:
    try:
        with open('regras.json', 'r', encoding='utf-8') as f:
            dados_regras = json.load(f)
    except FileNotFoundError:
        # Prevenção de falhas caso a runa falhe ou o arquivo não seja encontrado
        dados_regras = [
            {"Propriedade Mágica": "Bônus de Ataque/Dano", "Custo (P)": 3, "Tipo": "Multiplicador (Por +1)"}
        ]
        
    st.session_state.tabela_regras = pd.DataFrame(dados_regras)
# 2. Carrega os Itens Prontos (Aba 4)
if 'itens_prontos' not in st.session_state:
    try:
        with open('itens.json', 'r', encoding='utf-8') as f:
            st.session_state.itens_prontos = json.load(f)
    except FileNotFoundError:
        st.session_state.itens_prontos = []

# Variáveis globais
if 'propriedades_item' not in st.session_state:
    st.session_state.propriedades_item = []

if 'const_base' not in st.session_state: st.session_state.const_base = 50.0
if 'const_exp' not in st.session_state: st.session_state.const_exp = 1.5

if 'mundo_sel' not in st.session_state: st.session_state.mundo_sel = "Fantasia Padrão (Média) - x2.0"
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

def carregar_item_pronto(item_data):
    """Magia de Injeção: Carrega o item e ensina a tabela caso falte uma regra."""
    # 1. Aplica as variáveis do item
    st.session_state.req_sint = item_data.get("sintonizacao", "Não (x1.0)")
    st.session_state.tipo_consumo = item_data.get("consumo", "Permanente/Ilimitado (x1.0)")
    st.session_state.disruptivo = item_data.get("disruptivo", False)
    
    # 2. Limpa a forja atual
    st.session_state.propriedades_item = []
    
    # 3. Processa cada propriedade do item
    for prop in item_data["propriedades"]:
        nome_prop = prop["Propriedade Mágica"]
        
        # Cria a propriedade na Forja e define o multiplicador (ex: +3)
        novo_id = str(uuid.uuid4())
        st.session_state.propriedades_item.append({"id": novo_id, "nome": nome_prop})
        st.session_state[f"mult_{novo_id}"] = prop.get("multiplicador", 1)
        
        # 4. VERIFICAÇÃO DE DNA: A regra existe na Tabela Principal?
        if nome_prop not in st.session_state.tabela_regras["Propriedade Mágica"].values:
            nova_regra = {
                "Propriedade Mágica": nome_prop,
                "Custo (P)": prop["Custo (P)"],
                "Tipo": prop["Tipo"]
            }
            # Se não existir, injeta a regra na tabela na mesma hora!
            df_nova = pd.DataFrame([nova_regra])
            st.session_state.tabela_regras = pd.concat([st.session_state.tabela_regras, df_nova], ignore_index=True)

# ==========================================
# 2. MENU LATERAL
# ==========================================
st.sidebar.title("🎲 Grimório PPA")
st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Configuração do Mundo")

mundo_opcoes = {
    "Alta Magia (High Magic)": 1.0,
    "Fantasia Padrão (Média)": 2.0,
    "Baixa Magia (Low Magic)": 4.0
}
st.sidebar.radio("Nível de Magia da Campanha:", list(mundo_opcoes.keys()), key="mundo_sel")

st.sidebar.markdown("---")
st.sidebar.caption("Cálculo 100% reativo ao ambiente.")

# ==========================================
# 3. ABAS PRINCIPAIS
# ==========================================
aba1, aba2, aba3, aba4 = st.tabs(["⚒️ Forja de Itens", "📚 Tabela de Pontos", "⚙️ Fórmula & Configs", "💎 Exemplos"])

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
        prop_selecionada = st.selectbox("Selecione um poder:", opcoes_lista if opcoes_lista else ["Vazio"])
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
    st.write("Edite os valores livremente. Qualquer alteração aqui refletirá instantaneamente nos itens que já estão na sua Forja!")

    # Exibe a tabela carregada do JSON
    df_editado = st.data_editor(
        st.session_state.tabela_regras, 
        num_rows="dynamic", # Habilita a criação de novas linhas temporárias
        use_container_width=True,
        column_config={
            "Tipo": st.column_config.SelectboxColumn(
                "Tipo de Cálculo", 
                options=["Fixo", "Multiplicador (Por +1)", "Multiplicador (Por Dado)", "Multiplicador (Por Nível)"], 
                required=True
            ),
            "Custo (P)": st.column_config.NumberColumn(
                "Custo em Pontos (P)", 
                min_value=1, 
                required=True
            )
        },
        key="editor_tabela_volatil"
    )
    
    # Atualiza a memória da sessão atual com os feitiços inventados na hora
    st.session_state.tabela_regras = df_editado

with aba3:
    st.header("Matemática do Sistema")
    st.latex(r"Custo = \left( \sum P \right)^{Exponente} \times A \times C \times M \times Base")
    st.write("- **P:** Pontos das Propriedades Mágicas")
    st.write("- **A:** Modificador de Sintonização")
    st.write("- **C:** Modificador de Consumo")
    st.write("- **M:** Modificador do Mundo (Lateral)")
    
    st.markdown("---")
    st.subheader("Ajustar Constantes do Universo")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.const_base = st.number_input("Constante Base (Ouro):", value=st.session_state.const_base)
    with col_c2:
        st.session_state.const_exp = st.number_input("Constante Exponencial:", value=st.session_state.const_exp, min_value=1.0, max_value=2.5, step=0.1)

# --- ABA 4: ITENS PRONTOS ---
with aba4:
    st.header("💎 Baú de Artefatos")
    st.write("Carregue itens lendários com um clique. Se o item possuir uma propriedade desconhecida, ela será **adicionada magicamente à sua Tabela de Poderes (Aba 2)**!")
    
    if not st.session_state.itens_prontos:
        st.warning("Nenhum item pronto encontrado em `itens.json`.")
    else:
        for item in st.session_state.itens_prontos:
            with st.expander(f"🗡️ {item['nome_item']}"):
                st.write(f"**Sintonização:** {item['sintonizacao']} | **Consumo:** {item['consumo']} | **Disruptivo:** {'Sim' if item['disruptivo'] else 'Não'}")
                
                # Exibe as propriedades
                for prop in item['propriedades']:
                    mult_texto = f" (x{prop['multiplicador']})" if "Multiplicador" in prop['Tipo'] else ""
                    st.write(f"- {prop['Propriedade Mágica']}: {prop['Custo (P)']} pts{mult_texto}")
                
                # Botão de carregar
                st.button(f"Carregar {item['nome_item']} na Forja", key=f"btn_load_{item['nome_item']}", on_click=carregar_item_pronto, args=(item,))