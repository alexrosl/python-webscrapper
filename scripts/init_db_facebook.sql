DROP TABLE IF EXISTS facebook_posts;
DROP SEQUENCE IF EXISTS facebook_sequence;

CREATE SEQUENCE facebook_sequence START WITH 1;

CREATE TABLE facebook_posts
(
    id                  INTEGER PRIMARY KEY DEFAULT nextval('facebook_sequence'),
    post_id             VARCHAR NOT NULL,
    link                VARCHAR,
    author              VARCHAR NOT NULL,
    text                VARCHAR,
    datetime            TIMESTAMP,
    created             TIMESTAMP,
    modified            TIMESTAMP
);
CREATE UNIQUE INDEX facbook_id_idx ON facebook_posts(post_id)