from typing import Any, List, LiteralString, Union

from tower_tracker.database import get_session
from tower_tracker.models.models import RunStatistics


def insert_run(
    tier: int,
    wave: int,
    coins: float,
    cells: int,
    time_spent: int,
    notes: str,
    end_of_round: bool,
) -> None:
    with get_session() as session:
        new_run = RunStatistics(
            tier=tier,
            wave=wave,
            coins=coins,
            cells=cells,
            time_spent=time_spent,
            notes=notes,
            end_of_round=end_of_round,
        )
        session.add(new_run)
        session.commit()


def fetch_all_runs() -> List[RunStatistics]:
    with get_session() as session:
        return session.query(RunStatistics).all()  # type: ignore


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
