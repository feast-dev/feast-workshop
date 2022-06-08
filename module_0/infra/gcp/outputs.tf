output "project_name" {
  value = var.project_name
}
output "project_bucket" {
  value = google_storage_bucket.feast_bucket.url
}
