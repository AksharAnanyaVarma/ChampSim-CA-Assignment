#!/usr/bin/env python3
"""Randomly selects 4 traces from the assignment's 15-trace list for 4-core simulation."""
import random, sys, json, datetime

TRACES = [
    "401.bzip2-277B", "403.gcc-16B", "434.zeusmp-10B", "437.leslie3d-273B",
    "450.soplex-92B", "456.hmmer-327B", "462.libquantum-1343B", "482.sphinx3-1522B",
    "605.mcf_s-1644B", "605.mcf_s-665B", "619.lbm_s-3766B", "620.omnetpp_s-874B",
    "621.wrf_s-8100B", "623.xalancbmk_s-700B", "628.pop2_s-17B",
]

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
random.seed(seed)
selected = random.sample(TRACES, 4)

print("Random Trace Generator for 4-Core Simulation")
print("Pool size:", len(TRACES))
print("Seed:", seed)
print("\nSelected traces:")
for i, t in enumerate(selected):
    print("  Core %d: %s.champsimtrace.xz" % (i, t))

with open("selected_traces.txt", "w") as f:
    f.write(" ".join(t + ".champsimtrace.xz" for t in selected) + "\n")

with open("selection_log.json", "w") as f:
    json.dump({
        "seed": seed,
        "timestamp": str(datetime.datetime.now()),
        "pool": TRACES,
        "selected": selected
    }, f, indent=2)

print("\nWrote selected_traces.txt and selection_log.json")
