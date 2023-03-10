
import os
from collections import Counter

import matplotlib.pyplot as plt
import nltk
import pandas as pd
import seaborn as sns
# Lemmatizer helps to reduce words to the base form
from nltk.stem import WordNetLemmatizer
# This allows to create individual objects from a bog of words
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import os


PATH_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "ghost_stories")
IMG_PATH_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "img")
stopwords_personalized = nltk.corpus.stopwords.words("english")
new_stopwords = ["u", "/u", "would", "could", "get", "got", "even", "said", "wa", "around", "still"]
stopwords_personalized.extend(new_stopwords)


def word_freq(column_name: str)-> pd.DataFrame:
    df_posts = pd.read_parquet(f"{PATH_FILE}/posts_ghosts_stories.parquet")
    posts_text_string = ''.join(df_posts[column_name].tolist())
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
    word_counter_df = word_counter_df[~word_counter_df[f"words_in_{column_name}"].isin(stopwords_personalized)]
    print(word_counter_df)
    word_counter_df.to_csv(
        os.path.join(PATH_FILE, f"word_counter_{column_name}.csv"),
        encoding="utf-8-sig",
        index=False,
    )
    return word_counter_df


def create_graph(df: pd.DataFrame)->None:
    fig, axes = plt.subplots()
    fig.suptitle("Data taken from r/Ghoststories")  # or plt.suptitle('Main title')
    if "words_in_post_title" in list(df.columns):
        sns.barplot(x="frequency", y="words_in_post_title", data=df.head(25))
    else:
        sns.barplot(x="frequency", y="words_in_post_text", data=df.head(25))
    plt.savefig(
        os.path.join(IMG_PATH_FILE, f"{axes.get_ylabel()}.png"),
        bbox_inches="tight",
        dpi=150,
    )
    plt.close()


def create_wordcloud(column_name:str):
    df_posts: pd.DataFrame = pd.read_parquet(f"{PATH_FILE}/posts_ghosts_stories.parquet")
    posts_text_string: str =  ''.join(df_posts[column_name].to_list())

    wordcloud = WordCloud(
        colormap="ocean", background_color="gold", min_font_size=10
    ).generate(posts_text_string)
    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(
        os.path.join(IMG_PATH_FILE, f"wordcloud_{column_name}.png"), bbox_inches="tight"
    )
    plt.close()


if __name__ == "__main__":
    df_post_title = word_freq("post_title")
    df_post_text = word_freq("post_text")
    create_graph(df_post_title)
    create_graph(df_post_text)
    create_wordcloud("post_title")
    create_wordcloud("post_text")