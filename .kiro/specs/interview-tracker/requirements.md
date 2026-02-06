# Requirements Document

## Introduction

The Interview Tracker is a web-based application that helps job seekers systematically track their interview processes and share knowledge about interviewers. The system provides a collaborative platform where users can manage their job applications, track interview rounds, and contribute to a shared database of interviewer experiences and difficulty ratings.

## Glossary

- **System**: The Interview Tracker application
- **User**: A registered job seeker using the application
- **Interview**: A job application opportunity with a specific company
- **Interviewer**: An individual who conducts interviews at companies
- **Phone_Screen**: A preliminary interview conducted via phone or video call
- **Onsite_Interview**: An in-person or virtual interview session
- **Rating**: A numerical score (1-5) indicating interviewer difficulty
- **JWT_Token**: JSON Web Token used for user authentication

## Requirements

### Requirement 1: User Authentication and Management

**User Story:** As a job seeker, I want to create an account and securely log in, so that I can track my personal interview data.

#### Acceptance Criteria

1. WHEN a user provides valid registration information, THE System SHALL create a new user account with encrypted password storage
2. WHEN a user attempts to register with an existing username or email, THE System SHALL prevent duplicate account creation and return an error message
3. WHEN a user provides valid login credentials, THE System SHALL authenticate the user and return a JWT_Token
4. WHEN a user provides invalid login credentials, THE System SHALL reject the authentication attempt and return an error message
5. THE System SHALL expire JWT_Tokens after one hour to maintain security

### Requirement 2: Interview Management

**User Story:** As a job seeker, I want to add and track my job interviews, so that I can organize my job search process.

#### Acceptance Criteria

1. WHEN an authenticated user submits interview details, THE System SHALL create a new interview record with company name, job title, and optional recruiter information
2. WHEN creating an interview, THE System SHALL set the default status to "Applied"
3. WHEN storing interview data, THE System SHALL record the creation timestamp automatically
4. THE System SHALL allow users to include job URLs and comments with interview records
5. THE System SHALL associate each interview with the authenticated user's account

### Requirement 3: Interview Round Tracking

**User Story:** As a job seeker, I want to track different rounds of interviews, so that I can monitor my progress through each company's process.

#### Acceptance Criteria

1. WHEN a user adds a phone screen, THE System SHALL record the date, round number, and optional interviewer association
2. WHEN a user adds an onsite interview, THE System SHALL record the date, round number, and optional interviewer association
3. THE System SHALL allow multiple phone screens and onsite interviews per job interview
4. THE System SHALL maintain referential integrity between interview rounds and their parent interviews

### Requirement 4: Interviewer Database Management

**User Story:** As a job seeker, I want to add interviewers to a shared database, so that the community can benefit from collective knowledge.

#### Acceptance Criteria

1. WHEN a user adds a new interviewer, THE System SHALL store the interviewer's name and company
2. WHEN a user attempts to add a duplicate interviewer (same name and company), THE System SHALL prevent the duplicate and return an error message
3. THE System SHALL initialize new interviewers with zero difficulty rating and zero total reviews
4. THE System SHALL allow linking interviewers to specific interview rounds
5. WHEN displaying the interviewer list, THE System SHALL show interviewers sorted by average difficulty rating in descending order
6. WHEN a user searches for an interviewer, THE System SHALL filter results by name or company

### Requirement 5: Interviewer Rating and Review System

**User Story:** As a job seeker, I want to rate and review interviewers, so that I can help other candidates prepare for their interviews.

#### Acceptance Criteria

1. WHEN a user submits an interviewer rating, THE System SHALL accept ratings on a 1-5 scale where 1 is easiest and 5 is most difficult
2. WHEN a rating is submitted, THE System SHALL update the interviewer's average difficulty rating using all submitted ratings
3. WHEN a rating is submitted, THE System SHALL increment the interviewer's total review count
4. THE System SHALL allow users to include optional comments with their ratings
5. THE System SHALL record the timestamp and user identity for each rating submission
6. WHEN a user views an interviewer's ratings, THE System SHALL display all individual ratings with comments and timestamps
7. THE System SHALL prevent users from rating the same interviewer multiple times
8. WHEN displaying ratings, THE System SHALL show the most recent ratings first

