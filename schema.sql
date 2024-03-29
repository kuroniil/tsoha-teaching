CREATE TABLE Courses (
  id SERIAL PRIMARY KEY,
  teacher_id INTEGER REFERENCES Users(id),
  name TEXT UNIQUE,
  visible BOOLEAN
);

CREATE TABLE CourseStudents (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES Users(id),
  course_id INTEGER REFERENCES Courses(id)
);

CREATE TABLE ChoiceProblems (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES Courses(id),
  question TEXT,
  visible BOOLEAN,
  answer INTEGER
);

CREATE TABLE Users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE,
  password TEXT,
  title TEXT
);

CREATE TABLE TextContent (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES Courses(id),
  visible BOOLEAN,
  content TEXT
);

CREATE TABLE TextProblems (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES Courses(id),
  problem_id INTEGER,
  visible BOOLEAN,
  answer TEXT,
  question TEXT
);

CREATE TABLE Choices (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES Courses(id),
  choice_number INTEGER,
  content TEXT,
  problem_id INTEGER REFERENCES ChoiceProblems(id)
);

CREATE TABLE SolvedProblems (
  id SERIAL PRIMARY KEY,
  course_id INTEGER REFERENCES Courses(id),
  problem_id INTEGER,
  user_id INTEGER REFERENCES Users(id),
  type TEXT
);

CREATE TABLE CourseProblems (
  course_id INTEGER REFERENCES Courses(id),
  problem_id INTEGER,
  id_number INTEGER
);