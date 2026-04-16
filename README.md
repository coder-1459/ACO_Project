# ACO Manufacturing Job Scheduling (Production Dataset + Web Page)

This project demonstrates Ant Colony Optimization (ACO) for permutation flow-shop job scheduling using a production-style manufacturing dataset.

## Features

- Production-style dataset with 20 jobs and 5 machine stages
- ACO optimization to minimize makespan
- Metrics: makespan, waiting time, and machine idle time
- Static web dashboard (HTML/CSS/JS) with:
  - dataset table
  - convergence graph
  - machine utilization graph
  - Gantt-style schedule
  - best job sequence

## Project Files

- `dataset/production_jobs.csv` - production-level scheduling dataset
- `aco_engine.py` - reusable ACO and scheduling engine
- `run_cli.py` - runs ACO and exports `results/results.json`
- `web/index.html` - static web page
- `web/styles.css` - styling
- `web/script.js` - charts and table rendering
- `requirements.txt` - Python dependencies

## Setup

```bash
python -m pip install -r requirements.txt
```

## Generate Optimization Output

```bash
python run_cli.py
```

This creates `results/results.json` for the web page.

## Run Web Page

From project root:

```bash
python -m http.server 8000
```

Open: `http://localhost:8000/web/`

## Notes on dataset realism

The dataset includes `ProductFamily`, `BatchSize`, `DueDateHours`, and `Priority` with machine-wise process times. This mirrors commonly available fields from industrial production planning systems.

## How to Explain This Project (Viva / Presentation)

Use this simple flow while presenting:

1. **Problem statement**
   - "In manufacturing, multiple jobs must pass through multiple machines in order."
   - "The challenge is to decide job sequence to reduce total completion time (makespan), waiting, and machine idle time."

2. **Why ACO**
   - "This is a combinatorial optimization problem with many possible sequences."
   - "ACO is good because it balances exploration and exploitation using pheromone learning."

3. **Dataset**
   - "I used a production-style dataset with 20 jobs and 5 machine stages."
   - "Each row has product context (`ProductFamily`, `BatchSize`, `DueDateHours`, `Priority`) plus machine processing times."

4. **Method used**
   - "Each ant builds one full job sequence."
   - "Sequence quality is measured by makespan from flow-shop timing rules."
   - "Better sequences deposit more pheromone; pheromone also evaporates each iteration."
   - "After many iterations, the algorithm converges to a better schedule."

5. **What the web page shows**
   - Dataset table
   - Convergence graph (iteration vs best makespan)
   - Machine utilization chart
   - Gantt-style schedule
   - Final best job sequence

6. **Result statement**
   - "Compared to baseline FCFS sequence, ACO reduced makespan and improved flow efficiency."
   - "In this run, makespan improved from 1064 to 1040 (about 2.26%)."

### 2-Minute Demo Script

"This project optimizes manufacturing job scheduling using Ant Colony Optimization.  
We have 20 jobs and 5 machines in a flow-shop sequence.  
Normally, scheduling by simple order causes higher makespan and idle gaps.  
In ACO, multiple ants generate candidate sequences. Better sequences get stronger pheromone reinforcement, and evaporation prevents premature convergence.  
I run the optimizer using `python run_cli.py`, which generates `results/results.json`.  
Then the static web dashboard visualizes convergence, machine utilization, Gantt schedule, and the best sequence.  
The final result improves makespan from baseline 1064 to 1040, showing ACO can improve shop-floor scheduling decisions."

### Common Viva Questions and Answers

- **Q: What is makespan?**  
  **A:** Total time to complete all jobs; the completion time of the last job on the last machine.

- **Q: Why use metaheuristics instead of exact methods?**  
  **A:** For realistic scheduling sizes, exact methods become computationally expensive; metaheuristics provide high-quality solutions faster.

- **Q: What do alpha, beta, and rho control?**  
  **A:** `alpha` controls pheromone influence, `beta` controls heuristic influence, `rho` controls evaporation rate.

- **Q: How do you know optimization worked?**  
  **A:** We compare baseline and optimized KPIs (makespan, waiting, idle), and convergence trend shows progressive improvement.

- **Q: Future improvements?**  
  **A:** Hybrid ACO with local search, multi-objective scheduling, and real-time rescheduling for machine breakdowns/new jobs.
