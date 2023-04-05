# Paranormal subreddits data pipeline

## Objective

This project wants to know at which hour the posts more voted are posted, the ratio between upvoting score vs number of comments and the most common words in posts and comments from the subreddits: Ghoststories, Ghosts, Paranormal, ParanormalEncounters.
The data was obtained from the PRAW (The Python Reddit API Wrapper https://praw.readthedocs.io/en/stable/index.html), which makes it easier to interact with the posts, comments, and subreddits from Reddit's social app.

I focus on querying the top posts every day from the mentioned subreddits. I query the PRAW 4 times per day in order to obtain differents posts that were popular during the all the day. I query it automatically at 3 am, 9 am, 15 pm and 21 pm using Github Actions (https://docs.github.com/en/actions). At 3:50 am I also queried the comments from each post for obtaining the most frequent words in comments.

## Architecture
<p align="center">
    <img src="data/img/infra_project.png">
</p>


