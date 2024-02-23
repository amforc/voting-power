import matplotlib.pyplot as plt
import math
import numpy as np
import pathlib
import pandas as pd
import sys

from matplotlib.ticker import FixedLocator, FixedFormatter, FuncFormatter


def main():
    
    input_csv_path = pathlib.Path(sys.argv[1])
    output_directory = pathlib.Path(__file__).resolve().parent / 'heatmap_plots'
    heatmap_data = pd.read_csv(input_csv_path)
    decimals = 10 if 'polkadot' in sys.argv[1] else 12
    scaling_factor = 10**14 / 10**decimals
    heatmap_data['amount'] = heatmap_data['amount'] * scaling_factor
    plot_scaling_factor = 1_000_000 if 'polkadot' in sys.argv[1] else 1_000
    track = sys.argv[1][sys.argv[1].find('days_')+5:sys.argv[1].find('_conviction')].replace('_', ' ').title()
    plot_colors = 'viridis'
    edge_color = 'black'

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(heatmap_data['amount']/plot_scaling_factor, heatmap_data['conviction'], c=heatmap_data['power']*100, cmap=plot_colors, s=100)
    plt.scatter(heatmap_data['amount']/plot_scaling_factor, heatmap_data['original_conviction'], c='none', edgecolors=edge_color, linewidths=1.5, s=100)
    cbar = plt.colorbar(scatter, label='power')
    tick_max = math.ceil(heatmap_data['power'].max()*10)*10
    tick_positions = list(range(10, tick_max+10, 10))
    cbar.locator = FixedLocator(tick_positions)
    cbar.formatter = FixedFormatter([f'{i}%' for i in tick_positions])
    cbar.update_ticks()
    plt.ticklabel_format(style='plain', axis='x')
    plt.title(f'{track} Conviction Heatmap')
    xlabel = 'amount (in million DOT)' if 'polkadot' in sys.argv[1] else 'amount (in thousand KSM)'
    plt.xlabel(xlabel)
    plt.ylabel('conviction')
    output_filename = f"{input_csv_path.stem}_conviction_heatmap.png"
    output_png_path = output_directory / output_filename
    # plt.show()
    plt.savefig(output_png_path)

    epsilon = 0.0001
    heatmap_data['power'] = heatmap_data['power'].replace(0, epsilon)
    plt.figure(figsize=(10, 8))
    logscatter = plt.scatter(heatmap_data['amount'], heatmap_data['conviction'], c=heatmap_data['power']*100, cmap=plot_colors, s=100, norm='log')
    plt.scatter(heatmap_data['amount'], heatmap_data['original_conviction'], c='none', edgecolors=edge_color, linewidths=1.5, s=100)
    cbar = plt.colorbar(logscatter, label='power')
    tick_positions = [epsilon, 0.1, 1, 10, 50, 100]
    cbar.locator = FixedLocator(tick_positions)
    cbar.formatter = FixedFormatter([f'{i}%' if i != epsilon else '0%' for i in tick_positions])
    cbar.update_ticks()
    plt.xscale('log')
    plt.gca().xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f"{int(val):,}".replace(',',"'")))
    plt.title(f'{track} Conviction Heatmap')
    xlabel = 'amount (DOT)' if 'polkadot' in sys.argv[1] else 'amount (KSM)'
    plt.xlabel(xlabel)
    plt.ylabel('conviction')
    output_filename = f"{input_csv_path.stem}_conviction_heatmap_log_x_log_color.png"
    output_png_path = output_directory / output_filename
    plt.savefig(output_png_path)
    # plt.show()




if __name__ == "__main__":
    main()
