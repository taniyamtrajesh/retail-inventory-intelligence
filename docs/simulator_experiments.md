# Inventory Simulator: Single-Series Experiments

## 1. Objective

Build and test a single-item, single-store inventory simulator to understand how the safety-stock factor affects inventory availability and lost sales.

The experiment uses historical M5 retail sales as the demand input and compares three inventory policies with different safety-stock factors.

## 2. Simulation Setup

| Parameter | Value |
|---|---|
| Dataset | M5 retail sales dataset |
| Selected item | `FOODS_3_288` |
| Store | `CA_1` |
| Historical total units for selected series | 18,793 |
| First observed sales day | `d_743` |
| Simulation evaluation start | `d_771` |
| Warm-up period | 28 days |
| Evaluation period | 1,143 days |
| Nominal supplier lead time | 5 days |
| Inventory review period | 7 days |
| Probability of delivery delay | 15% |
| Additional delay when triggered | 2–5 days |
| Random seed | 42 |
| Safety-stock factors tested | 0.3, 0.8, 1.6 |

## 3. Methodology

The simulator uses the first recorded price week as a proxy for the beginning of observed product availability.

The first 28 post-price days are reserved for initialising inventory and estimating the order-up-to target. These days are excluded from the evaluation period.

The replenishment target is calculated as:

**Target stock = average recent demand × (lead time + review period) + safety-stock adjustment**

The safety-stock adjustment uses the selected factor, the standard deviation of recent demand, and the square root of the lead time plus review period.

Inventory is reviewed every seven simulated days. Orders are placed when inventory on hand plus inventory on order falls below the target. Deliveries arrive after the nominal lead time, with a probability of an additional delay.

All three experiments use the same historical demand series, random seed, and supplier-delay schedule so that differences between policies can be compared more consistently.

## 4. Experimental Results

| Metric | Factor 0.3 | Factor 0.8 | Factor 1.6 |
|---|---:|---:|---:|
| Initial target stock | 118.98 | 132.28 | 153.56 |
| Initial stock (rounded) | 119 | 133 | 154 |
| Total demand | 18,534 | 18,534 | 18,534 |
| Units fulfilled | 16,181 | 16,640 | 17,203 |
| Lost sales (units) | 2,353 | 1,894 | 1,331 |
| Fill rate | 87.30% | 89.78% | 92.82% |
| Days with lost sales | 12.95% | 10.41% | 7.26% |
| Days ending at zero stock | 13.56% | 11.37% | 7.87% |
| Average ending on-hand inventory | 86.79 | 97.66 | 116.57 |

*Fill rate = units fulfilled ÷ total demand. Average ending on-hand inventory is the mean daily closing stock and excludes inventory still in transit.*

## 5. Key Findings

### Effect of the safety-stock factor

Increasing the factor from 0.3 to 1.6 increased the fill rate from 87.30% to 92.82% and reduced lost sales from 2,353 to 1,331 units.

Compared with the default setting of 0.8, the factor of 1.6 reduced lost sales by 563 units, approximately 29.7%.

### Inventory trade-off

The higher factor also increased average ending on-hand inventory from 97.66 units at a factor of 0.8 to 116.57 units at a factor of 1.6.

This shows, for this series, the trade-off between carrying more inventory and reducing unmet demand. With the default setting of 0.8, the fill rate was 89.78%, with average ending inventory of 97.66 units. Increasing the service factor to 1.6 raised the fill rate to 92.82%, a gain of 3.04 percentage points, while increasing average ending inventory to 116.57 units—about 18.91 additional units of stock on average. That is a measurable service improvement, but it requires more inventory. These results apply to this item-store series and should not be generalized to the full dataset.

### Remaining stockout risk

Even with a factor of 1.6, 7.26% of evaluation days experienced lost sales.

Potential contributors include supplier delays, variability in demand, and the limitations of the replenishment rule. These explanations require further testing rather than being treated as proven causes.

## 6. Assumptions and Limitations

- Historical recorded sales are treated as the demand input for the simulation. True demand during historical stockouts is unknown.
- Unmet simulated demand is recorded as lost sales; customers do not backorder.
- The first recorded price week is an availability proxy and does not confirm physical stock availability.
- Initial inventory is set using the first 28 days of post-price demand and the selected safety-stock factor.
- The replenishment rule uses recent demand history and a nominal lead time, while actual simulated deliveries can be delayed.
- The experiments cover only one item-store series and cannot be generalised to the full dataset.
- No inventory holding costs, ordering costs, or explicit lost-sales financial costs have been included.

## 7. Validation

The simulation passed the following checks for all three policies:

- Fulfilled units plus lost sales equals total demand.
- Ending inventory never becomes negative.
- The evaluation period excludes the 28-day warm-up.
- The same demand history and seeded supplier-delay schedule are used across the three policy comparisons.

## 8. Next Steps

1. Refactor the simulator to support multiple item-store series.
2. Select a diverse sample of 100 series, including both fast-moving and slow-moving products.
3. Compare the same three safety-stock factors across the sample.
4. Report fill rate, lost-sales-day share, and average ending inventory by demand-volume group.
5. Evaluate whether slow-moving products need a separate replenishment rule.
6. Introduce inventory and replenishment costs before recommending a policy for production.

## 9. Sensitivity Analysis Across Five Supplier-Delay Seeds

To check whether the policy comparison depended on a single random supplier-delay schedule, the three service factors were evaluated with seeds 1 through 5. For each seed, all three policies used the same generated supplier-delay schedule.

| Seed | 0.3 | 0.8 | 1.6 |
|---:|---:|---:|---:|
| 1 | 85.99% | 88.39% | 91.79% |
| 2 | 88.18% | 90.53% | 93.65% |
| 3 | 88.08% | 90.65% | 93.84% |
| 4 | 88.43% | 90.95% | 94.15% |
| 5 | 86.45% | 88.91% | 92.39% |

### Interpretation

The ordering was consistent across all five seeds: factor 1.6 achieved a higher fill rate than 0.8, which in turn outperformed 0.3. The ranges across seeds describe variation in the absolute fill-rate levels; the within-seed comparison shows that the relative policy ranking did not change across these five tested schedules.

This supports the conclusion that the observed service-level improvement was not limited to a single supplier-delay schedule for this series. However, five seeds and one item-store combination are not sufficient to establish performance across the full product population.

