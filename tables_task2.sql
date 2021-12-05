# 

CREATE TABLE users (
    "id" serial NOT NULL PRIMARY KEY,
    "username" VARCHAR NOT NULL UNIQUE,
    "hashpassword" VARCHAR NULL,
    "email" VARCHAR,
);

CREATE TABLE reset_tokens (
    "id" serial NOT NULL PRIMARY KEY,
    "reset_token" VARCHAR NOT NULL,
    "create_datetime" DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username_id) REFERENCES users(id),
)