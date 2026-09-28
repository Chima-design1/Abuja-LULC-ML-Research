from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent

AREA_FILE = (
    ROOT
    / "outputs"
    / "area_statistics"
    / "LULC_Area_Statistics_Year_Specific.csv"
)

NET_CHANGE_FILE = (
    ROOT
    / "outputs"
    / "change_analysis"
    / "LULC_Net_Changes_Year_Specific.csv"
)

TRANSITION_FILE = (
    ROOT
    / "outputs"
    / "transition_analysis"
    / "transition_areas_2018_2024.csv"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "change_figures"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FIGURE 1 — LULC AREA TRENDS
# ============================================================

area_df = pd.read_csv(AREA_FILE)

plt.figure(figsize=(10, 6))

for class_name in [
    "Built-up",
    "Vegetation",
    "Bare land",
    "Water",
    "Cropland",
]:

    subset = area_df[
        area_df["class_name"] == class_name
    ].sort_values("year")

    plt.plot(
        subset["year"],
        subset["area_km2"],
        marker="o",
        linewidth=2,
        label=class_name,
    )

plt.title(
    "Abuja LULC Area Trends, 2018–2024"
)

plt.xlabel("Year")
plt.ylabel("Area (km²)")

plt.xticks(
    [2018, 2020, 2022, 2024]
)

plt.grid(
    alpha=0.3
)

plt.legend()

plt.tight_layout()

output = (
    OUTPUT_DIR
    / "Figure_1_LULC_Area_Trends.png"
)

plt.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(
    f"Saved: {output}"
)


# ============================================================
# FIGURE 2 — NET CHANGE BY PERIOD
# ============================================================

net_df = pd.read_csv(
    NET_CHANGE_FILE
)

period_labels = (
    net_df["from_year"].astype(str)
    + "–"
    + net_df["to_year"].astype(str)
)

classes = [
    "Built-up",
    "Vegetation",
    "Bare land",
    "Water",
    "Cropland",
]

x = range(len(period_labels))

width = 0.15

plt.figure(figsize=(12, 7))

for i, class_name in enumerate(classes):

    values = net_df[
        f"{class_name}_change_km2"
    ]

    positions = [
        value + (i - 2) * width
        for value in x
    ]

    plt.bar(
        positions,
        values,
        width=width,
        label=class_name,
    )

plt.axhline(
    0,
    linewidth=1,
)

plt.title(
    "Net LULC Area Change by Period"
)

plt.xlabel("Period")
plt.ylabel("Net change (km²)")

plt.xticks(
    list(x),
    period_labels,
)

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.legend()

plt.tight_layout()

output = (
    OUTPUT_DIR
    / "Figure_2_Net_LULC_Change.png"
)

plt.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(
    f"Saved: {output}"
)


# ============================================================
# FIGURE 3 — DOMINANT 2018–2024 TRANSITIONS
# ============================================================

transition_df = pd.read_csv(
    TRANSITION_FILE
)

# Remove unchanged transitions.
transition_df = transition_df[
    transition_df["from_class_name"]
    != transition_df["to_class_name"]
].copy()

transition_df[
    "transition"
] = (
    transition_df["from_class_name"]
    + " → "
    + transition_df["to_class_name"]
)

top_transitions = (
    transition_df
    .sort_values(
        "area_km2",
        ascending=False,
    )
    .head(10)
    .sort_values(
        "area_km2",
        ascending=True,
    )
)

plt.figure(figsize=(11, 7))

plt.barh(
    top_transitions["transition"],
    top_transitions["area_km2"],
)

plt.title(
    "Dominant LULC Transitions, 2018–2024"
)

plt.xlabel("Transition area (km²)")
plt.ylabel("LULC transition")

plt.grid(
    axis="x",
    alpha=0.3,
)

plt.tight_layout()

output = (
    OUTPUT_DIR
    / "Figure_3_Dominant_LULC_Transitions.png"
)

plt.savefig(
    output,
    dpi=300,
    bbox_inches="tight",
)

plt.close()

print(
    f"Saved: {output}"
)


print("\n" + "=" * 60)
print("CHANGE FIGURES COMPLETE")
print("=" * 60)

print(
    f"Figures saved to: {OUTPUT_DIR}"
)
