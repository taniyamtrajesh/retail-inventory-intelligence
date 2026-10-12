# Quick EDA — Retail Inventory Intelligence

## Dataset Overview

- **Sales records:** 30,490 item-store rows
- **Daily sales columns:** 1,913
- **Weekly price records:** 6,841,121
- **Calendar records:** 1,969

## 1. Zero-Sales Frequency and Observed Availability

- Total item-store-days: 58,327,370
- Total zero-sales item-store-days: 39,777,094
- Overall zero-sales share: 68.20%
- Days before the first recorded price: 12,299,413
- Zero-sales share before the first recorded price: 100.00%
- Days with a recorded price: 46,027,957
- Zero-sales share on days with a recorded price: 59.70%

### Business Interpretation

The overall zero-sales share of 68.20% includes days before the first recorded price, when no positive sales were observed. After separating these periods, 59.70% of days with a recorded price still had zero sales.

For demand analysis, the first recorded price week will serve as a proxy for the start of observed product availability. Pre-price days will be flagged separately rather than automatically interpreted as weak demand. A recorded price does not guarantee physical stock availability.

## 2. Observed Product Availability and Launch Timing

- Item-store pairs: 30,490
- Pairs without a recorded price in the first four calendar weeks: 17,691 (58.02%)
- Duplicate weekly price keys: 0
- Positive-sales days without a price record: 0
- Units sold without a price record: 0

### Business Interpretation

All 12,299,413 days without a recorded price fell before the first recorded price week for the corresponding item-store pair. No positive sales were observed on those days. This supports using the first recorded price week as a practical availability proxy for this dataset, while recognising that pricing records do not confirm physical inventory.

### Design Decision

Separate pre-price periods from demand observations. Calculate demand and slow-moving-product metrics using days at or after the first recorded price week, while retaining an availability flag so that pre-price periods are not mistaken for normal zero demand.

## 3. Price Changes

- **Total recorded price changes:** 78,815
- **Average price changes per item-store pair:** 2.58
- **Median price changes per item-store pair:** 2
- **Pairs with at least one recorded price change:** 72.95%
- **Items with the most changes:** 

| Item ID | Total changes across stores | Average changes per store | Number of stores |
|---|---:|---:|---:|
| FOODS_3_822 | 198 | 19.8 | 10 |
| FOODS_3_615 | 180 | 18.0 | 10 |
| FOODS_3_274 | 179 | 17.9 | 10 |
| FOODS_3_029 | 169 | 16.9 | 10 |
| FOODS_1_095 | 166 | 16.6 | 10 |
| FOODS_1_129 | 166 | 16.6 | 10 |
| FOODS_3_432 | 165 | 16.5 | 10 |
| FOODS_3_090 | 164 | 16.4 | 10 |
| FOODS_1_096 | 164 | 16.4 | 10 |
| FOODS_3_738 | 159 | 15.9 | 10 |

The item `FOODS_3_822` had the highest number of recorded price changes in this analysis, followed by `FOODS_3_615` and `FOODS_3_274`. All ten items were recorded across 10 stores, making their total change counts comparable in terms of store coverage.

These results identify products worth investigating further for pricing and demand patterns. However, the number of price changes does not indicate how large the changes were or whether they increased or decreased sales.


### Business Interpretation

Price changes occurred across 72.95% of item-store pairs, suggesting that price variation is a meaningful factor to consider when analysing retail demand. The average was 2.58 changes per pair, while the median was 2.

Changes in price may affect customer demand and the units sold for a product. Analysing price history alongside sales could help identify products whose sales patterns coincide with price changes and support more informed inventory planning.

These results describe observed price changes; they do not establish that price changes caused changes in demand. The analysis also counts differences between consecutive recorded prices, rather than assuming that every missing price week represents a price change.

## 4. Sales by Category

| Category | Units sold | Share of total units |
|---|---:|---:|
| FOODS | 45,089,939 | 68.63% |
| HOUSEHOLD | 14,480,670 | 22.04% |
| HOBBIES | 6,124,800 | 9.32% |

*Percentages may not sum to exactly 100% because of rounding.*

### Business Interpretation

FOODS was the leading category by sales volume, contributing 68.63% of total units sold. HOUSEHOLD accounted for 22.04%, while HOBBIES contributed 9.32%.

This concentration suggests that demand planning for FOODS could be particularly important when prioritising replenishment and forecasting efforts by unit volume. HOUSEHOLD and HOBBIES may require different inventory strategies according to their demand patterns and variability.

