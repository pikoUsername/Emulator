CREATE TABLE guild(
    guild_id BIGINT PRIMARY KEY,
    title VARCHAR(255));

CREATE TABLE users(
    user_id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    is_owner BOOL,
    referals INTEGER REFERENCES referal(id),
    guild_id BIGINT REFERENCES guild (guild_id)
);

CREATE TABLE referal(
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users (user_id) ON DELETE CASCADE
);
