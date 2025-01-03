import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from tower_tracker.crud import delete_data, fetch_all_runs, insert_run
from tower_tracker.database import get_session
from tower_tracker.ui.utils import format_coins, parse_coins, sortable_treeview


def show_add_entry_window(refresh_callback) -> None:  # type: ignore
    """
    Opens a window to add a new entry and refreshes the table after submission.
    """
    add_window = tk.Toplevel()
    add_window.title("Add Entry")

    # Input fields
    tk.Label(add_window, text="Tier").grid(row=0, column=0)
    tier = tk.Entry(add_window)
    tier.grid(row=0, column=1)

    tk.Label(add_window, text="Wave").grid(row=1, column=0)
    wave = tk.Entry(add_window)
    wave.grid(row=1, column=1)

    tk.Label(add_window, text="Coins").grid(row=2, column=0)
    coins = tk.Entry(add_window)
    coins.grid(row=2, column=1)

    tk.Label(add_window, text="Cells").grid(row=3, column=0)
    cells = tk.Entry(add_window)
    cells.grid(row=3, column=1)

    tk.Label(add_window, text="Time (hh:mm:ss)").grid(row=4, column=0)
    time_spent = tk.Entry(add_window)
    time_spent.grid(row=4, column=1)

    tk.Label(add_window, text="Notes").grid(row=5, column=0)
    notes = tk.Entry(add_window)
    notes.grid(row=5, column=1)

    tk.Label(add_window, text="End of Round").grid(row=6, column=0)
    end_of_round = tk.BooleanVar()
    tk.Checkbutton(add_window, variable=end_of_round).grid(row=6, column=1)

    def submit() -> None:
        try:
            tier_value = int(tier.get())
            wave_value = int(wave.get())
            coins_value = parse_coins(coins.get())
            cells_value = int(cells.get())
            time_value = sum(
                x * int(t) for x, t in zip([3600, 60, 1], time_spent.get().split(":"))
            )
            notes_value = notes.get()
            end_round_value = end_of_round.get()
            insert_run(
                tier_value,
                wave_value,
                coins_value,
                cells_value,
                time_value,
                notes_value,
                end_round_value,
            )
            messagebox.showinfo("Success", "Data added successfully!")
            refresh_callback()  # Refresh the table in the Data Viewer
            add_window.destroy()  # Close the Add Entry window
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add data: {e}")

    tk.Button(add_window, text="Submit", command=submit).grid(row=7, column=1)


