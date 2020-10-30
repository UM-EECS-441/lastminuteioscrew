PRAGMA foreign_keys = ON;

CREATE TABLE patients(
patientID INT NOT NULL,
fullname VARCHAR(40) NOT NULL,
PRIMARY KEY(patientID)
);

CREATE TABLE patient_speaker(
patientID INT NOT NULL,
speakerID INT NOT NULL,
relationship VARCHAR(20),
PRIMARY KEY(patientID, speakerID)
);

CREATE TABLE speakers(
speakerID INT NOT NULL,
fullname VARCHAR(40) NOT NULL,
PRIMARY KEY(speakerID)
);
