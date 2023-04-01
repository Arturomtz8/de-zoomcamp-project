{{
    config(
        materialized="table",
    )
}}

with
    comments_ghosts as (select * from {{ ref("prod_comments_ghosts") }}),
    posts_ghosts as (select * from {{ ref("prod_posts_ghosts") }})

{# todo reduce num of columns  #}

select comments_ghosts.*, posts_ghosts.*
from comments_ghosts
left join posts_ghosts on comments_ghosts.comments_post_id = posts_ghosts.post_fullname
