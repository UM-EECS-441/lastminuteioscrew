PRAGMA foreign_keys = ON;


INSERT INTO patients(patientID, fullname) VALUES(1, 'Alex Johnson');
INSERT INTO patients(patientID, fullname) VALUES(2, 'Jack Warner');

INSERT INTO patient_speaker(patientID, speakerID, relationship) VALUES (1, 1, 'sister');
INSERT INTO patient_speaker(patientID, speakerID, relationship) VALUES (2, 2, 'daughter');

INSERT INTO speakers(speakerID, fullname) VALUES(1, 'Hannah Jones');
INSERT INTO speakers(speakerID, fullname) VALUES(2, 'Sarah Mcneer');