import json
from pathlib import Path

from aco_engine import ACOFlowShop, MACHINE_COLS, evaluate_sequence, load_production_dataset


def _make_gantt_rows(sequence, start, completion, machine_cols, job_ids):
    rows = []
    for machine_idx, machine_name in enumerate(machine_cols):
        for pos, job_idx in enumerate(sequence):
            st = float(start[pos, machine_idx])
            en = float(completion[pos, machine_idx])
            rows.append(
                {
                    "machine": machine_name,
                    "jobId": job_ids[job_idx],
                    "start": st,
                    "end": en,
                    "duration": en - st,
                }
            )
    return rows


def main() -> None:
    data_path = Path("dataset/production_jobs.csv")
    results_path = Path("results/results.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)

    df = load_production_dataset(data_path)
    p_times = df[MACHINE_COLS].to_numpy(dtype=float)
    job_ids = df["JobID"].tolist()

    baseline_seq = list(range(len(df)))
    baseline = evaluate_sequence(baseline_seq, p_times)

    model = ACOFlowShop(p_times, ants=30, iterations=120, seed=42)
    best_seq, best_makespan, history = model.run()
    best = evaluate_sequence(best_seq, p_times)

    improvement = (baseline.makespan - best_makespan) / baseline.makespan * 100
    machine_busy = p_times[best_seq, :].sum(axis=0)
    machine_utilization = ((machine_busy / best_makespan) * 100).tolist()

    output = {
        "dataset": {
            "rows": df.to_dict(orient="records"),
            "machineColumns": MACHINE_COLS,
        },
        "metrics": {
            "baselineMakespan": float(baseline.makespan),
            "bestMakespan": float(best_makespan),
            "improvementPercent": float(improvement),
            "baselineWaiting": float(baseline.total_waiting),
            "bestWaiting": float(best.total_waiting),
            "baselineIdle": float(baseline.total_idle),
            "bestIdle": float(best.total_idle),
        },
        "bestSequence": [job_ids[i] for i in best_seq],
        "convergence": [float(v) for v in history],
        "machineUtilization": [
            {"machine": m, "utilizationPercent": float(u)}
            for m, u in zip(MACHINE_COLS, machine_utilization)
        ],
        "gantt": _make_gantt_rows(best_seq, best.start, best.completion, MACHINE_COLS, job_ids),
    }

    results_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("===== ACO RESULTS READY =====")
    print(f"Dataset jobs: {len(df)} | machines: {len(MACHINE_COLS)}")
    print(f"Best sequence: {' -> '.join(output['bestSequence'])}")
    print(f"Baseline makespan: {baseline.makespan:.2f}")
    print(f"ACO makespan: {best_makespan:.2f}")
    print(f"Improvement: {improvement:.2f}%")
    print(f"Saved JSON: {results_path}")


if __name__ == "__main__":
    main()
