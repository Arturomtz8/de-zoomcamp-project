import os
from collections import Counter
from pathlib import Path
from typing import List

import matplotlib
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import seaborn as sns
# Lemmatizer helps to reduce words to the base form
from nltk.stem import WordNetLemmatizer
# This allows to create individual objects from a bog of words
from nltk.tokenize import word_tokenize
from prefect import flow, task
from wordcloud import WordCloud


@task(log_prints=True)
def word_freq(
    data_file_path: Path, column_name: str, stopwords_list: List[str]
) -> pd.DataFrame:
    df_posts = pd.read_parquet(f"{data_file_path}/posts_ghosts_stories.parquet")
    posts_text_string = "".join(df_posts[column_name].tolist())
    # creates tokens, creates lower class, removes numbers and lemmatizes the words
    new_tokens = word_tokenize(posts_text_string)
    new_tokens = [t.lower() for t in new_tokens]
    new_tokens = [t for t in new_tokens if t.isalpha() and len(t) >= 2]

    lemmatizer = WordNetLemmatizer()
    new_tokens = [lemmatizer.lemmatize(t) for t in new_tokens]
    counted = Counter(new_tokens)
    word_counter_df = pd.DataFrame(
        counted.items(), columns=[f"words_in_{column_name}", "frequency"]
    ).sort_values(by="frequency", ascending=False)
    # remove words that add no value from df
    word_counter_df = word_counter_df[
        ~word_counter_df[f"words_in_{column_name}"].isin(stopwords_list)
    ]
    print(word_counter_df)
    word_counter_df.to_csv(
        f"{data_file_path}/word_counter_{column_name}.csv",
        encoding="utf-8-sig",
        index=False,
    )
    return word_counter_df


@task(log_prints=True)
def create_barplot(img_file_path: Path, df: pd.DataFrame) -> None:
    fig, axes = plt.subplots()
    fig.suptitle(
        "Data taken from subreddits: Ghoststories, Ghosts, Paranormal and ParanormalEncounters"
    )  # or plt.suptitle('Main title')
    if "words_in_post_title" in list(df.columns):
        sns.barplot(x="frequency", y="words_in_post_title", data=df.head(25))
    else:
        sns.barplot(x="frequency", y="words_in_post_text", data=df.head(25))
    plt.savefig(
        f"{img_file_path}/{axes.get_ylabel()}.png",
        bbox_inches="tight",
        dpi=150,
    )
    plt.close()


@task(log_prints=True)
def create_wordcloud(data_file_path: Path, img_file_path: Path, column_name: str):
    df_posts: pd.DataFrame = pd.read_parquet(
        f"{data_file_path}/posts_ghosts_stories.parquet"
    )
    posts_text_string: str = "".join(df_posts[column_name].to_list())

    wordcloud = WordCloud(
        colormap="ocean", background_color="gold", min_font_size=10
    ).generate(posts_text_string)
    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(f"{img_file_path}/wordcloud_{column_name}.png", bbox_inches="tight")
    plt.close()


@flow()
def create_plots():
    # set agg to prevent error from prefect
    # agg, is a non-interactive backend that can only write to files.
    # For more information and other ways of solving it see
    #  https://matplotlib.org/stable/users/explain/backends.html
    matplotlib.use("agg")
    raw_data_file_path = Path(f"data/ghost_stories")
    img_file_path = Path(f"data/img")
    stopwords_personalized = nltk.corpus.stopwords.words("english")
    new_stopwords = [
        "u",
        "/u",
        "would",
        "could",
        "get",
        "got",
        "even",
        "said",
        "wa",
        "around",
        "still",
        "ha",
    ]
    stopwords_personalized.extend(new_stopwords)
    df_post_title = word_freq(
        data_file_path=raw_data_file_path,
        column_name="post_title",
        stopwords_list=stopwords_personalized,
    )
    df_post_text = word_freq(
        data_file_path=raw_data_file_path,
        column_name="post_text",
        stopwords_list=stopwords_personalized,
    )
    create_barplot(img_file_path=img_file_path, df=df_post_title)
    create_barplot(img_file_path=img_file_path, df=df_post_text)
    create_wordcloud(
        data_file_path=raw_data_file_path,
        img_file_path=img_file_path,
        column_name="post_title",
    )
    create_wordcloud(
        data_file_path=raw_data_file_path,
        img_file_path=img_file_path,
        column_name="post_text",
    )


if __name__ == "__main__":
    create_plots()
