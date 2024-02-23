import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import sys

def main():
    
    first_input_csv = pathlib.Path(sys.argv[1])
    second_input_csv = pathlib.Path(sys.argv[2])

    first_power_map = pd.read_csv(first_input_csv)
    second_power_map = pd.read_csv(second_input_csv)

    comparison_map = first_power_map.merge(second_power_map, on='address')
    comparison_map['deviation_weight'] = abs(comparison_map['weight_fraction_y']-comparison_map['weight_fraction_x'])/comparison_map['weight_fraction_x']
    comparison_map['deviation_power'] = abs(comparison_map['power_y']-comparison_map['power_x'])/comparison_map['power_x']

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8,6))
    top = 0.02 if 'kusama' in sys.argv[1] else 0.002
    axes[0].plot(comparison_map['weight_fraction_x'], comparison_map['deviation_weight'])
    axes[0].set_title("deviation_weight")
    axes[0].set_ylim(bottom=0, top=top)
    axes[1].plot(comparison_map['power_x'], comparison_map['deviation_power'])
    axes[1].set_title("deviation_power")
    axes[1].set_ylim(bottom=0, top=top)
    plt.tight_layout()
    # plt.show()
    output_folder = first_input_csv.parent.parent / 'comparison_plots'
    output_filename = 'deviations_' + first_input_csv.stem + '.png'
    plt.savefig(output_folder / output_filename)


if __name__ == "__main__":
    main()
