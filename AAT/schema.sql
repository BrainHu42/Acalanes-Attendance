DROP TABLE IF EXISTS teacher;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS stranger;
DROP TABLE IF EXISTS history;
DROP TABLE IF EXISTS data;

CREATE TABLE teacher (
  email TEXT PRIMARY KEY,
  password TEXT NOT NULL,
  currentMeeting TEXT,
  startTime TIMESTAMPTZ NOT NULL,
  userID TEXT UNIQUE NOT NULL,
  tardyTime INTEGER NOT NULL,
  name TEXT NOT NULL,
  accessToken TEXT NOT NULL,
  refreshToken TEXT NOT NULL
);

CREATE TABLE student (
  name TEXT PRIMARY KEY,
  currentMeeting TEXT,
  joinTime TIMESTAMPTZ,
  teacher1 TEXT,
  teacher2 TEXT,
  teacher3 TEXT,
  teacher4 TEXT,
  teacher5 TEXT,
  teacher6 TEXT,
  teacher7 TEXT,
  teacher8 TEXT,
  userID TEXT UNIQUE,
  confidence INTEGER
);

CREATE TABLE stranger (
  userID TEXT NOT NULL,
  currentMeeting TEXT,
  joinTime TIMESTAMPTZ,
  name TEXT UNIQUE
);

CREATE TABLE history (
  absent TEXT ARRAY,
  tardy TEXT ARRAY,
  period TEXT,
  teacher TEXT,
  stranger TEXT ARRAY,
  date TIMESTAMPTZ
);

CREATE TABLE data (
  json TEXT,
  event TEXT
);