
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
# 4. Configure the inventory policy
# --------------------------------------------------

rng = np.random.default_rng(42)

lead_time = 5           # Expected delivery lead time in days
review_period = 7       # Check inventory every seven days
service_factor = 1.6    # Controls safety stock
print("Service factor used:", service_factor)
delay_probability = 0.15

# Begin with approximately 12 days of stock,
# estimated using the first 28 days of demand.
initial_target = (
    initial_history.mean() * (lead_time + review_period)
    + service_factor
    * initial_history.std()
    * np.sqrt(lead_time + review_period)
)

print("Initial target stock:", initial_target)

on_hand = int(np.ceil(initial_target))

on_order = 0
arrivals = np.zeros(len(demand) + 30, dtype=np.int64)

logs = []


# --------------------------------------------------
# 5. Simulate demand, stock and replenishment
# --------------------------------------------------

# --------------------------------------------------
# 5. Simulate demand, stock and replenishment
# --------------------------------------------------

for t in range(len(demand)):

    # Record stock available at the start of the day,
    # before receiving today's delivery.
    opening_on_hand = on_hand

    # Receive any orders due today.
    received = int(arrivals[t])
    on_hand += received
    on_order -= received

    # Fulfil demand using available stock.
    units_demanded = int(demand[t])
    fulfilled = min(units_demanded, on_hand)
    lost_sales = units_demanded - fulfilled

    on_hand -= fulfilled

    # Log the correct day, accounting for the warm-up period.
    logs.append({
        "day": day_cols[start + warmup_days + t],
        "demand": units_demanded,
        "fulfilled": fulfilled,
        "lost_sales": lost_sales,
        "opening_on_hand": opening_on_hand,
        "ending_on_hand": on_hand,
        "on_order": on_order,
        "received": received
    })

    # Review inventory every seven simulated days.
    if t % review_period == 0:

        history_end = warmup_days + t
        recent_demand = all_demand[history_end - 28:history_end]

        target_stock = (
            recent_demand.mean() * (lead_time + review_period)
            + service_factor
            * recent_demand.std()
            * np.sqrt(lead_time + review_period)
        )

        order_qty = max(
            0,
            int(np.ceil(target_stock)) - on_hand - on_order
        )

        if order_qty > 0:
            delayed = rng.random() < delay_probability

            extra_delay = (
                int(rng.integers(2, 6)) if delayed else 0
            )

            delivery_days = lead_time + extra_delay
            arrivals[t + delivery_days] += order_qty
            on_order += order_qty

# --------------------------------------------------
# 6. Check and summarise the results
# --------------------------------------------------

results = pd.DataFrame(logs)

assert (
    results["fulfilled"] + results["lost_sales"]
    == results["demand"]
).all(), "Demand reconciliation failed."

assert (
    results["ending_on_hand"] >= 0
).all(), "Inventory became negative."

assert (
    results["opening_on_hand"] >= 0
).all(), "Opening inventory became negative."

print("\nFirst 40 simulation days:")
print(results.head(40).to_string(index=False))

print("\n--- Simulation summary ---")
print("Total demand:", f"{results['demand'].sum():,}")
print("Units fulfilled:", f"{results['fulfilled'].sum():,}")
print("Lost sales:", f"{results['lost_sales'].sum():,}")

print(
    "Days with lost sales:",
    f"{(results['lost_sales'] > 0).mean() * 100:.2f}%"
)

print(
    "Days ending at zero stock:",
    f"{(results['ending_on_hand'] == 0).mean() * 100:.2f}%"
)

print("\nInventory reconciliation checks passed.")
