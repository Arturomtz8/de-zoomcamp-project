# Paranormal subreddits ELT

## Objective
This project wants to know at which hour the posts more voted are posted, the ratio between upvoting score vs number of comments and the most common words in posts and comments from the subreddits: Ghoststories, Ghosts, Paranormal, ParanormalEncounters.
The data was obtained from the [PRAW - The Python Reddit API Wrapper](https://praw.readthedocs.io/en/stable/index.html), which makes it easier to interact with the posts, comments, and subreddits from Reddit's social app.

## Architecture
<p align="center">
    <img src="data/img/infra_project.png">
</p>

## Technologies used
 - [Terraform](https://developer.hashicorp.com/terraform/docs)
 - [Github Actions](https://github.com/features/actions)
 - [Poetry (for the python environment)](https://python-poetry.org/docs/)
 - [Prefect](https://www.prefect.io/)
 - [Google Cloud Storage](https://cloud.google.com/storage/)
 - [Google Big Query](https://cloud.google.com/bigquery)
 - [dbt](https://docs.getdbt.com/)
 - [Google Looker Studio](https://lookerstudio.google.com)

## Data pipeline
A lot of the orchestration of the project is done via Github Actions located in [link to code](.github/workflows/) and Prefect [link to code](src/flows/).

Github Actions is mainly used for running jobs (python scripts and dbt commands) via cronjob and Prefect is responsible for creating the flows and connecting to Google Cloud services in a secure way using [Blocks](https://docs.prefect.io/concepts/blocks/) and [Secrets](https://discourse.prefect.io/t/how-to-securely-store-secrets-in-prefect-2-0/1209). 

I query the top posts every day from the mentioned subreddits 4 times per day (3 am, 9 am, 15 pm and 21 pm) in order to obtain the posts that were popular during all the day and save them in Google Cloud Storage and Big Query.

At 3:50 am I also query the comments from each post for obtaining the most frequent words in comments and info about the comments. Every time that I query the PRAW, I make sure to not include posts or comments that I have already in Google Cloud Storage.

With all the posts and comments saved in Google Cloud Storage, I also create wordclouds and graphs from the most frequent words in the post title, post text, and comment body:
<p align="center">
    <img src="data/img/wordcloud_post_title.png">
    <img src="data/img/words_in_comment_body.png">
</p>

Finally, at 4:10 am I run dbt for cleaning and preparing de data from Big Query and serve it in Google Looker Studio.

## Prerequisites for running the project
- Use terraform for building the necessary infrastructure in Google Cloud. You will need to create 1 environment variable in your terminal:
    ```bash
    $ export TF_VAR_project=your_project_id_from_google_cloud
    ```

- Download [Poetry]((https://python-poetry.org/docs/)) and run the command 'poetry install' . This command will take the dependencies located in [pyproject.toml](pyproject.toml) and create a new environment that will help you to sync your dependencies and run the python scripts easily.

- You will also have to create an agent that will interact with PRAW, here are the steps for doing it: https://praw.readthedocs.io/en/stable/getting_started/quick_start.html#prerequisites

- Use Prefect Cloud for configuring Secrets and Blocks that are used in the [flows scripts](src/flows/)

Take into account that you must have your environment variables and secrets stored in your terminal or in your repo. If you want to run it in Github Actions, you will have to create
