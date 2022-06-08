output "project_name" {
  value = var.project_name
}
output "project_bucket" {
  value = "s3://${aws_s3_bucket.feast_bucket.bucket}"
}
