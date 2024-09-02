from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("MergeDataFrames") \
    .getOrCreate()

# Read Data from S3 (Parquet format)
s3_input_path = "s3://group8project/credit_card_fraud/org80percent/"
df_s3 = spark.read.parquet(s3_input_path)

# Read Data from RDS
rds_url = "jdbc:mysql://database-1.c83nalmcke6t.us-east-1.rds.amazonaws.com:3306/creditdb"
rds_properties = {
    "user": "admin",
    "password": "8989717872",
    "driver": "com.mysql.cj.jdbc.Driver"
}

df_rds = spark.read.jdbc(url=rds_url, table="creditdata", properties=rds_properties)

# Merge the DataFrames using union (assuming they have the same schema)
df_merged = df_s3.union(df_rds)

# Remove duplicates (assuming you want to keep the first occurrence)
df_deduped = df_merged.dropDuplicates()

# Remove rows with null values
df_cleaned = df_deduped.na.drop()

# Save the cleaned data back to S3
s3_output_path = "s3://group8project/credit_card_fraud/mergeddata/"
df_cleaned.write.mode('overwrite').parquet(s3_output_path)

# Stop the Spark session
spark.stop()
