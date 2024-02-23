import copy
import numpy as np
import pandas as pd
import pathlib
import sys


def small_voters_coalition(addresses_and_weights_df, account_for_conviction: bool):
    votes_or_amount = 'votes' if account_for_conviction else 'amount'
    total_weight = addresses_and_weights_df[f'total_{votes_or_amount}'].sum()
    small_voters_df = addresses_and_weights_df[addresses_and_weights_df[f'total_{votes_or_amount}'] < 0.001*total_weight].copy()
    small_voters_df['amount'] = small_voters_df[f'total_{votes_or_amount}'] / small_voters_df['avg_conviction']
    small_voters_total = small_voters_df[f'total_{votes_or_amount}'].sum()
    average_conviction = small_voters_total/small_voters_df['amount'].sum()
    addresses_and_weights_df = addresses_and_weights_df[addresses_and_weights_df[f'total_{votes_or_amount}'] >= 0.001*total_weight]
    small_voters_combined_df = pd.DataFrame([{'address': 'SmallVotersCombined', f'total_{votes_or_amount}': small_voters_total, 'avg_conviction': average_conviction}])
    addresses_and_weights_df = pd.concat([addresses_and_weights_df, small_voters_combined_df], ignore_index=True)

    return addresses_and_weights_df


def update_for_conviction(addresses_and_weights, address, new_conviction, new_votes_amount):
    for voter in addresses_and_weights:
        if voter['address'] == address:
            voter['total_votes'] = new_votes_amount
            voter['avg_conviction'] = new_conviction
    
    addresses_and_weights.sort(key=lambda x: x['total_votes'], reverse=True)

    return addresses_and_weights

def calculate_voter_power(current_voter, addresses_and_weights, quota, account_for_conviction: bool):
    votes_or_amount = 'votes' if account_for_conviction else 'amount'
    starting_value = np.array([1], dtype=np.float64)
    voter_polynomial = np.poly1d(starting_value)

    for voter in addresses_and_weights:
        if voter['address'] == current_voter['address']:
            continue
        factor = np.poly1d(1)
        factor[voter[f'total_{votes_or_amount}']] = 1
        voter_polynomial *= factor

    coefficients = voter_polynomial.coeffs
    lower_end = quota - current_voter[f'total_{votes_or_amount}']
    upper_end = quota - 1
    voter_power = sum(coefficient for exponent, coefficient in enumerate(coefficients) 
                      if lower_end <= exponent <= upper_end)
    
    return voter_power


def normalize_power_map(power_map):
    total_power = sum(voter['power'] for voter in power_map)
    for voter in power_map:
        voter['power'] /= total_power
    
    return power_map


def write_to_file(input_csv_path, heatmap_data):
    output_filename = f"{input_csv_path.stem}_conviction_heatmap{input_csv_path.suffix}"
    output_directory = pathlib.Path(__file__).resolve().parent / 'banzhaf_heatmap'
    output_csv_path = output_directory / output_filename
    data = pd.DataFrame(heatmap_data)
    data = data[['address', 'conviction', 'amount', 'weight', 'weight_fraction', 'power', 'original_conviction']]
    data.sort_values(['amount', 'address', 'conviction'], ascending=[False, True, True]).to_csv(output_csv_path, index=False)

    return

def main():

    account_for_conviction = True
    combine_small_voters = True
    votes_or_amount = 'votes' if account_for_conviction else 'amount'
    conviction_options = [0.1, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    input_csv_path = pathlib.Path(sys.argv[1])
    electorate = pd.read_csv(input_csv_path)
    decimals = 10 if 'polkadot' in sys.argv[1] else 12
    scaling_factor = 10**14 / 10**decimals

    addresses_and_weights_df = electorate.drop(['referendum_index','origin','amount','status','voting_time', 'delegated_votes', 'delegated_amounts'], axis=1)
    if combine_small_voters:
        addresses_and_weights_df = small_voters_coalition(addresses_and_weights_df, account_for_conviction)
    addresses_and_weights_df[f'total_{votes_or_amount}'] = round(addresses_and_weights_df[f'total_{votes_or_amount}']/scaling_factor)
    addresses = addresses_and_weights_df['address'].to_list()
    addresses_and_weights = addresses_and_weights_df.astype({f'total_{votes_or_amount}': 'int32'}).sort_values(f'total_{votes_or_amount}', ascending=False).to_dict('records')

    heatmap_data = []
    for address in addresses:
        address_data = next(((entry['total_votes'], entry['avg_conviction']) for entry in addresses_and_weights if entry['address'] == address))
        address_amount = address_data[0]/address_data[1]
        for conviction in conviction_options:
            address_votes = address_amount * conviction
            temp_addresses_and_weights = update_for_conviction(copy.deepcopy(addresses_and_weights), address, new_conviction=conviction, new_votes_amount=int(address_votes))
            total_weight = pd.DataFrame(temp_addresses_and_weights)[f'total_{votes_or_amount}'].sum()
            quota = int(total_weight/2+1)

            if temp_addresses_and_weights[0][f'total_{votes_or_amount}'] >= quota:
                power_map = [{'address': voter['address'], 'conviction': voter['avg_conviction'], 'weight': voter[f'total_{votes_or_amount}'], 'weight_fraction': voter[f'total_{votes_or_amount}']/total_weight, 'amount': voter[f'total_{votes_or_amount}'] / voter['avg_conviction'], 'power': 0.0} for voter in temp_addresses_and_weights]
                power_map[0]['power'] = 1.0

            else:
                power_map = []
                for current_voter in temp_addresses_and_weights:
                    voter_weight = current_voter[f'total_{votes_or_amount}']
                    duplicate = next((voter for voter in power_map if voter['weight'] == voter_weight), None)

                    if duplicate:
                        power_map.append({'address': current_voter['address'], 'conviction': current_voter['avg_conviction'], 'weight': voter_weight, 'weight_fraction': voter_weight/total_weight, 'power': duplicate['power']})
                    else:
                        voter_power = calculate_voter_power(current_voter=current_voter, addresses_and_weights=temp_addresses_and_weights, quota=quota, account_for_conviction=account_for_conviction)
                        power_map.append({'address': current_voter['address'], 'conviction': current_voter['avg_conviction'], 'weight': voter_weight, 'weight_fraction': voter_weight/total_weight, 'power': voter_power})
                
                power_map = normalize_power_map(power_map)

            voter_data = next((voter for voter in power_map if voter['address'] == address), None)
            voter_data['amount'] = address_amount
            voter_data['original_conviction'] = address_data[1]
            heatmap_data.append(voter_data)

    write_to_file(input_csv_path, heatmap_data)


if __name__ == "__main__":
    main()
