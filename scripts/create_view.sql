create or replace view all_info as
SELECT * FROM
(
    SELECT 'facebook' as source,
        post_id    as id,
        author,
        link,
        text,
        datetime,
        created
    FROM facebook_posts
    UNION ALL
    SELECT 'instagram' as source,
        insta_id  as id,
        author,
        link,
        text,
        datetime,
        created
    FROM instagram_posts
    UNION ALL
    SELECT
        'vk' as source,
        post_id as id,
        author,
        post_url as link,
        text,
        datetime,
        created
    FROM vk_posts
    UNION ALL
    SELECT
        source,
        COALESCE(source_id, CAST(id as VARCHAR)) as id,
        COALESCE(author, source) as author,
        url as link,
        text,
        COALESCE(datetime, created) as datetime,
        created
    FROM other_info
) as information
ORDER BY information.datetime DESC