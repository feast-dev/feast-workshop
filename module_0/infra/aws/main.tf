provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "feast_bucket" {
  bucket        = "feast-repo-gyerli"
  force_destroy = true
}

# resource "aws_s3_bucket_acl" "feast_bucket_acl" {
#   bucket = aws_s3_bucket.feast_bucket.bucket
# }

resource "aws_s3_bucket_object" "feast_workshop_folder" {
  bucket = aws_s3_bucket.feast_bucket.id
  key    = "feast-workshop-${var.project_name}/"
}

resource "aws_s3_object" "driver_stats_upload" {
  bucket = aws_s3_bucket.feast_bucket.bucket
  key    = "feast-workshop-${var.project_name}/driver_stats.parquet"
  source = "${path.module}/../driver_stats.parquet"
}