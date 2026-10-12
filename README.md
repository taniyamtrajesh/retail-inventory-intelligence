# retail-inventory-intelligence
End-to-end retail inventory intelligence pipeline using Azure Data Lake Storage, Databricks, Spark, and machine learning.


## Business Problem

Retailers need to anticipate product demand to make better inventory and replenishment decisions. Poor demand estimates can contribute to excess inventory, wasted working capital, and missed sales opportunities.

This project explores how historical sales, selling prices, calendar events, and demand patterns can be transformed into reliable forecasts and practical inventory-planning recommendations.

## Core business question:

How can historical retail sales, pricing, and calendar data be used to forecast product demand and support better inventory-planning decisions across stores?

## Project Objectives

- Build a data lake following the Bronze, Silver, and Gold architecture.

- Ingest and validate raw retail data.

- Clean and transform sales, calendar, and pricing datasets using Spark.

- Engineer features that capture demand trends, seasonality, prices, and events.

- Develop and evaluate demand forecasting models against simple baselines.

- Translate forecasts into illustrative inventory-planning recommendations.

- Track data quality, forecast accuracy, and business-oriented metrics.

- Version-control code, documentation, and tests using Git and GitHub.

## Dataset

This project uses the M5 Forecasting dataset from Kaggle.

Source: M5 Forecasting - Accuracy

## Key files:

- sales_train_validation.csv — historical daily unit sales by item and store.

- calendar.csv — dates, calendar features, and events.

- sell_prices.csv — weekly selling prices by item and store.

The original source files are stored in the Azure Data Lake's raw container and are treated as immutable inputs.

Data limitation: The M5 dataset does not directly provide actual on-hand inventory, supplier lead times, or observed stockouts. Inventory recommendations will therefore be illustrative and based on explicitly documented assumptions rather than claims about actual stockout reduction.

## Planned Architecture

```text
Kaggle M5 Dataset
       |
       v
Azure Data Lake Storage Gen2
       |
       v
     Bronze
 Raw ingested data
       |
       v
     Silver
 Cleaned and validated data
       |
       v
      Gold
 Aggregated analytics
 Forecast-ready features
       |
       v
 Demand Forecasting
       |
       v
Inventory Planning
  and Evaluation
```

Azure Databricks and Apache Spark will be used for data processing and analytics where appropriate.


## Data Lake Design

| Layer | Purpose |
|---|---|
| Raw | Preserve the original source files |
| Bronze | Record ingested data with minimal transformations |
| Silver | Clean, validate, and standardize datasets |
| Gold | Produce analytical tables and model-ready features |

## Planned Technical Stack

- Cloud: Microsoft Azure

- Storage: Azure Data Lake Storage Gen2

- Processing: Azure Databricks, Apache Spark, PySpark

- Programming: Python, SQL

- Machine Learning: Scikit-learn and an appropriate forecasting approach

- Version Control: Git and GitHub

- Testing: Pytest and data-quality checks

The final model and evaluation strategy will be selected after exploratory analysis and baseline comparisons.

## Evaluation Strategy

The project will assess both data quality and forecast performance.

Potential metrics include:

- Data quality: missing values, duplicate records, schema validity, and referential integrity.

- Forecasting: MAE, RMSE, and an appropriate scaled error metric.

- Business analysis: forecast bias and illustrative inventory requirements under documented assumptions.

Model performance will be compared against simple baselines before deciding whether a more complex model is justified.

## Repository Structure

```text
retail-inventory-intelligence/
├── docs/
│   └── project-documentation.md
├── simulator/
│   └── generate_retail_data.py
├── notebooks/
│   ├── 01_bronze/
│   │   └── .gitkeep
│   ├── 02_silver/
│   │   └── .gitkeep
│   ├── 03_gold/
│   │   └── .gitkeep
│   └── 04_ml/
│       └── .gitkeep
├── tests/
│   └── .gitkeep
├── .gitignore
└── README.md
```

### Directory Descriptions

| Path | Purpose |
|---|---|
| `docs/` | Architecture diagrams, business requirements, and project documentation |
| `simulator/` | Scripts for generating synthetic inventory or operational scenarios |
| `notebooks/01_bronze/` | Raw data ingestion and initial validation |
| `notebooks/02_silver/` | Data cleaning, standardization, and quality checks |
| `notebooks/03_gold/` | Business aggregations and analytics-ready datasets |
| `notebooks/04_ml/` | Demand forecasting, model evaluation, and inventory analysis |
| `tests/` | Unit tests and data-quality tests |
| `.gitignore` | Files and folders Git should exclude |
| `README.md` | Project overview, business question, architecture, and setup instructions |

The `.gitkeep` files are placeholders that allow Git to track directories before they contain actual project files. They can be removed as real files are added.