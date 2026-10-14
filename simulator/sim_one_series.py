
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. Locate the downloaded M5 files
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "m5"

sales_path = DATA_DIR / "sales_train_validation.csv"
calendar_path = DATA_DIR / "calendar.csv"
prices_path = DATA_DIR / "sell_prices.csv"

for path in [sales_path, calendar_path, prices_path]:
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}\n"
            "Check that all three CSVs are in data/m5/."
        )


# --------------------------------------------------
# 2. Select one reasonably busy item in CA_1
# --------------------------------------------------

header = pd.read_csv(sales_path, nrows=0).columns.tolist()

day_cols = sorted(
    [
        col for col in header
        if col.startswith("d_") and col[2:].isdigit()
    ],
    key=lambda col: int(col[2:])
)

metadata_cols = [
    "id", "item_id", "dept_id",
    "cat_id", "store_id", "state_id"
]

candidate_chunks = []

for chunk in pd.read_csv(
    sales_path,
    usecols=metadata_cols + day_cols,
    chunksize=2000
):
    chunk = chunk[chunk["store_id"] == "CA_1"].copy()

    if not chunk.empty:
        chunk["total_units"] = chunk[day_cols].sum(axis=1)
        candidate_chunks.append(chunk)

if not candidate_chunks:
    raise ValueError("No sales records found for store CA_1.")

candidates = pd.concat(candidate_chunks, ignore_index=True)

# Select the 51st highest-selling item, rather than the top seller.
candidates = candidates.sort_values(
    "total_units", ascending=False
).reset_index(drop=True)

row = candidates.iloc[min(50, len(candidates) - 1)]

item_id = row["item_id"]
store_id = row["store_id"]

print("Selected item:", item_id)
print("Selected store:", store_id)
print("Historical total units:", int(row["total_units"]))


# --------------------------------------------------
# 3. Find the first recorded price week
# --------------------------------------------------

item_price_chunks = []

for chunk in pd.read_csv(
    prices_path,
    usecols=["store_id", "item_id", "wm_yr_wk", "sell_price"],
    chunksize=500_000
):
    matching = chunk[
        (chunk["store_id"] == store_id)
        & (chunk["item_id"] == item_id)
    ]

    if not matching.empty:
        item_price_chunks.append(matching)

if not item_price_chunks:
    raise ValueError("No price records found for the selected item-store.")

item_prices = pd.concat(item_price_chunks, ignore_index=True)

first_week = int(item_prices["wm_yr_wk"].min())

calendar = pd.read_csv(
    calendar_path,
    usecols=["d", "wm_yr_wk"]
)

day_weeks = (
    calendar.set_index("d")
    .loc[day_cols, "wm_yr_wk"]
    .to_numpy()
)

start_candidates = np.flatnonzero(day_weeks >= first_week)

if len(start_candidates) == 0:
    raise ValueError("Could not find a sales day for the first price week.")

start = int(start_candidates[0])

# Demand from the first recorded price week onwards.
all_demand = row[day_cols].astype("int64").to_numpy()[start:]

# Use the first 28 post-price days as a warm-up period.
warmup_days = 28

if len(all_demand) <= warmup_days:
    raise ValueError("Not enough observed days after the warm-up period.")

initial_history = all_demand[:warmup_days]

# Evaluate inventory performance only after the warm-up.
demand = all_demand[warmup_days:]
T = len(demand)

print("First observed sales day:", day_cols[start])
print("Simulation starts on:", day_cols[start + warmup_days])
print("Warm-up days:", warmup_days)
print("Days simulated:", T)


# --------------------------------------------------
# 4. Reusable inventory simulation function
# --------------------------------------------------

