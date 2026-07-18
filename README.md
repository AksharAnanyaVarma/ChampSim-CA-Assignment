# Computer Architecture Assignment — Labs 9, 10 & 11
### Branch Prediction and Cache Replacement in ChampSim

This repo has all the code, results, and the report for the branch prediction and
last-level cache (LLC) part of the assignment. Everything was run on ChampSim (StonyBrook
DPC3 build) on WSL2 (Ubuntu 20.04, gcc 9.4), with 1M warmup and 10M simulated
instructions per run.

---

## 1. What I changed and where

All new files go in the normal ChampSim folders. Here is every file I added or changed.

### New branch predictors — in `branch/`
| File | Task | What it does |
|------|------|--------------|
| `branch/bullseye.bpred` | 1(c) | Modified Bullseye. Uses Hashed Perceptron as the base, plus a small "hard-to-predict" (H2P) table and a tiny per-branch perceptron. The tiny perceptron only overrides the base after it proves it is better. Fixed thresholds. |
| `branch/bullseye_adaptive.bpred` | 1(c) bonus | Same as above, but the thresholds change while it runs. They depend on how many branches are in the H2P table (`Exec ≥ 512+64N`, `Mispred ≥ 32+8N`, `Acc < f(N)`). It also drops a branch from the table if the base predictor clearly beats it. |

### New LLC replacement policies — in `replacement/`
| File | Task | What it does |
|------|------|--------------|
| `replacement/mru.llc_repl` | 2(c) | MRU. Throws out the most recently used block (opposite of LRU). Used as a bad-case policy. |
| `replacement/random.llc_repl` | 2(c) | Random. Throws out a random block, keeps no history. Fixed seed so runs repeat. |
| `replacement/hcit.llc_repl` | 2(e) bonus | HCIT. Built on SRRIP. Keeps a small PC table, finds the few PCs that cause most misses, and protects only those blocks. |

### Changed file — `inc/cache.h`
I edited the LLC settings in `inc/cache.h` for the Task 2 tests. Normal (spec) values and
what I changed them to:

| Setting | Spec value | Changed for |
|---------|-----------|-------------|
| `LLC_SET` | `NUM_CPUS*4096` (= 4 MB per core, 16-way, 64 B) | Task 2(a): `NUM_CPUS*1024` / `*2048` / `*4096` / `*8192` for 1 / 2 / 4 / 8 MB |
| `LLC_WAY` | `16` | Task 2(b): changed to `8` for the 8-way test |
| `L1D_WAY` | `8` | checked it was 8 (= 32 KB) |
| `L2C_SET` | `512` | checked it was 512 (= 256 KB) |

L1, L2, and all 64-byte line sizes stayed at the spec values.

### Bonus 4-core trace picker — `random_trace_gen.py`
`random_trace_gen.py` (in the repo root) picks the four traces for the multi-core test
from the 15-trace list, using a fixed seed. **Seed 42** picked: `619.lbm` (core 0),
`403.gcc` (core 1), `401.bzip2` (core 2), `620.omnetpp` (core 3). It writes
`selected_traces.txt` and `selection_log.json`, both in `results/`.

---

## 2. What is in this repo

```
.
├── README.md                     # this file
├── report.pdf                    # full results document (all tasks)
├── random_trace_gen.py           # 4-core trace picker (seed 42)
├── code/                         # copies of the files I added/changed
│   ├── bullseye.bpred
│   ├── bullseye_adaptive.bpred
│   ├── mru.llc_repl
│   ├── random.llc_repl
│   └── hcit.llc_repl
├── results/
│   ├── tables/                   # the CSV files used to build the report
│   ├── raw/                      # raw ChampSim output text files
│   ├── selected_traces.txt       # trace picker output
│   └── selection_log.json        # trace picker output (seed, time, picks)
└── graphs/                       # all the graphs used in the report
```

To use the code: copy the `.bpred` files into ChampSim's `branch/` folder and the
`.llc_repl` files into `replacement/`, then build (see below).

---

## 3. How to build and run

Same commands as the ChampSim sheet.

**Give run permissions once:**
```bash
chmod +x build_champsim.sh run_champsim.sh
```

**Build command:**
```bash
./build_champsim.sh ${BRANCH} ${L1I_PREF} ${L1D_PREF} ${L2C_PREF} ${LLC_PREF} ${LLC_REPL} ${NUM_CORE}
```

### Task 1 — branch predictors (single core)
```bash
./build_champsim.sh bimodal            no no no no lru 1
./build_champsim.sh gshare             no no no no lru 1
./build_champsim.sh perceptron         no no no no lru 1
./build_champsim.sh hashed_perceptron  no no no no lru 1
./build_champsim.sh bullseye           no no no no lru 1
./build_champsim.sh bullseye_adaptive  no no no no lru 1

# then run each one on the four traces, for example:
./run_champsim.sh hashed_perceptron-no-no-no-no-lru-1core 1 10 605.mcf_s-665B.champsimtrace.xz
```

### Task 1 — four-core mix (seed 42)
```bash
./build_champsim.sh bullseye_adaptive no no no no lru 4
./run_4core.sh bullseye_adaptive-no-no-no-no-lru-4core 1 10 0 \
  619.lbm_s-3766B.champsimtrace.xz 403.gcc-16B.champsimtrace.xz \
  401.bzip2-277B.champsimtrace.xz 620.omnetpp_s-874B.champsimtrace.xz
```

### Task 2 — LLC replacement policies
The last build option is the LLC policy. `lru`, `srrip`, `drrip`, `ship` already come with
ChampSim. `mru`, `random`, `hcit` are the ones I added.
```bash
./build_champsim.sh hashed_perceptron no no no no ship   1
./build_champsim.sh hashed_perceptron no no no no mru    1
./build_champsim.sh hashed_perceptron no no no no random 1
./build_champsim.sh hashed_perceptron no no no no hcit   1
```

### Task 2 — size and associativity tests
Change `LLC_SET` (for size) or `LLC_WAY` (for associativity) in `inc/cache.h` as shown in
Section 1, rebuild, and run again. Each size and policy was run for both 1 core and 4 cores.

Results show up in `results_10M/` as text files with Cumulative IPC, hit rates, miss
counts, and LLC writes.

---

## 4. Results

All the numbers — MPKI, accuracy, IPC, execution time for the predictors, and IPC,
L1/L2/LLC miss rates, LLC hit rate, LLC writes, and execution time for the caches — are in
tables and graphs in `report.pdf`, for both 1-core and 4-core. The raw output files and the
CSVs are in `results/`.

**Short version of the findings:** predictors get better in the order Bimodal → GShare →
Perceptron → Hashed Perceptron. The adaptive Bullseye gives the lowest MPKI on 605.mcf
(17.19) and the best 4-core cumulative IPC. For the cache, a bigger LLC only helps the
memory-heavy trace 605.mcf, and associativity barely matters at 4 MB. SHIP is the best
replacement policy, and my HCIT policy beats LRU on 605.mcf and comes just behind SHIP.

---
