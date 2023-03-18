terraform {
  required_version = ">= 1.0"
  backend "local" {} # Can change from "local" to "gcs" (for google) or "s3" (for aws), if you would like to preserve your tf-state online
  required_providers {
    google = {
      source = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.region
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name     = "${local.data_lake_bucket}_${var.project}" # Concatenating DL bucket & Project name for unique naming
  location = var.region

  # Optional, but recommended settings:
  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 720 // days
    }
  }

  force_destroy = true
}

# Two datasets, one from the course, one for the project
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
}


resource "google_bigquery_dataset" "reddit_dataset" {
  dataset_id = var.BQ_DATASET_REDDIT
  project    = var.project
  location   = var.region
}

# create table for posts
resource "google_bigquery_table" "raw_posts" {
  dataset_id          = google_bigquery_dataset.reddit_dataset.dataset_id
  table_id            = "raw_posts_ghosts"
  description         = "Ghosts and paranormal raw posts from reddit"
  deletion_protection = true

  external_data_configuration {
    autodetect            = true
    source_format         = "PARQUET"
    compression           = "GZIP"
    ignore_unknown_values = true
    max_bad_records       = 90
    source_uris = [
      var.uri_posts_ghosts,
    ]
  }
}


# create table for comments
resource "google_bigquery_table" "raw_comments" {
  dataset_id          = google_bigquery_dataset.reddit_dataset.dataset_id
  table_id            = "raw_comments_ghosts"
  description         = "Ghosts and paranormal raw comments from reddit"
  deletion_protection = true

  external_data_configuration {
    autodetect            = true
    source_format         = "PARQUET"
    compression           = "GZIP"
    ignore_unknown_values = true
    max_bad_records       = 90
    source_uris = [
      var.uri_comments_ghosts,
    ]
  }
}


# resource "google_storage_bucket_object" "archive" {
#   name   = "src_code.zip"
#   bucket = google_storage_bucket.bucket.name
#   source = "./data/ghost_stories/"
# }
# resource "google_cloudfunctions_function" "function" {
#   name        = "function-test"
#   description = "function for updating bq automatically when a new file is uploaded"
#   runtime     = "python39"
#   region   = var.region

#   available_memory_mb          = 128
#   source_archive_bucket        = google_storage_bucket.bucket.name
#   source_archive_object        = google_storage_bucket_object.archive.name
#   trigger_http                 = true
#   https_trigger_security_level = "SECURE_ALWAYS"
#   timeout                      = 60
#   entry_point                  = "import_to_big_query"
#   labels = {
#     my-label = "cloud-function-bq"
#   }

#   environment_variables = {
#     dataset="reddit_data",
#     table="posts_ghosts",
#   }
# }

# # IAM entry for a single user to invoke the function
# resource "google_cloudfunctions_function_iam_member" "invoker" {
#   project        = google_cloudfunctions_function.function.project
#   region         = google_cloudfunctions_function.function.region
#   cloud_function = google_cloudfunctions_function.function.name

#   role   = "roles/cloudfunctions.invoker"
#   member = "user:myFunctionInvoker@example.com"
# }
