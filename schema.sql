DROP TABLE Skill CASCADE;
CREATE TABLE Skill (
  skillId SERIAL PRIMARY KEY,
  name VARCHAR
);

DROP TABLE BusinessSector CASCADE;
CREATE TABLE BusinessSector (
  businessSectorId SERIAL PRIMARY KEY,
  name VARCHAR
);

DROP TABLE WebsiteFeedback CASCADE;
CREATE TABLE WebsiteFeedback (
  websiteFeedbackId SERIAL PRIMARY KEY,
  message VARCHAR
);

DROP TABLE DevelopmentFeedback CASCADE;
CREATE TABLE DevelopmentFeedback (
  developmentFeedbackId SERIAL PRIMARY KEY,
  content VARCHAR,
  metric DOUBLE PRECISION
);

DROP TABLE Account CASCADE;
CREATE TABLE Account (
  accountId SERIAL PRIMARY KEY,
  name VARCHAR,
  email VARCHAR,
  passwordHash BYTEA,
  dob DATE,
  businessSectorId INTEGER REFERENCES BusinessSector(businessSectorId)
);

DROP TABLE Mentor CASCADE;
CREATE TABLE Mentor (
  mentorId SERIAL PRIMARY KEY,
  accountId INTEGER REFERENCES Account(accountId)
);

DROP TABLE MentorSkill CASCADE;
CREATE TABLE MentorSkill (
  mentorSkillId SERIAL PRIMARY KEY,
  mentorId INTEGER REFERENCES Mentor(mentorId),
  skillId INTEGER REFERENCES Skill(skillId)
);

DROP TABLE Mentee CASCADE;
CREATE TABLE Mentee (
  menteeId SERIAL PRIMARY KEY,
  accountId INTEGER REFERENCES Account(accountId)
);

DROP TABLE MenteeSkill CASCADE;
CREATE TABLE MenteeSkill (
  menteeSkillId SERIAL PRIMARY KEY,
  menteeId INTEGER REFERENCES Mentee(menteeId),
  skillId INTEGER REFERENCES Skill(skillId)
);

DROP TABLE Assignment CASCADE;
CREATE TABLE Assignment (
  assignmentId SERIAL PRIMARY KEY,
  mentorId INTEGER REFERENCES Mentor(mentorId),
  menteeId INTEGER REFERENCES Mentee(menteeId)
);

DROP TABLE Meeting CASCADE;
CREATE TABLE Meeting (
  meetingId SERIAL PRIMARY KEY,
  assignmentId INTEGER REFERENCES Assignment(assignmentId),
  link VARCHAR,
  start TIMESTAMP,
  duration INTEGER /* in minutes */
);

DROP TABLE MenteeMessage CASCADE;
CREATE TABLE MenteeMessage (
  menteeMessageId SERIAL PRIMARY KEY,
  menteeId INTEGER REFERENCES Mentee(menteeId),
  message VARCHAR
);

DROP TABLE MentorMessage CASCADE;
CREATE TABLE MentorMessage (
  mentorMessageId SERIAL PRIMARY KEY,
  mentorId INTEGER REFERENCES Mentor(mentorId),
  message VARCHAR
);

DROP TABLE MentorFeedback CASCADE;
CREATE TABLE MentorFeedback (
  mentorFeedbackId SERIAL PRIMARY KEY,
  assignmentId INTEGER REFERENCES Assignment(assignmentId),
  rating DOUBLE PRECISION
);

DROP TABLE MenteeFeedback CASCADE;
CREATE TABLE MenteeFeedback (
  menteeFeedbackId SERIAL PRIMARY KEY,
  assignmentId INTEGER REFERENCES Assignment(assignmentId),
  rating DOUBLE PRECISION,
  developmentFeedbackId INTEGER REFERENCES DevelopmentFeedback(developmentFeedbackId)
);

DROP TABLE Milestone CASCADE;
CREATE TABLE Milestone (
  milestoneId SERIAL PRIMARY KEY,
  menteeId INTEGER REFERENCES Mentee(menteeId),
  content VARCHAR,
  completed BOOLEAN
);

DROP TABLE Workshop CASCADE;
CREATE TABLE Workshop (
  workshopId SERIAL PRIMARY KEY,
  skillId INTEGER REFERENCES Skill(skillId),
  start TIMESTAMP,
  duration INTEGER, /* in minutes */
  link VARCHAR
);