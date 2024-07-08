import json
import pandas as pd
import pathlib
import sys


def sum_delegates(electorate: pd.DataFrame, account_for_conviction: bool):
    votes_or_amount = 'votes' if account_for_conviction else 'amount'
    delegated_votes = electorate.dropna()
    direct_votes = electorate[electorate['delegate'].isna()]

    delegated_votes_totals = delegated_votes.groupby('delegate')[votes_or_amount].sum().reset_index()
    delegated_votes_totals.rename(columns={votes_or_amount: f'delegated_{votes_or_amount}'}, inplace=True)
    delegated_amounts_totals = delegated_votes.groupby('delegate')['amount'].sum().reset_index()
    delegated_amounts_totals.rename(columns={'amount': f'delegated_amounts'}, inplace=True)
    delegated_votes_and_amounts = delegated_votes_totals.merge(delegated_amounts_totals, on='delegate')
    delegated_votes_and_amounts['avg_conviction'] = delegated_votes_and_amounts['delegated_votes'] / delegated_votes_and_amounts['delegated_amounts']
    
    combined_votes = direct_votes.merge(delegated_votes_and_amounts, left_on='address', right_on='delegate', how='left')
    combined_votes.fillna(value={f'delegated_{votes_or_amount}': 0, 'delegated_amounts': 0, 'avg_conviction': 0}, inplace=True)
    combined_votes[votes_or_amount] = combined_votes[votes_or_amount] + combined_votes[f'delegated_{votes_or_amount}']
    combined_votes.rename(columns={votes_or_amount: f'total_{votes_or_amount}'}, inplace=True)
    combined_votes['conviction'] = (combined_votes['conviction']*combined_votes['amount'] + combined_votes['delegated_amounts']*combined_votes['avg_conviction'])/(combined_votes['amount'] + combined_votes['delegated_amounts'])
    combined_votes.drop(['delegate_x', 'delegate_y', 'avg_conviction'], axis=1, inplace=True)
    combined_votes.rename(columns={'conviction': 'avg_conviction'}, inplace=True)

    return combined_votes


def main():

    account_for_conviction = True

    input_csv_path = pathlib.Path(sys.argv[1])
    decimals = 10 if 'polkadot' in sys.argv[1] else 12

    votes_df = pd.read_csv(input_csv_path)

    # with open("linked_addresses.json", "r") as jsonfile:
    #     linked_addresses = json.load(jsonfile)
    # for subaddresses in linked_addresses.values():
    #     votes_df = votes_df[~votes_df['address'].isin(subaddresses)]
        
    votes_or_amount = 'votes' if account_for_conviction else 'amount'
    origins = votes_df.drop_duplicates('origin')['origin'].to_list()

    electorate_by_origin = {}
    for origin in origins:
        electorate_by_origin[f'{origin}'] = votes_df.copy()[votes_df.copy()['origin'] == origin]

    for origin in electorate_by_origin:
        electorate_by_origin[origin] = electorate_by_origin[origin].sort_values(votes_or_amount, axis=0, ascending=False, ignore_index=True)
        electorate_by_origin[origin] = electorate_by_origin[origin].drop_duplicates('address', ignore_index=True)
        electorate_by_origin[origin]['amount'] = electorate_by_origin[origin]['amount']/(10**decimals)
        electorate_by_origin[origin]['votes'] = electorate_by_origin[origin]['votes']/(10**decimals)
        electorate_by_origin[origin] = sum_delegates(electorate_by_origin[origin], account_for_conviction)
        electorate_by_origin[origin].sort_values(f'total_{votes_or_amount}', ascending=False, inplace=True)

        output_filename = f"{input_csv_path.stem}_{electorate_by_origin[origin]['origin'].to_list()[0]}{input_csv_path.suffix}"
        output_directory = pathlib.Path(__file__).resolve().parent / 'input_csvs_heatmap'
        output_csv_path = output_directory / output_filename
        electorate_by_origin[origin].to_csv(output_csv_path, index=False)


if __name__ == "__main__":
    main()
