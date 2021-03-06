DROP TABLE IF EXISTS vk_posts;
DROP SEQUENCE IF EXISTS vk_sequence;

CREATE SEQUENCE vk_sequence START WITH 1;

CREATE TABLE vk_posts
(
    id                  INTEGER PRIMARY KEY DEFAULT nextval('vk_sequence'),
    post_id             VARCHAR NOT NULL,
    post_url            VARCHAR NOT NULL,
    author              VARCHAR NOT NULL,
    text                VARCHAR,
    datetime            TIMESTAMP,
    created             TIMESTAMP,
    modified            TIMESTAMP
);
CREATE UNIQUE INDEX vk_url_idx ON vk_posts(post_id)