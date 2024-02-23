import numpy as np
import pandas as pd
import pathlib
import sys


def small_voters_coalition(addresses_and_weights_df, account_for_conviction: bool):
    votes_or_amount = 'votes' if account_for_conviction else 'amount'
    total_weight = addresses_and_weights_df[f'total_{votes_or_amount}'].sum()
    small_voters_df = addresses_and_weights_df[addresses_and_weights_df[f'total_{votes_or_amount}'] < 0.001*total_weight]
    small_voters_total = small_voters_df[f'total_{votes_or_amount}'].sum()
    addresses_and_weights_df = addresses_and_weights_df[addresses_and_weights_df[f'total_{votes_or_amount}'] >= 0.001*total_weight]
    small_voters_combined_df = pd.DataFrame([{'address': 'SmallVotersCombined', f'total_{votes_or_amount}': small_voters_total}])
    addresses_and_weights_df = pd.concat([addresses_and_weights_df, small_voters_combined_df], ignore_index=True)

    return addresses_and_weights_df


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


def write_to_file(input_csv_path, power_map):
    output_filename = f"{input_csv_path.stem}_voting_power{input_csv_path.suffix}"
    output_directory = pathlib.Path(__file__).resolve().parent / 'banzhaf_output_csvs'
    output_csv_path = output_directory / output_filename
    pd.DataFrame(power_map).to_csv(output_csv_path, index=False)

    return

def main():

    account_for_conviction = True
    combine_small_voters = True
    votes_or_amount = 'votes' if account_for_conviction else 'amount'

    input_csv_path = pathlib.Path(sys.argv[1])
    electorate = pd.read_csv(input_csv_path)
    decimals = 10 if 'polkadot' in sys.argv[1] else 12
    scaling_factor = 10**13 / 10**decimals

    addresses_and_weights_df = electorate.drop(['referendum_index','origin','amount','conviction','status','voting_time','delegated_votes'], axis=1)
    if combine_small_voters:
        addresses_and_weights_df = small_voters_coalition(addresses_and_weights_df, account_for_conviction)
    addresses_and_weights_df[f'total_{votes_or_amount}'] = round(addresses_and_weights_df[f'total_{votes_or_amount}']/scaling_factor)
    total_weight = addresses_and_weights_df[f'total_{votes_or_amount}'].sum()
    quota = int(total_weight/2+1)
    addresses_and_weights = addresses_and_weights_df.astype({f'total_{votes_or_amount}': 'int32'}).sort_values(f'total_{votes_or_amount}', ascending=False).to_dict('records')

    if addresses_and_weights[0][f'total_{votes_or_amount}'] >= quota:
        power_map = [{'address': voter['address'], 'weight': voter[f'total_{votes_or_amount}'], 'weight_fraction': voter[f'total_{votes_or_amount}']/total_weight, 'power': 0.0} for voter in addresses_and_weights]
        power_map[0]['power'] = 1.0
        write_to_file(input_csv_path, power_map)
        return

    power_map = []
    for current_voter in addresses_and_weights:
        voter_weight = current_voter[f'total_{votes_or_amount}']
        duplicate = next((voter for voter in power_map if voter['weight'] == voter_weight), None)

        if duplicate:
            power_map.append({'address': current_voter['address'], 'weight': voter_weight, 'weight_fraction': voter_weight/total_weight, 'power': duplicate['power']})
        else:
            voter_power = calculate_voter_power(current_voter=current_voter, addresses_and_weights=addresses_and_weights, quota=quota, account_for_conviction=account_for_conviction)
            power_map.append({'address': current_voter['address'], 'weight': voter_weight, 'weight_fraction': voter_weight/total_weight, 'power': voter_power})
    
    power_map = normalize_power_map(power_map)

    write_to_file(input_csv_path, power_map)



if __name__ == "__main__":
    main()
