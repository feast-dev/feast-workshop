provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "feast_bucket" {
  bucket        = "feast-spark-workshop-test"
  acl           = "private"
  force_destroy = true
}

resource "aws_s3_bucket_object" "driver_stats_upload" {
  bucket = aws_s3_bucket.feast_bucket.bucket
  key    = "driver_stats.parquet"
  source = "${path.module}/driver_stats.parquet"
}