### Requirement 6: Interviewer Information Retrieval

**User Story:** As a job seeker, I want to view interviewer ratings and information, so that I can prepare appropriately for upcoming interviews.

#### Acceptance Criteria

1. WHEN a user requests interviewer information, THE System SHALL return a list of all interviewers with their ratings
2. THE System SHALL display interviewer names, companies, average difficulty ratings, and total review counts
3. THE System SHALL round difficulty ratings to two decimal places for display
4. THE System SHALL make interviewer information publicly accessible without authentication requirements
5. WHEN a user views a specific interviewer, THE System SHALL display all ratings and comments for that interviewer
6. THE System SHALL provide a visual indicator (color coding or icons) for difficulty levels (easy: 1-2, medium: 2-4, hard: 4-5)

### Requirement 7: Interviewer Rating User Interface

**User Story:** As a job seeker, I want an intuitive interface to add and rate interviewers, so that I can easily contribute to the community knowledge base.

#### Acceptance Criteria

1. WHEN a user accesses the interviewer management page, THE System SHALL display a form to add new interviewers with name and company fields
2. WHEN a user views the interviewer list, THE System SHALL display a table with interviewer name, company, average rating, and total reviews
3. WHEN a user clicks on an interviewer, THE System SHALL display a rating form with a 1-5 scale selector and optional comment field
4. WHEN a user submits a rating, THE System SHALL provide immediate visual feedback of success or error
5. THE System SHALL display existing ratings and comments for each interviewer in chronological order
6. WHEN viewing ratings, THE System SHALL show the rating value, comment, and submission date for each review
7. THE System SHALL provide a search/filter interface to find interviewers by name or company

### Requirement 8: Interview Round and Interviewer Integration

**User Story:** As a job seeker, I want to link interviewers to my interview rounds, so that I can track who I interviewed with and later rate them.

#### Acceptance Criteria

1. WHEN adding an interview round, THE System SHALL provide an option to select an interviewer from the database
2. WHEN adding an interview round, THE System SHALL allow entering a free-text interviewer name if not in database
3. WHEN viewing interview rounds, THE System SHALL display the linked interviewer name and company
4. WHEN viewing interview rounds with a linked interviewer, THE System SHALL provide a quick link to rate that interviewer
5. THE System SHALL maintain the association between interview rounds and interviewers even after ratings are submitted

### Requirement 9: Data Security and Access Control

**User Story:** As a job seeker, I want my personal interview data to be secure, so that my job search information remains private.

#### Acceptance Criteria

1. WHEN accessing protected endpoints, THE System SHALL require valid JWT authentication
2. WHEN a user accesses interview data, THE System SHALL only return interviews belonging to that user
3. THE System SHALL hash all user passwords before storing them in the database
4. THE System SHALL validate JWT tokens and reject expired or invalid tokens
5. THE System SHALL allow public access to interviewer information and ratings without authentication
6. THE System SHALL require authentication for submitting ratings and adding interviewers

### Requirement 10: Database Integrity and Performance

**User Story:** As a system administrator, I want the database to maintain data integrity, so that the application remains reliable and consistent.

#### Acceptance Criteria

1. THE System SHALL enforce foreign key constraints between related tables
2. THE System SHALL require unique usernames and email addresses
3. THE System SHALL prevent deletion of referenced records through foreign key constraints
4. THE System SHALL use database migrations to manage schema changes safely
5. THE System SHALL disable SQLAlchemy modification tracking to optimize performance
6. THE System SHALL enforce unique constraint on interviewer (name, company) combination to prevent duplicates