These rankings are based on units sold, not revenue or profit. A category with the highest unit volume is not necessarily the most profitable or the one with the highest financial value.

## 5. Estimated Revenue by Category

| Category | Estimated revenue | Revenue share |
|---|---:|---:|
| FOODS | 108,904,622.04 | 58.03% |
| HOUSEHOLD | 55,953,542.68 | 29.81% |
| HOBBIES | 22,818,405.30 | 12.16% |

- **Estimated total revenue:** 187,676,570.02
- **Positive-sales weekly rows without a price:** 0

### Business Interpretation

FOODS generated the highest estimated revenue, accounting for 58.03% of the total, compared with 68.63% of units sold. HOUSEHOLD contributed 29.81% of estimated revenue from 22.04% of units, while HOBBIES contributed 12.16% of revenue from 9.32% of units.

This demonstrates why category inventory analysis should consider both sales volume and estimated revenue. These figures represent price-based revenue estimates, not profit or margin, and do not account for transaction-level discounts that are absent from the dataset.


## 6. Store-Level Sales Patterns

| Store | Total units sold |
|---|---:|
| CA_3 | 11,188,180 |
| CA_1 | 7,698,216 |
| TX_2 | 7,214,384 |
| WI_2 | 6,544,012 |
| WI_3 | 6,427,782 |
| TX_3 | 6,089,330 |
| CA_2 | 5,685,475 |
| TX_1 | 5,595,292 |
| WI_1 | 5,149,062 |
| CA_4 | 4,103,676 |

### Business Interpretation

CA_3 recorded the highest total unit sales, while CA_4 recorded the lowest. CA_3 sold approximately 2.73 times as many units as CA_4 over the observed period. This variation makes store-level demand analysis useful for prioritising forecasting and replenishment efforts. Total sales alone do not establish whether the difference comes from customer demand, availability, or other factors.

## 7. Weekday Sales Patterns

| Weekday | Average total units sold per day |
|---|---:|
| Saturday | 41,546.89 |
| Sunday | 41,130.02 |
| Monday | 32,852.97 |
| Tuesday | 30,368.78 |
| Wednesday | 30,010.02 |
| Thursday | 30,205.01 |
| Friday | 34,225.99 |

### Business Interpretation

Saturday and Sunday had the highest average daily unit sales, whereas Wednesday had the lowest. Saturday's average was approximately 38.4% higher than Wednesday's. This supports including day-of-week features in demand forecasting and investigating whether weekend demand requires different replenishment planning.

## 8. Monthly Sales Patterns

### Highest-Sales Complete Months

| Year | Month | Total units sold |
|---:|---|---:|
| 2016 | March | 1,275,746 |
| 2015 | August | 1,254,341 |
| 2015 | October | 1,248,437 |
| 2015 | July | 1,232,147 |
| 2016 | January | 1,215,286 |

### Lowest-Sales Complete Months

| Year | Month | Total units sold |
|---:|---|---:|
| 2011 | May | 719,562 |
| 2011 | February | 726,375 |
| 2011 | April | 737,713 |
| 2011 | June | 753,380 |
| 2011 | March | 763,567 |

### Business Interpretation

March 2016 had the highest monthly sales volume at 1,275,746 units, while May 2011 had the lowest at 719,562 units. The difference suggests that aggregate sales volume varies substantially across the observation period.

These totals do not establish a recurring seasonal pattern because differences in product availability, assortment, and underlying demand may influence the trend. Further analysis should compare individual product-store demand over time and examine recurring calendar effects before drawing conclusions about seasonality.

## 9. EDA-Driven Design Decisions

- **High zero-sales frequency →** distinguish pre-price periods from demand observations and measure zero-sales frequency after the first recorded price week.
- **Variable price history →** retain weekly prices and investigate whether price changes coincide with changes in sales.
- **Differences between categories →** evaluate inventory priorities using both unit volume and estimated revenue, not units alone.
- **Differences between stores →** develop store-level demand forecasts instead of assuming every store has the same demand.
- **Weekday and monthly variation →** evaluate day-of-week and calendar features in forecasting, and validate seasonality before using it for replenishment decisions.


## Caveats

- Zero sales do not necessarily indicate excess inventory; they may reflect intermittent demand or product availability.
- The first recorded price is used as an availability proxy; it does not confirm the actual launch date or physical stock availability.
- Price differences and sales patterns show associations, not proof of causation.
- Category rankings are based on units sold, not revenue, margin, or profit.
- Further analysis is required before translating these findings into specific replenishment recommendations.