def simulate(all_demand, lead, z, delay_p, seed, review=7, warm=28):
    all_demand = np.asarray(all_demand, dtype=np.int64)

    if len(all_demand) <= warm:
        raise ValueError("Demand history must exceed the warm-up period.")

    if np.any(all_demand < 0):
        raise ValueError("Demand cannot be negative.")

    # Reserve the first 28 observed days for initialisation.
    initial_history = all_demand[:warm]
    demand = all_demand[warm:]
    T = len(demand)

    def target(history):
        return (
            history.mean() * (lead + review)
            + z * history.std() * np.sqrt(lead + review)
        )

    initial_target = target(initial_history)
    initial_stock = int(np.ceil(initial_target))
    on_hand = initial_stock
    on_order = 0

    # Pre-generate delays so every service factor faces the
    # same potential supplier-delay sequence.
    n_reviews = (T + review - 1) // review
    rng = np.random.default_rng(seed)

    delayed = rng.random(n_reviews) < delay_p
    extensions = rng.integers(2, 6, size=n_reviews)
    delays = np.where(delayed, extensions, 0)

    arrivals = np.zeros(T + lead + 6, dtype=np.int64)
    logs = []

    for t, units in enumerate(demand):
        # Stock at the beginning of the day, before delivery.
        opening_on_hand = on_hand

        received = int(arrivals[t])
        on_hand += received
        on_order -= received

        available_before_demand = on_hand
        units_demanded = int(units)
        fulfilled = min(units_demanded, on_hand)
        lost = units_demanded - fulfilled
        on_hand -= fulfilled

        order_qty = 0

        # Review every seven days, beginning on evaluation day 0.
        if t % review == 0:
            history_end = warm + t
            history = all_demand[history_end - warm:history_end]

            order_qty = max(
                0,
                int(np.ceil(target(history))) - on_hand - on_order
            )

            if order_qty > 0:
                delay = int(delays[t // review])
                arrival_day = t + lead + delay
                arrivals[arrival_day] += order_qty
                on_order += order_qty

        logs.append({
            "evaluation_day": t,
            "opening_on_hand": opening_on_hand,
            "received": received,
            "available_before_demand": available_before_demand,
            "demand": units_demanded,
            "fulfilled": fulfilled,
            "lost_sales": lost,
            "ending_on_hand": on_hand,
            "order_qty": order_qty,
            "on_order_end": on_order
        })

    results = pd.DataFrame(logs)

    # Validate inventory and demand reconciliation.
    assert (
        results["fulfilled"] + results["lost_sales"]
        == results["demand"]
    ).all(), "Demand reconciliation failed."

    assert (
        results["ending_on_hand"] >= 0
    ).all(), "Inventory became negative."

    return results, initial_target, initial_stock


# --------------------------------------------------
# 5. Compare all three service-factor settings
# --------------------------------------------------

lead_time = 5
review_period = 7
delay_probability = 0.15
warmup_days = 28
random_seed = 42

service_factors = [0.3, 0.8, 1.6]

experiment_results = {}
summaries = []

for z in service_factors:
    results, initial_target, initial_stock = simulate(
        all_demand=all_demand,
        lead=lead_time,
        z=z,
        delay_p=delay_probability,
        seed=random_seed,
        review=review_period,
        warm=warmup_days
    )

    experiment_results[z] = results

    total_demand = int(results["demand"].sum())
    fulfilled_units = int(results["fulfilled"].sum())
    lost_units = int(results["lost_sales"].sum())

    fill_rate = (
        fulfilled_units / total_demand * 100
        if total_demand else 0.0
    )

    summaries.append({
        "service_factor": z,
        "initial_target": round(initial_target, 2),
        "initial_stock": initial_stock,
        "total_demand": total_demand,
        "fulfilled": fulfilled_units,
        "lost_sales": lost_units,
        "fill_rate_pct": round(fill_rate, 2),
        "lost_sales_days_pct": round(
            (results["lost_sales"] > 0).mean() * 100, 2
        ),
        "zero_ending_stock_days_pct": round(
            (results["ending_on_hand"] == 0).mean() * 100, 2
        ),
        "avg_ending_on_hand": round(
            results["ending_on_hand"].mean(), 2
        )
    })

    print(
        f"Completed service_factor={z}; "
        f"initial_stock={initial_stock}; "
        f"lost_sales={lost_units:,}"
    )

summary = pd.DataFrame(summaries)

print("\n--- Comparison across service factors ---")
print(summary.to_string(index=False))

# Inspect the first 40 evaluation days at the baseline factor.
print("\n--- First 40 evaluation days: service_factor=0.8 ---")
print(
    experiment_results[0.8]
    .head(40)
    .to_string(index=False)
)

print("\nAll simulation runs passed the inventory checks.")



# --------------------------------------------------
# 6. Robustness check across five supplier-delay seeds
# --------------------------------------------------

seed_results = []

for seed in range(1, 6):
    for z in [0.3, 0.8, 1.6]:
        results, initial_target, initial_stock = simulate(
            all_demand=all_demand,
            lead=lead_time,
            z=z,
            delay_p=delay_probability,
            seed=seed,
            review=review_period,
            warm=warmup_days
        )

        total_demand = int(results["demand"].sum())
        fulfilled = int(results["fulfilled"].sum())
        lost = int(results["lost_sales"].sum())

        seed_results.append({
            "seed": seed,
            "service_factor": z,
            "fill_rate_pct": (
                fulfilled / total_demand * 100
                if total_demand else 0
            ),
            "lost_sales": lost,
            "lost_sales_days_pct": (
                results["lost_sales"].gt(0).mean() * 100
            ),
            "avg_ending_on_hand": (
                results["ending_on_hand"].mean()
            )
        })

seed_df = pd.DataFrame(seed_results)

print("\n--- Results by seed ---")
print(seed_df.to_string(index=False))

print("\n--- Fill-rate range across five seeds ---")
fill_summary = seed_df.groupby("service_factor").agg(
    min_fill_rate=("fill_rate_pct", "min"),
    mean_fill_rate=("fill_rate_pct", "mean"),
    max_fill_rate=("fill_rate_pct", "max"),
    min_lost_sales=("lost_sales", "min"),
    max_lost_sales=("lost_sales", "max")
).round(2)

print(fill_summary.to_string())
