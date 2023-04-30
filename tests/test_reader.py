import os
import sys
from pathlib import Path

sys.path.insert(0, (os.path.join(os.path.dirname(__file__), "..")))

from src.flows.gc_funcs.reader_writer import (  # noqa: E402
    get_posts_from_gcs,
    write_to_gcs,
)

df_test_posts = get_posts_from_gcs()
# df_test_comments = get_comments_from_gcs()

local_path = Path("data/ghost_stories/posts_ghosts_stories.parquet")
# # local_path.parent.mkdir(parents=True, exist_ok=True)
print(df_test_posts["post_url"])
df_test_posts.drop_duplicates(
    subset=["post_title"],
    keep="last",
    inplace=True,
)
df_test_posts.to_parquet(local_path, compression="gzip")

write_to_gcs(local_path=local_path, gcs_bucket_path=local_path)

# df_test_posts.to_csv("test_posts.csv", index=False, encoding="utf-8")
# df_test_comments.to_csv("test_comments.csv", index=False, encoding="utf-8")
