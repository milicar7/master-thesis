-- Generated DDL for postgresql
-- Generated at: 2025-08-24T13:50:05.156117

CREATE TABLE "test_data_complex_normalization" (
    "StudentID" VARCHAR(8) NOT NULL,
    "CourseID" VARCHAR(14) NOT NULL,
    "StudentName" VARCHAR(26) NOT NULL,
    "CourseName" VARCHAR(54) NOT NULL,
    "Instructor" VARCHAR(26) NOT NULL,
    "Prerequisites" VARCHAR(26) NOT NULL,
    "Credits" INTEGER NOT NULL,
    "ProjectTopic" VARCHAR(36) NOT NULL,
    "ProjectSupervisor" VARCHAR(20) NOT NULL,
    "SupervisorOffice" VARCHAR(16) NOT NULL,
    PRIMARY KEY ("StudentID", "CourseID")
);
