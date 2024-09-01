from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("EMR Job") \
    .getOrCreate()

# JDBC properties
jdbc_url = "jdbc:mysql://database-1.cow8emhoqtau.us-east-1.rds.amazonaws.com:3306/datadb"
mysql_properties = {
    "user": "admin",
    "password": "pass1234",
    "driver": "com.mysql.cj.jdbc.Driver"
}

# Read data from MySQL
df_ten = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "credit_card") \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .load()

df_ten_one = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "credit_card_two") \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .load()

# Read data from S3
s3_input = "s3://projecttry/credit/credit_card_csv/"
s3_df = spark.read.csv(s3_input, header=True, inferSchema=True)

# Union DataFrames
df_union = df_ten.union(df_ten_one).union(s3_df)

# Drop rows with any null values
df_dropped_na = df_union.dropna()

# Remove duplicates
df_uniq_all = df_dropped_na.dropDuplicates()

# Write the resulting DataFrame to S3 in CSV format
output_path = "s3://credit-card-twenty/credit_card_csv/credit_card.csv"
df_uniq_all.write.mode("overwrite").csv(output_path)

# Stop the Spark session
spark.stop()
