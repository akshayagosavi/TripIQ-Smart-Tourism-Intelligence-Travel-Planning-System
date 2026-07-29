from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("test").master("local[*]").getOrCreate()
print("PySpark version:", spark.version)
spark.stop()
print("SparkSession stopped cleanly.")
