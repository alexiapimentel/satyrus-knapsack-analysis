import streamlit as st
from knapsack_analysis import KnapsackAnalysis as KA
import utils
from st_aggrid import AgGrid


st.set_page_config(page_title='Knapsack PESC', layout='wide')
st.markdown('<h3 align=center>Análise da Solução do Problema da Mochila</h3><br>', unsafe_allow_html=True)

# problem parameters
st.sidebar.header('Parametrização do Problema')
json_solution = st.sidebar.file_uploader('Solução em JSON')
n_items = st.sidebar.number_input('Número de Itens', step=1)
knapsack_capacity = st.sidebar.number_input('Capacidade da(s) Mochila(s)', step=1)
expected_carried_value = st.sidebar.number_input('Valor Esperado para Função Objetivo', step=1)
st.sidebar.markdown('* Adicione todos os itens antes de parametrizar o peso!')

if n_items > 0:
    st.markdown('<h6 align=left><u>Parametrização do peso dos itens</u></h6><br>', unsafe_allow_html=True)
    item_weights = utils.build_item_weights_df(n_items)
    editable_weights = AgGrid(item_weights, editable=True, height=75)
    weights = utils.transform_weights(editable_weights['data'])

    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<h6 align=left><u>Parametrização do valor dos itens</u></h6><br>', unsafe_allow_html=True)
    item_values = utils.build_item_values(n_items)
    editable_values = AgGrid(item_values, editable=True, height=75, key="editable_values")
    i_values = utils.transform_values(editable_values['data'])

    analyse_btn = st.button('Analisar Resultados')

    if analyse_btn:
        st.markdown('<br>', unsafe_allow_html=True)

        KA_inst = KA(json_solution, knapsack_capacity, weights)
        knapsack_configuration = KA_inst.knapsack_results()

        carried_value = KA_inst.check_carried_value(i_values)
        st.markdown(f'<h6 align=left>Valor Levado: {carried_value}</h6>', unsafe_allow_html=True)
        utils.check_carried_value(carried_value, expected_carried_value)

        st.markdown('<br>', unsafe_allow_html=True)
        with st.expander('Configuração da Mochila', expanded=True):
            utils.plot_knapsacks(knapsack_configuration)

        with st.expander('Relatório das Restrições', expanded=False):
            st.markdown('<h6 align=left><u>Restrição de Peso</u></h6>', unsafe_allow_html=True)
            st.markdown('<i>Para cada mochila i, a capacidade máxima não deve ser excedida pela soma do peso dos itens levados</i>', unsafe_allow_html=True)
            weight_constraint_check, weight_constraint_text, weight_constraint_color = KA_inst.check_weight_constraint()
            st.markdown(f'<font color={weight_constraint_color}>{weight_constraint_text}</font>', unsafe_allow_html=True)
            utils.plot_styled_constraint_df(weight_constraint_check)

            st.markdown('<br>', unsafe_allow_html=True)

            st.markdown('<h6 align=left><u>Restrição de Carga dos Itens</u></h6>', unsafe_allow_html=True)
            st.markdown('<i>Se um item j é levado na mochila i, ele não pode ser levado em nenhuma outra mochila</i>', unsafe_allow_html=True)
            item_carry_contraint, item_carry_contraint_text, item_carry_contraint_color = KA_inst.check_item_in_one_knapsack_constraint()
            st.markdown(f'<font color={item_carry_contraint_color}>{item_carry_contraint_text}</font>', unsafe_allow_html=True)
            utils.plot_styled_constraint_df(item_carry_contraint)

            st.markdown('<br>', unsafe_allow_html=True)

            st.markdown('<h6 align=left><u>Restrição de Blocos Levados</u></h6>', unsafe_allow_html=True)
            st.markdown('<i>Se um item j é levado em alguma mochila, todos os blocos desse item devem ser levados. O item é levado de forma inteira</i>', unsafe_allow_html=True)
            item_int_contraint, item_int_contraint_text, item_int_contraint_color = KA_inst.check_all_blocks_constraint()
            st.markdown(f'<font color={item_int_contraint_color}>{item_int_contraint_text}</font>', unsafe_allow_html=True)
            utils.plot_styled_constraint_df(item_int_contraint)
