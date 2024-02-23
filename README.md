Voting Power of DOT Holders

1. Run "python voting_from_subscan.py {network} {lookback_period_in_days}"
2. This will output {network}_votes_{lookback}_days.csv
3. Run "python prepare_data.py {csvfile}", this will create suitable input csv files for banzhaf.py in folder input_csvs
4. Run "run_banzhaf.ps1" for all csv files in input_csvs or "python banzhaf.py {input_csvfile}"
5. Run "python heatmap_prepare_data.py {csvfile}", this will create suitable input csv files for heatmap_banzhaf.py in folder input_csvs_heatmap
6. Run "run_banzhaf_heatmap.ps1" for all csv files in input_csvs or "python heatmap_banzhaf.py {input_csvfile}"
7. Run "run_banzhaf_heatmap_plots.ps1" to generate plots from heatmap outputs
8. Analyze outputs

These steps will generate a set of addresses that have participated on a specific voting track in the lookback period. Delegated votes are added to the delegate's voting power. It will then generate Banzhaf voting powers using a generative polynomials algorithm.
