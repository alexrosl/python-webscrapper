DROP TABLE IF EXISTS instagram_posts;
DROP SEQUENCE IF EXISTS insta_sequence;

CREATE SEQUENCE insta_sequence START WITH 1;

CREATE TABLE instagram_posts
(
    id                  INTEGER PRIMARY KEY DEFAULT nextval('insta_sequence'),
    insta_id            VARCHAR NOT NULL,
    link                VARCHAR NOT NULL,
    author              VARCHAR,
    text                VARCHAR,
    datetime            TIMESTAMP
);
CREATE UNIQUE INDEX insta_id_idx ON instagram_posts(insta_id)