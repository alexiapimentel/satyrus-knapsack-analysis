import pandas as pd
from typing import Tuple


class KnapsackAnalysis:
    def __init__(self, satyrus_output, knapsack_capacity: int, items_weights: pd.DataFrame) -> None:
        self.results = pd.read_json(satyrus_output).reset_index().rename(columns={'index': 'variable'})
        self.item_blocks = self._weights_to_blocks(items_weights)
        self.knapsack_capacity = knapsack_capacity
        self.weights = items_weights

    @staticmethod
    def _weights_to_blocks(weights: pd.DataFrame) -> pd.DataFrame:
        item_blocks = []
        item_idx = 1
        blocks_idx = 1
        for w in weights['weight'].values:
            for idx in range(w):
                item_blocks.append([item_idx, blocks_idx])
                blocks_idx += 1
            item_idx += 1

        item_blocks = pd.DataFrame(item_blocks, columns=['item', 'block'])
        return item_blocks

    def knapsack_results(self) -> pd.DataFrame:
        """parse the json result into a dataframe with the knapsack composition"""

        # the knapsack configuration is in the format X_i_j_k where the indexes meanings are
        # i = knapsack
        # j = knapsack slot
        # k = item block
        knapsack_sol = self.results.loc[self.results['variable'].str.contains('x_')].copy()
        knapsack_sol[['_', 'knapsack', 'slot', 'block']] = knapsack_sol['variable'].str.split('_', 3, expand=True)
        knapsack_sol['block'] = knapsack_sol['block'].apply(lambda x: int(x))

        # merge blocks with item blocks relation to obtain knapsack configuration
        knapsack_sol = knapsack_sol.merge(self.item_blocks, on='block')
        knapsack_sol = knapsack_sol.loc[knapsack_sol['solution'] == 1]
        knapsack_sol = knapsack_sol[['knapsack', 'slot', 'item']].sort_values(by=['knapsack', 'slot', 'item'])

        self.knapsack_configuration = knapsack_sol.copy()

        knapsack_sol.rename(columns={'knapsack': 'Mochila', 'slot': 'Slot', 'item': 'Item'}, inplace=True)

        return knapsack_sol

    @staticmethod
    def _check_constraint_violation(constraint_df: pd.DataFrame, constraint: str) -> Tuple[pd.DataFrame, str, str]:
        color = 'red'
        suffix = 'violada'

        if constraint_df.loc[constraint_df['Status da Restrição'] == 'Violada'].empty:
            color = 'green'
            suffix = 'atendida'

        return constraint_df, f'Restrição {constraint} {suffix}', color

    def check_weight_constraint(self) -> Tuple[pd.DataFrame, str, str]:
        """The sum of carried item's weight must be less than or equal capacity of the knapsack capacity"""
        solution_by_item = self.knapsack_configuration.groupby(by=['knapsack', 'item'])['slot'].count().reset_index()
        weight_constraint = pd.merge(solution_by_item, self.weights, on='item').groupby(by='knapsack')['weight'].sum().reset_index()
        weight_constraint['Capacidade'] = self.knapsack_capacity
        weight_constraint.loc[:, 'Status da Restrição'] = weight_constraint['weight'].apply(lambda x: 'Ok' if x <= self.knapsack_capacity else 'Violada')
        weight_constraint.rename(columns={'knapsack': 'Mochila', 'weight': 'Peso Levado'}, inplace=True)

        return self._check_constraint_violation(weight_constraint, 'de capacidade da mochila')

    def check_item_in_one_knapsack_constraint(self) -> Tuple[pd.DataFrame, str, str]:
        """Each item must be carried on at most one knapsack"""

        # remove the slots logic to look only at the item dimension
        one_knapsack_constraint = self.knapsack_configuration[['item', 'knapsack']].copy()
        one_knapsack_constraint = one_knapsack_constraint.drop_duplicates()
        one_knapsack_constraint = one_knapsack_constraint.groupby(by='item')['knapsack'].count().reset_index()
        one_knapsack_constraint.rename(columns={'item': 'Item', 'knapsack': 'Número de Mochilas'}, inplace=True)

        # check if condition holds
        one_knapsack_constraint.loc[:, 'Status da Restrição'] = one_knapsack_constraint['Número de Mochilas'].apply(lambda x: 'Ok' if x == 1 else 'Violada')

        return self._check_constraint_violation(one_knapsack_constraint, 'do item é levado em apenas uma mochila')

    def check_all_blocks_constraint(self) -> Tuple[pd.DataFrame, str, str]:
        """The item should be carried as whole"""

        # the number of slots taken by item = item blocks carried, hence its weights
        all_blocks = self.knapsack_configuration.groupby(by='item')['slot'].count().reset_index()
        all_blocks = pd.merge(all_blocks, self.weights, on='item')

        all_blocks.loc[:, 'Status da Restrição'] = all_blocks.apply(lambda x: 'Ok' if x['slot'] == x['weight'] else 'Violada', axis=1)
        all_blocks.rename(columns={'item': 'Item', 'slots': 'Número de blocos levados', 'weight': ' Peso Esperado'}, inplace=True)

        return self._check_constraint_violation(all_blocks, 'de todos os slots do item serem carregados')
