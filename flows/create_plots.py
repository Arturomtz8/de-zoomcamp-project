import random
from collections import Counter
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import nltk
import pandas as pd
import seaborn as sns
from gc_funcs.reader_writer import (get_comments_from_gcs, get_posts_from_gcs,
                                    write_to_gcs)
# Lemmatizer helps to reduce words to the base form
from nltk.stem import WordNetLemmatizer
# This allows to create individual objects from a bog of words
from nltk.tokenize import word_tokenize
from prefect import flow, task
from wordcloud import WordCloud


def grey_color_func(
    word,  # noqa: ANN001, ARG001
    font_size,  # noqa: ANN001, ARG001
    position,  # noqa: ANN001, ARG001
    orientation,  # noqa: ANN001, ARG001
    random_state=None,  # noqa: ANN001, ARG001
    **kwargs,  # noqa: ANN001, ANN003, ARG001
) -> None:
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)  # noqa: S311


@task(log_prints=True)
def create_word_freq_df(
    data_file_path: Path, column_name: str, stopwords_list: list[str]
) -> pd.DataFrame:
    if column_name in ["post_title", "post_text"]:
        df = get_posts_from_gcs()
    elif column_name == "body":
        df = get_comments_from_gcs()

    column_to_string = "".join(df[column_name].tolist())
    # creates tokens, creates lower class, removes numbers and lemmatizes the words
    new_tokens = word_tokenize(column_to_string)
    new_tokens = [t.lower() for t in new_tokens]
    min_len_tokens = 2
    new_tokens = [t for t in new_tokens if t.isalpha() and len(t) >= min_len_tokens]

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
        "Data taken from subreddits: Ghoststories, Ghosts, Paranormal and ParanormalEncounters"  # noqa: E501
    )  # or plt.suptitle('Main title')
    if "words_in_post_title" in list(df.columns):
        sns.barplot(
            x="frequency", y="words_in_post_title", data=df.head(25), palette="Blues_d"
        )
    elif "words_in_post_text" in list(df.columns):
        sns.barplot(
            x="frequency", y="words_in_post_text", data=df.head(25), palette="Blues_d"
        )
    elif "words_in_body" in list(df.columns):
        # change the name to a more descriptive name
        df["words_in_comment_body"] = df["words_in_body"]
        sns.barplot(
            x="frequency",
            y="words_in_comment_body",
            data=df.head(25),
            palette="Blues_d",
        )

    local_path = Path(f"{img_file_path}/{axes.get_ylabel()}.png")
    plt.savefig(
        local_path,
        bbox_inches="tight",
        dpi=150,
    )
    write_to_gcs(local_path=local_path, gcs_bucket_path=local_path)
    plt.close()


@task(log_prints=True)
def create_wordcloud(
    img_file_path: Path, column_name: str, stopwords_list: list[str]
) -> Path:
    if column_name in ["post_title", "post_text"]:
        df = get_posts_from_gcs()
        local_path = Path(f"{img_file_path}/wordcloud_{column_name}.png")
    elif column_name == "body":
        df = get_comments_from_gcs()
        local_path = Path(f"{img_file_path}/wordcloud_comment_{column_name}.png")

    column_to_string: str = "".join(df[column_name].to_list())

    wordcloud = WordCloud(
        colormap="ocean",
        background_color="black",
        mode="RGBA",
        color_func=grey_color_func,
        min_font_size=10,
        stopwords=stopwords_list,
    ).generate(column_to_string)
    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation="bilinear")
    # plt.tight_layout(pad=0)
    plt.axis("off")
    plt.savefig(local_path, transparent=True, bbox_inches="tight", pad_inches=0)
    write_to_gcs(local_path=local_path, gcs_bucket_path=local_path)
    plt.close()


@flow()
def create_plots() -> None:
    # set agg to prevent error from prefect
    # agg, is a non-interactive backend that can only write to files.
    # For more information and other ways of solving it see
    #  https://matplotlib.org/stable/users/explain/backends.html
    matplotlib.use("agg")
    raw_data_file_path = Path("data/ghost_stories")
    img_file_path = Path("data/img")
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
    df_post_title = create_word_freq_df(
        data_file_path=raw_data_file_path,
        column_name="post_title",
        stopwords_list=stopwords_personalized,
    )
    df_post_text = create_word_freq_df(
        data_file_path=raw_data_file_path,
        column_name="post_text",
        stopwords_list=stopwords_personalized,
    )
    df_comments_text = create_word_freq_df(
        data_file_path=raw_data_file_path,
        column_name="body",
        stopwords_list=stopwords_personalized,
    )
    create_barplot(img_file_path=img_file_path, df=df_post_title)
    create_barplot(img_file_path=img_file_path, df=df_post_text)
    create_barplot(img_file_path=img_file_path, df=df_comments_text)
    create_wordcloud(
        img_file_path=img_file_path,
        column_name="post_title",
        stopwords_list=stopwords_personalized,
    )
    create_wordcloud(
        img_file_path=img_file_path,
        column_name="post_text",
        stopwords_list=stopwords_personalized,
    )
    create_wordcloud(
        img_file_path=img_file_path,
        column_name="body",
        stopwords_list=stopwords_personalized,
    )


if __name__ == "__main__":
    create_plots()