def show_data_viewer() -> None:
    """
    Creates a new window to display and manage the currently entered data.
    Includes functionality to view box-and-whisker plots.
    """
    viewer = tk.Toplevel()
    viewer.title("Data Viewer")

    # Create Treeview
    tree = ttk.Treeview(
        viewer,
        columns=(
            "id",
            "tier",
            "wave",
            "coins",
            "cells",
            "time_spent",
            "notes",
            "end_of_round",
            "datetime_collected",
        ),
        show="headings",
    )
    tree.pack(fill=tk.BOTH, expand=True)

    # Define columns
    column_names = {
        "id": "ID",
        "tier": "Tier",
        "wave": "Wave",
        "coins": "Coins",
        "cells": "Cells",
        "time_spent": "Time Spent",
        "notes": "Notes",
        "end_of_round": "End of Round",
        "datetime_collected": "Datetime Collected",
    }
    for col, col_label in column_names.items():
        tree.heading(col, text=col_label)
        tree.column(col, width=100, anchor=tk.W)

    # Populate Treeview with data
    def load_data() -> None:
        for row in tree.get_children():
            tree.delete(row)

        data = fetch_all_runs()
        for run in data:
            tree.insert(
                "",
                tk.END,
                values=(
                    run.id,
                    run.tier,
                    run.wave,
                    format_coins(run.coins),
                    run.cells,
                    run.time_spent,
                    run.notes,
                    run.end_of_round,
                    run.datetime_collected,
                ),
            )

    load_data()

    # Enable sorting
    sortable_treeview(tree)

    # Add delete button
    def delete_selected() -> None:
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an entry to delete.")
            return

        for item in selected_item:
            entry_id = tree.item(item, "values")[0]
            if delete_data(entry_id):
                messagebox.showinfo(
                    "Success", f"Entry ID {entry_id} deleted successfully!"
                )
            else:
                messagebox.showerror("Error", f"Failed to delete entry ID {entry_id}.")

        load_data()

    delete_button = tk.Button(viewer, text="Delete Selected", command=delete_selected)
    delete_button.pack(pady=5)

    # Add refresh button
    refresh_button = tk.Button(viewer, text="Refresh", command=load_data)
    refresh_button.pack(pady=5)

    # Add button to open Add Entry UI
    add_entry_button = tk.Button(
        viewer, text="Add New Entry", command=lambda: show_add_entry_window(load_data)
    )
    add_entry_button.pack(pady=5)

    # Add box-and-whisker plot buttons
    def view_boxplot() -> None:
        """
        Fetch aggregated data and show box-and-whisker plots grouped by tier.
        Includes datapoints to visualize outliers and distribution.
        """
        with get_session() as session:
            df = pd.read_sql_query("SELECT * FROM run_statistics", session.bind)
            df["coins_per_hour"] = df["coins"] / (df["time_spent"] / 3600)
            df["coins_per_wave"] = df["coins"] / df["wave"]
            df["cells_per_hour"] = df["cells"] / (df["time_spent"] / 3600)
            df["cells_per_wave"] = df["cells"] / df["wave"]

        metrics = [
            "coins_per_hour",
            "coins_per_wave",
            "cells_per_hour",
            "cells_per_wave",
        ]

        for metric in metrics:
            grouped_data = [
                df[df["tier"] == tier][metric].dropna()
                for tier in sorted(df["tier"].unique())
            ]
            tiers = sorted(df["tier"].unique())

            plt.figure(figsize=(12, 8))

            # Create the box-and-whisker plot
            boxplot = plt.boxplot(
                grouped_data, labels=tiers, patch_artist=True, showfliers=True
            )

            # Add individual data points
            for i, tier in enumerate(tiers):
                data_points = grouped_data[i]
                # Add jitter to x-axis to spread data points slightly
                jittered_x = np.random.normal(
                    loc=i + 1, scale=0.05, size=len(data_points)
                )
                plt.scatter(
                    jittered_x,
                    data_points,
                    alpha=0.6,
                    label=f"Tier {tier}",
                    color="blue",
                )

            plt.title(
                f"{metric.replace('_', ' ').capitalize()} by Tier with Data Points"
            )
            plt.xlabel("Tier")
            plt.ylabel(metric.replace("_", " ").capitalize())
            plt.grid(axis="y", linestyle="--", alpha=0.7)
            plt.tight_layout()
            plt.show()

    plot_button = tk.Button(
        viewer, text="View Box-and-Whisker Plots", command=view_boxplot
    )
    plot_button.pack(pady=5)


def show_averages() -> None:
    """
    Displays a new window showing the average statistics per tier.
    """
    averages_window = tk.Toplevel()
    averages_window.title("Average Statistics per Tier")

    # Create Treeview for displaying averages
    tree = ttk.Treeview(
        averages_window,
        columns=(
            "tier",
            "avg_coins_per_hour",
            "avg_coins_per_wave",
            "avg_cells_per_hour",
            "avg_cells_per_wave",
        ),
        show="headings",
    )
    tree.pack(fill=tk.BOTH, expand=True)

    # Define column headings
    column_names = {
        "tier": "Tier",
        "avg_coins_per_hour": "Avg Coins/Hour",
        "avg_coins_per_wave": "Avg Coins/Wave",
        "avg_cells_per_hour": "Avg Cells/Hour",
        "avg_cells_per_wave": "Avg Cells/Wave",
    }
    for col, col_label in column_names.items():
        tree.heading(col, text=col_label)
        tree.column(col, width=150, anchor=tk.CENTER)

    # Fetch data and populate Treeview
    with get_session() as session:
        df = pd.read_sql_query("SELECT * FROM run_statistics", session.bind)
        df["coins_per_hour"] = df["coins"] / (df["time_spent"] / 3600)
        df["coins_per_wave"] = df["coins"] / df["wave"]
        df["cells_per_hour"] = df["cells"] / (df["time_spent"] / 3600)
        df["cells_per_wave"] = df["cells"] / df["wave"]

        averages = (
            df.groupby("tier")
            .agg(
                avg_coins_per_hour=("coins_per_hour", "mean"),
                avg_coins_per_wave=("coins_per_wave", "mean"),
                avg_cells_per_hour=("cells_per_hour", "mean"),
                avg_cells_per_wave=("cells_per_wave", "mean"),
            )
            .reset_index()
        )

        for _, row in averages.iterrows():
            tree.insert(
                "",
                tk.END,
                values=(
                    int(row["tier"]),
                    format_coins(row["avg_coins_per_hour"]),
                    format_coins(row["avg_coins_per_wave"]),
                    round(row["avg_cells_per_hour"], 2),
                    round(row["avg_cells_per_wave"], 2),
                ),
            )

    # Enable sorting
    sortable_treeview(tree)

    # Close button
    close_button = tk.Button(
        averages_window, text="Close", command=averages_window.destroy
    )
    close_button.pack(pady=10)
