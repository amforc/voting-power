import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib
import sys

def main():
    
    account_for_conviction = True
    votes_or_amount = 'total_votes' if account_for_conviction else 'amount'

    input_csv_path = pathlib.Path(sys.argv[1])
    addresses_and_weights = pd.read_csv(input_csv_path)

    sorted_votes = np.sort(addresses_and_weights[votes_or_amount])
    cumulative_distribution = np.cumsum(sorted_votes) / np.sum(sorted_votes)

    plt.figure(figsize=(10, 6))
    plt.plot(sorted_votes, cumulative_distribution, marker='.', linestyle='none')
    plt.xscale('log')
    plt.title('Cumulative Distribution of Shares')
    plt.xlabel('Number of Shares')
    plt.ylabel('Cumulative Percentage')
    plt.grid(True)
    plt.show()
    # output_folder = first_input_csv.parent.parent / 'comparison_plots'
    # output_filename = 'deviations_' + first_input_csv.stem + '.png'
    # plt.savefig(output_folder / output_filename)


if __name__ == "__main__":
    main()
