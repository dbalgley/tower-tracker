from matplotlib import pyplot as plt

# TODO: This function is not used in the current implementation. It needs to be used instead of the current, nested method.
def plot_outliers(df):
    """
    Plots a box-and-whisker plot grouped by tier.

    Each box corresponds to a tier, and the plot shows the distribution of
    coins_per_hour, coins_per_wave, cells_per_hour, and cells_per_wave for that tier.
    """
    metrics = ["coins_per_hour", "coins_per_wave", "cells_per_hour", "cells_per_wave"]

    for metric in metrics:
        grouped_data = [
            df[df["tier"] == tier][metric].dropna()
            for tier in sorted(df["tier"].unique())
        ]

        plt.figure(figsize=(10, 6))
        plt.boxplot(grouped_data, labels=sorted(df["tier"].unique()), showfliers=True)
        plt.title(f"{metric.replace('_', ' ').capitalize()} by Tier")
        plt.xlabel("Tier")
        plt.ylabel(metric.replace("_", " ").capitalize())
        plt.grid(axis="y")
        plt.show()
