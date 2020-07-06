DROP TABLE IF EXISTS facebook_posts;
DROP SEQUENCE IF EXISTS facebook_sequence;

CREATE SEQUENCE facebook_sequence START WITH 1;

CREATE TABLE facebook_posts
(
    id                  INTEGER PRIMARY KEY DEFAULT nextval('facebook_sequence'),
    post_id             VARCHAR NOT NULL,
    author              VARCHAR NOT NULL,
    link                VARCHAR,
    text                VARCHAR,
    datetime            TIMESTAMP
);
CREATE UNIQUE INDEX facbook_id_idx ON facebook_posts(post_id)