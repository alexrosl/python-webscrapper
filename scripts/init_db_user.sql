DROP TABLE IF EXISTS users;
DROP SEQUENCE IF EXISTS users_sequence;

CREATE SEQUENCE users_sequence START WITH 1;

CREATE TABLE users
(
    id                INTEGER PRIMARY KEY DEFAULT nextval('users_sequence'),
    login             VARCHAR NOT NULL,
    password          VARCHAR NOT NULL,
    name              VARCHAR,
    created           TIMESTAMP DEFAULT now(),
    modified          TIMESTAMP DEFAULT now()
);

CREATE UNIQUE INDEX users_idx ON users(login)