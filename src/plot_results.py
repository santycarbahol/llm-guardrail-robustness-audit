"""Combine results/*.csv from any number of models into figures and a summary table.

    python src/plot_results.py            # reads results/, writes figures/

Outputs:
  figures/asr_heatmap.png   attack x defense success rate, one panel per model
  figures/summary.md        per-defense ASR and utility for every model (table view)
"""
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from attacks import ATTACKS
from defenses import DEFENSES

RESULTS, FIGURES = Path("results"), Path("figures")

# Single-hue sequential ramp (blue 100 -> 700), light = low success.
RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
SURFACE, INK, INK_2 = "#fcfcfb", "#0b0b0b", "#52514e"
CMAP = LinearSegmentedColormap.from_list("asr", RAMP)


def load():
    """-> {model: {(attack, defense): {"injected": [...], "utility": [...]}}}"""
    data = defaultdict(lambda: defaultdict(lambda: {"injected": [], "utility": []}))
    for path in sorted(RESULTS.glob("*.csv")):
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["error"]:
                    continue
                cell = data[r["model"]][(r["attack"], r["defense"])]
                cell["injected"].append(int(r["injected"]))
                cell["utility"].append(int(r["utility"]))
    return data


def ordered(keys, reference):
    """Keep the attack/defense order from the source files; unknown names go last."""
    keys = set(keys)
    return [k for k in reference if k in keys] + sorted(keys - set(reference))


def rate(values):
    return sum(values) / len(values) if values else np.nan


def plot_heatmaps(data, attacks, defenses):
    models = list(data)
    ncols = min(3, len(models))
    nrows = -(-len(models) // ncols)
    fig, axes = plt.subplots(
        nrows, ncols, squeeze=False, facecolor=SURFACE,
        figsize=(0.95 * len(defenses) * ncols + 2.2, 0.42 * len(attacks) * nrows + 1.4),
    )
    for ax in axes.flat[len(models):]:
        ax.axis("off")

    for ax, model in zip(axes.flat, models):
        grid = np.array([[rate(data[model][(a, d)]["injected"]) for d in defenses] for a in attacks])
        ax.set_facecolor(SURFACE)
        # Surface-colored gaps between cells keep the grid legible.
        ax.pcolormesh(grid, cmap=CMAP, vmin=0, vmax=1, edgecolors=SURFACE, linewidth=2)
        for i in range(len(attacks)):
            for j in range(len(defenses)):
                v = grid[i, j]
                label = "–" if np.isnan(v) else f"{v:.0%}"
                ax.text(j + 0.5, i + 0.5, label, ha="center", va="center", fontsize=8,
                        color=SURFACE if v >= 0.5 else INK)
        ax.set_xticks(np.arange(len(defenses)) + 0.5, defenses, rotation=30, ha="right",
                      fontsize=8, color=INK_2)
        ax.set_yticks(np.arange(len(attacks)) + 0.5, attacks, fontsize=8, color=INK_2)
        ax.invert_yaxis()
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(model, fontsize=10, color=INK, loc="left")

    fig.suptitle("Injection success rate by attack and defense (lower is better)",
                 x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout()
    out = FIGURES / "asr_heatmap.png"
    fig.savefig(out, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    return out


def write_summary(data, attacks, defenses):
    real_attacks = [a for a in attacks if a != "none"]  # "none" is the no-attack control
    lines = ["# Results summary", "",
             "ASR = injection success rate across all attacks (excluding the no-attack control).",
             "Utility = share of summaries that covered the document's key facts.", ""]
    for model, cells in data.items():
        lines += [f"## {model}", "", "| defense | ASR | utility | utility, no attack |",
                  "|---|---:|---:|---:|"]
        for d in defenses:
            inj = [v for a in real_attacks for v in cells[(a, d)]["injected"]]
            util = [v for a in real_attacks for v in cells[(a, d)]["utility"]]
            clean = cells[("none", d)]["utility"]
            fmt = lambda x: "–" if np.isnan(x) else f"{x:.0%}"
            lines.append(f"| {d} | {fmt(rate(inj))} | {fmt(rate(util))} | {fmt(rate(clean))} |")
        lines.append("")
    out = FIGURES / "summary.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main():
    data = load()
    if not data:
        raise SystemExit(f"No results found in {RESULTS}/ - run src/run_grid.py first.")
    attacks = ordered({a for m in data.values() for a, _ in m}, list(ATTACKS))
    defenses = ordered({d for m in data.values() for _, d in m}, list(DEFENSES))
    FIGURES.mkdir(exist_ok=True)
    print(plot_heatmaps(data, attacks, defenses))
    print(write_summary(data, attacks, defenses))


if __name__ == "__main__":
    main()
