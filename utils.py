import pandas as pd
import numpy as np
import streamlit as st


def build_item_weights_df(n_items: int) -> pd.DataFrame:
    column_list = [f'Item {i}' for i in range(1, n_items+1)]
    item_weights = pd.DataFrame(columns=column_list)
    item_weights.loc[0] = list(np.zeros(n_items))
    item_weights.loc[:, 'idx'] = 'Peso'
    item_weights.set_index('idx', inplace=True)

    return item_weights


def transform_weights(df: pd.DataFrame) -> pd.DataFrame:
    weights = df.T.reset_index().rename(columns={'index': 'item', 0: 'weight'})
    weights.loc[:, 'item'] = weights['item'].apply(lambda x: int(x.replace('Item ', '')))

    return weights


def plot_knapsacks(knapsacks_config: pd.DataFrame) -> None:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<h6 align=left><u>Configuração das Mochilas</u></h6>', unsafe_allow_html=True)
    knapsacks = knapsacks_config['Mochila'].unique()
    for k in knapsacks:
        st.markdown(f'<h6 align=left>Mochila {k}</h6>', unsafe_allow_html=True)
        current = knapsacks_config.loc[knapsacks_config['Mochila'] == k].set_index('Mochila')
        st.dataframe(current)


def _color_constraint_df(s):
    if s['Status da Restrição'] == 'Violada':
        return ['background-color: #F1948A'] * len(s)
    else:
        return ['background-color: #7DCEA0'] * len(s)


def plot_styled_constraint_df(df: pd.DataFrame) -> pd.DataFrame:
    st.dataframe(df.style.apply(_color_constraint_df, axis=1))
