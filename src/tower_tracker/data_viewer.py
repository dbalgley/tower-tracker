import pandas as pd
from sqlalchemy import func

from tower_tracker.database import get_session
from tower_tracker.models.models import RunStatistics


def generate_new_run_id():
    """
    Generate a new run_id based on the highest existing run_id.
    """
    with get_session() as session:
        result = session.query(func.max(RunStatistics.run_id)).scalar()
        return (result or 0) + 1

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
