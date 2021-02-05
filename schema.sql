CREATE TABLE users(
    id serial PRIMARY KEY,
    user_id BIGINT,
    name VARCHAR(255),
    is_owner BOOL);
