# Databricks notebook source
# MAGIC %md
# MAGIC Ingest raw files to databricks

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS retail_inv;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS retail_inv.bronze;
# MAGIC CREATE SCHEMA IF NOT EXISTS retail_inv.silver;
# MAGIC CREATE SCHEMA IF NOT EXISTS retail_inv.gold;
# MAGIC CREATE SCHEMA IF NOT EXISTS retail_inv.ml;
# MAGIC CREATE VOLUME IF NOT EXISTS retail_inv.bronze.raw_files;

# COMMAND ----------

from pyspark.sql import functions as F

base = "/Volumes/retail_inv/bronze/raw_files/m5/"

def ingest(file_name, table_name):
    df = (spark.read
          .option("header", True)
          .option("inferSchema", True)
          .csv(base + file_name)
          .withColumn("_ingested_at", F.current_timestamp())
          .withColumn("_source_file", F.col("_metadata.file_path")))
    df.write.format("delta").mode("overwrite").saveAsTable(f"retail_inv.bronze.{table_name}")
    print(table_name, spark.table(f"retail_inv.bronze.{table_name}").count())

ingest("calendar.csv", "calendar")
ingest("sell_prices.csv", "sell_prices")
ingest("sales_train_validation.csv", "sales_wide")

# COMMAND ----------

