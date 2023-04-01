{{
    config(
        materialized="table",
    )
}}

with
    raw_comments_ghosts as (
        select
            post_url,
            author,
            comment_id,
            body,
            created_at,
            distinguished,
            edited,
            is_author_submitter,
            post_id,
            link_comment,
            comment_score
        from {{ source("raw", "comments_ghosts") }}
    )

select
    post_url as comments_post_url,
    author as author_comment,
    comment_id,
    body as comment_body,
    created_at as comment_created_at,
    {{ extract_hour("created_at") }} as hour_comment_created_at,
    {{ normalize_timestamp("created_at") }} as normalized_comment_created_at,
    distinguished as comment_distinguished,
    edited as comment_edited,
    is_author_submitter,
    post_id as comments_post_id,
    link_comment,
    comment_score
from raw_comments_ghosts
