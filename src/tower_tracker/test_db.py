from tower_tracker.crud import fetch_all_runs, insert_run

# Insert a new run
insert_run(
    tier=5,
    wave=10,
    coins=1_000_000.0,
    cells=500,
    time_spent=3600,
    notes="Test run",
    end_of_round=True,
)

# Fetch and print all runs
runs = fetch_all_runs()
for run in runs:
    print(run.tier, run.wave, run.coins, run.cells, run.datetime_collected)
