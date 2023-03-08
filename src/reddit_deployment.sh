prefect deployment build ./proto-project/proto_main.py:scrape_reddit \
  -n docker-reddit \
  -q test \
  -sb github/git-docker \
  -ib docker-container/docker-reddit \
  -o docker-reddit \
  --apply


# {
#     "EXTRA_PIP_PACKAGES":  "pandas==1.5.2 praw==7.6.1 pyarrow==10.0.1 prefect-gcp[cloud_storage]==0.2.4"
# }



