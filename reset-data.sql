DELETE FROM Skill;
DELETE FROM BusinessSector;
DELETE FROM WebsiteFeedback;
DELETE FROM DevelopmentFeedback;
DELETE FROM Account;
DELETE FROM Mentor;
DELETE FROM MentorSkill;
DELETE FROM Mentee;
DELETE FROM MenteeSkill;
DELETE FROM Assignment;
DELETE FROM Meeting;
DELETE FROM MenteeMessage;
DELETE FROM MentorMessage;
DELETE FROM MentorFeedback;
DELETE FROM MenteeFeedback;
DELETE FROM Milestone;
DELETE FROM Workshop;

ALTER SEQUENCE skill_skillid_seq RESTART WITH 1;
ALTER SEQUENCE businesssector_businesssectorid_seq RESTART WITH 1;
ALTER SEQUENCE websitefeedback_websitefeedbackid_seq RESTART WITH 1;
ALTER SEQUENCE developmentfeedback_developmentfeedbackid_seq RESTART WITH 1;
ALTER SEQUENCE account_accountid_seq RESTART WITH 1;
ALTER SEQUENCE mentor_mentorid_seq RESTART WITH 1;
ALTER SEQUENCE mentorskill_mentorskillid_seq RESTART WITH 1;
ALTER SEQUENCE mentee_menteeid_seq RESTART WITH 1;
ALTER SEQUENCE menteeskill_menteeskillid_seq RESTART WITH 1;
ALTER SEQUENCE assignment_assignmentid_seq RESTART WITH 1;
ALTER SEQUENCE meeting_meetingid_seq RESTART WITH 1;
ALTER SEQUENCE menteemessage_menteemessageid_seq RESTART WITH 1;
ALTER SEQUENCE mentormessage_mentormessageid_seq RESTART WITH 1;
ALTER SEQUENCE mentorfeedback_mentorfeedbackid_seq RESTART WITH 1;
ALTER SEQUENCE menteefeedback_menteefeedbackid_seq RESTART WITH 1;
ALTER SEQUENCE milestone_milestoneid_seq RESTART WITH 1;
ALTER SEQUENCE workshop_workshopid_seq RESTART WITH 1;