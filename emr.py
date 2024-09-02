from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DecimalType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("SplitDataFrame") \
    .getOrCreate()

# Define Schema
schema = StructType([
    StructField("_c0", StringType(), True),
    StructField("ssn", StringType(), True),
    StructField("cc_num", StringType(), True),
    StructField("first", StringType(), True),
    StructField("last", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("street", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("zip", DecimalType(5, 0), True),
    StructField("lat", DecimalType(9, 6), True),
    StructField("long", DecimalType(9, 6), True),
    StructField("city_pop", StringType(), True),
    StructField("job", StringType(), True),
    StructField("dob", StringType(), True),
    StructField("acct_num", StringType(), True),
    StructField("profile", StringType(), True),
    StructField("trans_num", StringType(), True),
    StructField("trans_date", StringType(), True),
    StructField("trans_time", StringType(), True),
    StructField("unix_time", StringType(), True),
    StructField("category", StringType(), True),
    StructField("amt", DecimalType(9, 2), True),
    StructField("is_fraud", DecimalType(9, 0), True),
    StructField("merchant", StringType(), True),
    StructField("merch_lat", DecimalType(9, 6), True),
    StructField("merch_long", DecimalType(9, 6), True)
])

# Read data from S3
s3_path = "s3://group8project/credit_card_fraud/"
df = spark.read.csv(s3_path, schema=schema, header=True)

# Split DataFrame
df_rds = df.limit(100000)  # First 100,000 rows for RDS
df_s3 = df.subtract(df_rds)  # Remaining 33,900,000 rows for S3

# Coalesce df_s3 to reduce the number of partitions
df_s3_coalesced = df_s3.coalesce(10)  # Adjust the number of partitions as needed

# Save 33,900,000 rows to S3
s3_output_path = "s3://group8project/credit_card_fraud/org80percent"
df_s3_coalesced.write.mode('overwrite').parquet(s3_output_path)

# Save 100,000 rows to RDS
rds_url = "jdbc:mysql://database-1.c83nalmcke6t.us-east-1.rds.amazonaws.com:3306/creditdb"
rds_properties = {
    "user": "admin",
    "password": "8989717872",
    "driver": "com.mysql.cj.jdbc.Driver"
}

df_rds.write.jdbc(url=rds_url, table="creditdata", mode="overwrite", properties=rds_properties)

# Stop the Spark session
spark.stop()
