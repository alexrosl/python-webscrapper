DROP TABLE IF EXISTS other_info;
DROP SEQUENCE IF EXISTS other_info_sequence;

CREATE SEQUENCE other_info_sequence START WITH 1;

CREATE TABLE other_info
(
    id                  INTEGER PRIMARY KEY DEFAULT nextval('other_info_sequence'),
    source              VARCHAR NOT NULL,
    url                 VARCHAR,
    title               VARCHAR,
    description         VARCHAR,
    date                VARCHAR,
    address             VARCHAR,
    created             TIMESTAMP,
    modified            TIMESTAMP
);