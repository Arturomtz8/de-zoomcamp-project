import os
import sys
from pathlib import Path

sys.path.insert(0, (os.path.join(os.path.dirname(__file__), "..")))

import sys

from src.flows.gc_funcs.reader_writer import (read_comments, read_posts,
                                              write_to_gcs)

df_posts = read_posts()
# df_test_comments = read_comments()
# df_posts.drop(columns=["poll_option_Besties with Casper", "poll_option_Nope...", "total_vote_count", "voting_end_timestamp"], inplace=True)

# local_path = Path(f"data/ghost_stories/posts_ghosts_stories.parquet")
# # local_path.parent.mkdir(parents=True, exist_ok=True)
# df_posts.to_parquet(local_path, compression="gzip")
# write_to_gcs(local_path=local_path, gcs_bucket_path=local_path)

df_posts.to_csv("test_posts.csv", index=False, encoding="utf-8")
# df_test_comments.to_csv("test_comments.csv", index=False, encoding="utf-8")
