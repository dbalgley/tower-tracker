import pandas as pd

from tower_tracker.database import get_session


def analyze_data():
    """
    Analyzes data from the database and calculates additional statistics.
    """
    with get_session() as session:
        df = pd.read_sql_query("SELECT * FROM run_statistics", session.bind)
        df["coins_per_hour"] = df["coins"] / (df["time_spent"] / 3600)
        df["coins_per_wave"] = df["coins"] / df["wave"]
        df["cells_per_hour"] = df["cells"] / (df["time_spent"] / 3600)
        df["cells_per_wave"] = df["cells"] / df["wave"]
        return df
