{{
    config(
        materialized="table",
    )
}}


with
    raw_posts_ghosts as (
        select
            author,
            author_flair_text,
            distinguished,
            edited,
            post_id,
            is_original_content,
            locked,
            post_fullname,
            post_title,
            post_text,
            num_comments,
            post_score,
            post_url,
            created_at,
            over_18,
            spoiler,
            stickied,
            upvote_ratio

        from {{ source("raw", "posts_ghosts") }}
    )

select
    author as author_post,
    author_flair_text,
    distinguished as distinguished_post,
    edited as edited_post,
    post_id,
    is_original_content as post_is_original_content,
    locked as post_locked,
    post_fullname,
    post_title,
    post_text,
    cast(num_comments as int64) as num_comments,
    cast(post_score as int64) as post_score,
    post_url,
    created_at as post_created_at,
    {{ extract_hour("created_at") }} as hour_post_created_at,
    {{ normalize_timestamp("created_at") }} as normalized_post_created_at,
    over_18 as post_over_18,
    spoiler as post_spoiler,
    stickied as post_stickied,
    cast(upvote_ratio as float64) as post_upvote_ratio
from raw_posts_ghosts
