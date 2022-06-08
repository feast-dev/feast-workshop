provider "google" {
  project = var.gcp_project
}

resource "google_storage_bucket" "feast_bucket" {
  name          = "feast-workshop-${var.project_name}"
  force_destroy = true
  location      = "US"

  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "driver_stats_upload" {
  bucket = google_storage_bucket.feast_bucket.name
  name   = "driver_stats.parquet"
  source = "${path.module}/../driver_stats.parquet"
}
