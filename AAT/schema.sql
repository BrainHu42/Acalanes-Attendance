DROP TABLE IF EXISTS teacher;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS stranger;

CREATE TABLE teacher (
  email TEXT PRIMARY KEY,
  password TEXT NOT NULL,
  currentMeeting TEXT,
  tardyTime INTEGER NOT NULL,
  name TEXT NOT NULL,
  accessToken TEXT NOT NULL,
  refreshToken TEXT NOT NULL,
  userID TEXT NOT NULL
);

CREATE TABLE student (
  name TEXT PRIMARY KEY,
  userID TEXT UNIQUE,
  currentMeeting TEXT,
  teacher1 TEXT,
  teacher2 TEXT,
  teacher3 TEXT,
  teacher4 TEXT,
  teacher5 TEXT,
  teacher6 TEXT,
  teacher7 TEXT
);

CREATE TABLE stranger (
  userID TEXT PRIMARY KEY,
  currentMeeting TEXT,
  name TEXT
);