from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

import numpy as np
import pandas as pd


MACHINE_COLS = [
    "M1_Cutting",
    "M2_Drilling",
    "M3_Welding",
    "M4_Painting",
    "M5_Assembly",
]


@dataclass
class ScheduleMetrics:
    completion: np.ndarray
    start: np.ndarray
    makespan: float
    total_waiting: float
    total_idle: float


def load_production_dataset(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    required = {"JobID", "ProductFamily", "BatchSize", "DueDateHours", "Priority", *MACHINE_COLS}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Dataset missing columns: {sorted(missing)}")
    return df


def evaluate_sequence(sequence: Sequence[int], processing_times: np.ndarray) -> ScheduleMetrics:
    n_jobs = len(sequence)
    n_machines = processing_times.shape[1]

    completion = np.zeros((n_jobs, n_machines), dtype=float)
    start = np.zeros((n_jobs, n_machines), dtype=float)

    for i in range(n_jobs):
        job_idx = sequence[i]
        for m in range(n_machines):
            if i == 0 and m == 0:
                start[i, m] = 0.0
            elif i == 0:
                start[i, m] = completion[i, m - 1]
            elif m == 0:
                start[i, m] = completion[i - 1, m]
            else:
                start[i, m] = max(completion[i - 1, m], completion[i, m - 1])
            completion[i, m] = start[i, m] + processing_times[job_idx, m]

    makespan = completion[-1, -1]

    waiting = 0.0
    for i in range(n_jobs):
        for m in range(1, n_machines):
            waiting += max(0.0, start[i, m] - completion[i, m - 1])

    idle = 0.0
    for m in range(n_machines):
        previous_end = 0.0
        for i in range(n_jobs):
            if start[i, m] > previous_end:
                idle += start[i, m] - previous_end
            previous_end = completion[i, m]

    return ScheduleMetrics(completion, start, makespan, waiting, idle)


class ACOFlowShop:
    def __init__(
        self,
        processing_times: np.ndarray,
        alpha: float = 1.0,
        beta: float = 2.0,
        rho: float = 0.12,
        q: float = 160.0,
        ants: int = 30,
        iterations: int = 120,
        seed: int = 42,
    ) -> None:
        self.processing_times = processing_times
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.ants = ants
        self.iterations = iterations

        self.n_jobs = processing_times.shape[0]
        self.rng = np.random.default_rng(seed)

        self.tau = np.ones((self.n_jobs, self.n_jobs), dtype=float)
        self.tau_start = np.ones(self.n_jobs, dtype=float)
        total_job_time = np.sum(processing_times, axis=1)
        self.eta = 1.0 / (total_job_time + 1e-9)

        self.best_sequence: List[int] = []
        self.best_makespan = float("inf")
        self.best_history: List[float] = []

    def _select_next_job(self, current_job: int | None, remaining: set[int]) -> int:
        candidates = list(remaining)
        desirability = []
        for job in candidates:
            pheromone = self.tau_start[job] if current_job is None else self.tau[current_job, job]
            score = (pheromone ** self.alpha) * (self.eta[job] ** self.beta)
            desirability.append(score)

        probabilities = np.array(desirability, dtype=float)
        prob_sum = probabilities.sum()
        if prob_sum <= 0:
            probabilities = np.full(len(candidates), 1.0 / len(candidates))
        else:
            probabilities /= prob_sum
        selected_index = self.rng.choice(len(candidates), p=probabilities)
        return candidates[selected_index]

    def _construct_solution(self) -> List[int]:
        remaining = set(range(self.n_jobs))
        sequence: List[int] = []
        current = None
        while remaining:
            nxt = self._select_next_job(current, remaining)
            sequence.append(nxt)
            remaining.remove(nxt)
            current = nxt
        return sequence

    def _evaporate(self) -> None:
        self.tau *= 1.0 - self.rho
        self.tau_start *= 1.0 - self.rho
        self.tau = np.clip(self.tau, 1e-6, 1e6)
        self.tau_start = np.clip(self.tau_start, 1e-6, 1e6)

    def _deposit(self, sequence: Sequence[int], makespan: float, weight: float = 1.0) -> None:
        delta = weight * (self.q / (makespan + 1e-9))
        self.tau_start[sequence[0]] += delta
        for i in range(len(sequence) - 1):
            a, b = sequence[i], sequence[i + 1]
            self.tau[a, b] += delta

    def run(self) -> tuple[List[int], float, List[float]]:
        for _ in range(self.iterations):
            ant_results: List[tuple[List[int], float]] = []
            for _ in range(self.ants):
                seq = self._construct_solution()
                metrics = evaluate_sequence(seq, self.processing_times)
                ant_results.append((seq, metrics.makespan))
                if metrics.makespan < self.best_makespan:
                    self.best_makespan = metrics.makespan
                    self.best_sequence = seq.copy()

            self._evaporate()
            for seq, makespan in ant_results:
                self._deposit(seq, makespan, weight=1.0)

            if self.best_sequence:
                self._deposit(self.best_sequence, self.best_makespan, weight=2.0)
            self.best_history.append(self.best_makespan)

        return self.best_sequence, self.best_makespan, self.best_history
