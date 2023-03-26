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


resource "google_bigquery_table" "raw_posts" {
  dataset_id = google_bigquery_dataset.reddit_dataset.dataset_id
  table_id   = "raw_posts_ghosts"
  description =  "Ghosts and paranormal raw posts from reddit"
  deletion_protection = false


  schema = <<EOF
[
  {
    "name": "author",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "author of the post"
  },
  {
    "name": "author_flair_text",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "flair text of the author, if he/she doesn't have, it will appear None"
  },
  {
    "name": "clicked",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if I clicked the post"
  },
  {
    "name": "distinguished",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post is distinguished inside the subreddit"
  },
  {
    "name": "edited",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post was edited"
  },
  {
    "name": "post_id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "the id of the post"
  },
  {
    "name": "is_original_content",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post is original"
  },
  {
    "name": "locked",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post is locked"
  },
  {
    "name": "post_fullname",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "the fullname of the post, similar to post id but with t3_ as a prefix"
  },
  {
    "name": "post_title",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "the title of the post"
  },
  {
    "name": "post_text",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "the text of the post"
  },
  {
    "name": "num_comments",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "the number of comments"
  },
  {
    "name": "post_score",
    "type": "INT64",
    "mode": "REQUIRED",
    "description": "the score of the post"
  },
  {
    "name": "post_url",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "the url of the post"
  },
  {
    "name": "saved",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post was saved by me"
  },
  {
    "name": "created_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "the timestamp the post was created"
  },
  {
    "name": "over_18",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post was marked as over 18 content"
  },
  {
    "name": "spoiler",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post contains an spoiler"
  },
  {
    "name": "stickied",
    "type": "BOOL",
    "mode": "REQUIRED",
    "description": "if the post was stickied in the subreddit"
  },
  {
    "name": "upvote_ratio",
    "type": "FLOAT64",
    "mode": "REQUIRED",
    "description": "the ratio of the upvotes the post received"
  }
]
EOF

}




# resource "google_bigquery_table" "raw_posts" {
#   dataset_id          = google_bigquery_dataset.reddit_dataset.dataset_id
#   table_id            = "raw_posts_ghosts"
#   description         = "Ghosts and paranormal raw posts from reddit"
#   deletion_protection = false

#   external_data_configuration {
#     autodetect            = true
#     source_format         = "PARQUET"
#     compression           = "GZIP"
#     ignore_unknown_values = false
#     max_bad_records       = 90
#     source_uris = [
#       var.uri_posts_ghosts,
#     ]
#   }
# }


# resource "google_bigquery_table" "raw_comments" {
#   dataset_id          = google_bigquery_dataset.reddit_dataset.dataset_id
#   table_id            = "raw_comments_ghosts"
#   description         = "Ghosts and paranormal raw comments from reddit"
#   deletion_protection = false

#   external_data_configuration {
#     autodetect            = true
#     source_format         = "PARQUET"
#     compression           = "GZIP"
#     ignore_unknown_values = false
#     max_bad_records       = 90
#     source_uris = [
#       var.uri_comments_ghosts,
#     ]
#   }
# }

