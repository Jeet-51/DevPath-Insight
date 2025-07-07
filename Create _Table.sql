-- Group 2: DevPath Insight: A Stack Overflow Data-Driven Career Tool
-- Team Members: Jeet Patel, Minju Kim(Lead), FNU Aditi

CREATE DATABASE adt_final_project;

-- Users Table
-- Entered by Minju Kim
CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(256) NOT NULL, 
    SignUpDate DATETIME NOT NULL,
    LastLogin DATETIME NULL,
    INDEX (Email) -- For faster search on email
);

-- Users Profile Table
-- Entered by Minju Kim
CREATE TABLE UserProfile (
    ProfileID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NOT NULL UNIQUE ,
    EducationLevel VARCHAR(255) NOT NULL,
    WorkExperienceYears INT NOT NULL,
    CurrentRole VARCHAR(150),
    DesiredRole VARCHAR(150),
    Industry VARCHAR(150),
    Preferred_Location ENUM('Remote', 'Hybrid', 'Offsite') NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

ALTER TABLE Users
MODIFY COLUMN SignUpDate DATE NOT NULL,
MODIFY COLUMN LastLogin DATE;

-- Skills Table
-- Entered by Jeet Patel
CREATE TABLE Skills (
    SkillID INT AUTO_INCREMENT PRIMARY KEY,
    SkillName VARCHAR(255) NOT NULL UNIQUE,
    Category VARCHAR(255) NOT NULL,
    DifficultyLevel ENUM('Beginner', 'Intermediate', 'Advanced') NOT NULL,
    Trending ENUM('Not Trending', 'Stable', 'Rising', 'Hot') NOT NULL
);

-- Users Skills Table
-- Entered by Jeet Patel
CREATE TABLE UserSkills (
    UserSkillID INT AUTO_INCREMENT PRIMARY KEY,
    ProfileID INT NOT NULL UNIQUE,
    SkillID INT NOT NULL UNIQUE,
    ProficiencyLevel ENUM('Beginner', 'Intermediate', 'Advanced', 'Expert') NOT NULL,
    YearsOfExperience INT,
    LastUsed YEAR,
    InterestLevel ENUM('Low', 'Medium', 'High'),
    FOREIGN KEY (ProfileID) REFERENCES UserProfile(ProfileID),
    FOREIGN KEY (SkillID) REFERENCES Skills(SkillID)
);



-- Desired Position Table
-- Entered by FNU Aditi
CREATE TABLE DesiredPositions (
    DesiredPositionID INT AUTO_INCREMENT PRIMARY KEY,
    ProfileID INT NOT NULL,
    PositionName VARCHAR(150) NOT NULL,
    EstimatedSalary VARCHAR(150),  -- here we are going to impute an range of salary
    LocationPreference VARCHAR(150),
    RemotePreference ENUM('Yes', 'No', 'Flexible') NOT NULL,
    Industry VARCHAR(255),
    FOREIGN KEY (ProfileID) REFERENCES UserProfile(ProfileID)
);

-- Positions Table
-- Entered by FNU Aditi
CREATE TABLE PositionSkills (
    PositionSkillID INT AUTO_INCREMENT PRIMARY KEY,
    DesiredPositionID INT NOT NULL,
    SkillID INT NOT NULL,
    ImportanceLevel ENUM('Essential', 'Desirable') NOT NULL,
    SkillGap ENUM('None', 'Minor', 'Moderate', 'Major') NOT NULL DEFAULT 'None',  -- here using this category it will very useful for the users, they can determine their skill gaps perfectly
    FOREIGN KEY (DesiredPositionID) REFERENCES DesiredPositions(DesiredPositionID),
    FOREIGN KEY (SkillID) REFERENCES Skills(SkillID)
);
ALTER TABLE PositionSkills
ADD COLUMN SkillsRequired VARCHAR(150);
ALTER TABLE PositionSkills DROP COLUMN SkillsRequired;
SELECT * FROM PositionSkills;

-- connecting desired positions with their associated skills through their shared DesiredPositionID, facilitating comprehensive analysis of desired positions and their required skills.
-- Jeet Rakesh Patel
SELECT dp.DesiredPositionID, dp.ProfileID, dp.PositionName, dp.EstimatedSalary, dp.LocationPreference, dp.RemotePreference, dp.Industry,
       ps.PositionSkillID, ps.SkillID, ps.ImportanceLevel, ps.SkillGap
FROM DesiredPositions dp
INNER JOIN PositionSkills ps ON dp.DesiredPositionID = ps.DesiredPositionID;
