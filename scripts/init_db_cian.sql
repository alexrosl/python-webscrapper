DROP TABLE IF EXISTS cian_properties;
DROP SEQUENCE IF EXISTS global_seq;

CREATE SEQUENCE global_seq START WITH 1;

CREATE TABLE cian_properties
(
    id                  INTEGER DEFAULT nextval('global_seq'),
    cian_id             INTEGER PRIMARY KEY NOT NULL,
    link                VARCHAR NOT NULL,
    title               VARCHAR,
    attributes          VARCHAR,
    area                INTEGER,
    metro               VARCHAR,
    remoteness          VARCHAR,
    walk                BOOL DEFAULT false,
    address             VARCHAR,
    price_full          INTEGER,
    price_per_meter     INTEGER,
    currency            VARCHAR,
    description         VARCHAR
);
CREATE UNIQUE INDEX cian_id_idx ON cian_properties(cian_id)