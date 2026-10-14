# Inventory Simulator — Stage 1 Experiments

## Setup

- Item: `FOODS_3_288`
- Store: `CA_1`
- Evaluation period: 1,143 days after a 28-day warm-up
- Lead time: 5 days, with a 15% probability of an additional 2–5 days
- Inventory review period: 7 days
- Random seed: 42

## Results

| Service factor | Initial stock | Total demand | Units fulfilled | Lost sales | Days with lost sales |
|---:|---:|---:|---:|---:|---:|
| 0.3 | 119 | 18,534 | 15,939 | 2,595 | 13.65% |
| 0.8 | 133 | 18,534 | 16,337 | 2,197 | 11.37% |
| 1.6 | 154 | 18,534 | 16,991 | 1,543 | 8.22% |

## Findings

Increasing the service factor reduced lost sales for this item-store series. At a factor of 1.6, lost sales fell by 654 units, approximately 29.8%, compared with the baseline factor of 0.8.

The higher factor also required more initial inventory. A final policy recommendation requires additional evaluation of holding costs, replenishment costs, and service performance across many item-store series.

## Validation

- Demand reconciles to fulfilled units plus lost sales.
- Inventory did not become negative.
- Performance was measured after the warm-up period.
- Results are for one item-store series and should not be generalised to the full product population.
