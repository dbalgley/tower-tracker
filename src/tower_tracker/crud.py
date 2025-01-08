from typing import Any, List, LiteralString, Union

from tower_tracker.database import get_session
from tower_tracker.models.models import RunStatistics

def get_run_tier(run_id: int):
    """
    Fetches the tier associated with a given run_id.
    Returns the tier if the run_id exists, or None if it does not.
    """
    with get_session() as session:
        run = session.query(RunStatistics).filter_by(run_id=run_id).first()
        return run.tier if run else None

def get_run_status(run_id: int) -> bool:
    """
    Checks if the round associated with the given run_id has ended.
    Returns True if the round has ended, False otherwise.
    """
    with get_session() as session:
        run = session.query(RunStatistics).filter_by(run_id=run_id).first()
        return run.end_of_round if run else False

def get_active_run_id():
    """
    Returns the current active run_id, or None if no run is active.
    """
    with get_session() as session:
        active_run = session.query(RunStatistics).filter_by(end_of_round=False).order_by(RunStatistics.run_id.desc()).first()
        return active_run.run_id if active_run else None

def insert_run(\
    run_id: int,
    tier: int,
    wave: int,
    coins: float,
    cells: int,
    time_spent: int,
    notes: str,
    end_of_round: bool,
) -> None:
    with get_session() as session:
        # Check if the run exists
        existing_run = session.query(RunStatistics).filter_by(run_id=run_id).first()

        # if existing_run:
        #     # Run exists, ensure it's not ended
        #     if existing_run.end_of_round:
        #         raise ValueError(f"Cannot add entries to an ended run (run_id: {run_id}).")
        # else:
        #     # If run_id does not exist, assume a new run is being created
        #     print(f"Creating new run with run_id: {run_id}")
        new_run = RunStatistics(
            run_id=run_id,
            tier=tier,
            wave=wave,
            coins=coins,
            cells=cells,
            time_spent=time_spent,
            notes=notes,
            end_of_round=end_of_round,
        )
        session.add(new_run)

        # If this is the end-of-round entry, mark the run as ended
        if end_of_round:
            session.query(RunStatistics).filter_by(run_id=run_id).update({"end_of_round": True})

        session.commit()


def fetch_all_data() -> List[RunStatistics]:
    with get_session() as session:
        return session.query(RunStatistics).all()  # type: ignore

def fetch_all_run_ids() -> List[RunStatistics]:
    with get_session() as session:
        return [row[0] for row in session.query(RunStatistics.run_id).distinct().order_by(RunStatistics.run_id).all()]

def fetch_all_runs() -> List[RunStatistics]:
    with get_session() as session:
        runs = []
        for run_id in fetch_all_run_ids():
            latest_run = session.query(RunStatistics).filter_by(run_id=run_id).order_by(RunStatistics.datetime_collected.desc()).first()
            if latest_run:
                runs.append(latest_run)
        return runs

def fetch_all_entries_for_run(run_id: int) -> List[RunStatistics]:
    with get_session() as session:
        return session.query(RunStatistics).filter_by(run_id=run_id).order_by(RunStatistics.datetime_collected).all()  # type: ignore


def delete_data(entry_id: Union[Any | LiteralString]) -> bool:
    """
    Deletes a specific run entry by ID.
    """
    with get_session() as session:
        try:
            run = session.query(RunStatistics).filter_by(id=entry_id).first()
            if run:
                session.delete(run)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
