import tkinter as tk

from tower_tracker.ui.windows import show_averages, show_data_viewer


def main() -> None:
    root = tk.Tk()
    root.title("Game Statistics Tracker")

    # Button to show data viewer
    tk.Button(root, text="View Data", command=show_data_viewer).pack(pady=10)

    # Button to show averages
    tk.Button(root, text="Show Averages", command=show_averages, width=20).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
