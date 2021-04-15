DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS system_users;

CREATE TABLE movies(
  id      INTEGER PRIMARY KEY,
  imdbid  INTEGER NOT NULL,
  rating  INTEGER NOT NULL,
  title   TEXT NOT NULL,
  year    INTEGER NOT NULL
);

CREATE TABLE system_users(
  username    TEXT NOT NULL PRIMARY KEY,
  passw       VARCHAR(550) NOT NULL,
  session_key TEXT
);