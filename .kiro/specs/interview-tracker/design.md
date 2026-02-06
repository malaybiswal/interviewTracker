# Design Document: Interview Tracker

## Overview

The Interview Tracker is a Flask-based web application that provides job seekers with a comprehensive platform to manage their interview processes while contributing to a collaborative database of interviewer experiences. The system combines personal interview tracking with community-driven interviewer ratings to help candidates prepare more effectively.

The application follows a RESTful API architecture with JWT-based authentication, providing secure access to personal data while maintaining public access to community interviewer information.

## Architecture

### System Architecture

The application uses a three-tier architecture:

1. **Presentation Layer**: RESTful API endpoints serving JSON responses
2. **Business Logic Layer**: Flask application with route handlers and business rules
3. **Data Layer**: SQLAlchemy ORM with relational database backend

### Technology Stack

- **Backend Framework**: Flask (Python)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens) with Flask-JWT-Extended
- **Database**: MySQL (configurable)
- **Password Security**: Werkzeug password hashing
- **Database Migrations**: Flask-Migrate (Alembic)

### Security Model

- JWT-based stateless authentication with 1-hour token expiration
- Password hashing using Werkzeug's secure methods
- Role-based access control (authenticated vs. public endpoints)
- Input validation and sanitization for all user inputs

## Components and Interfaces

### Authentication System

**Purpose**: Manages user registration, login, and JWT token lifecycle

**Key Components**:
- User registration with duplicate prevention
- Secure password hashing and verification
- JWT token generation and validation
- Token expiration management (1-hour lifespan)

**API Endpoints**:
- `POST /register` - User registration
- `POST /login` - User authentication
- Token validation middleware for protected routes

### Interview Management System

**Purpose**: Handles personal interview tracking and lifecycle management

**Key Components**:
- Interview CRUD operations
- Status tracking (default: "Applied")
- Automatic timestamp recording
- User-specific data isolation

**API Endpoints**:
- `POST /interviews` - Create new interview
- `GET /interviews` - List user's interviews
- `PUT /interviews/{id}` - Update interview
- `DELETE /interviews/{id}` - Remove interview

### Interview Round Tracking System

**Purpose**: Manages multiple interview rounds per job application

**Key Components**:
- Phone screen tracking with date and round number
- Onsite interview tracking with date and round number
- Optional interviewer association
- Referential integrity with parent interviews

**API Endpoints**:
- `POST /interviews/{id}/phone-screens` - Add phone screen
- `POST /interviews/{id}/onsite-interviews` - Add onsite interview
- `GET /interviews/{id}/rounds` - List all rounds for interview

### Interviewer Database System

**Purpose**: Maintains shared database of interviewer information with search and filtering

**Key Components**:
- Interviewer profile management (name, company)
- Duplicate prevention (same name + company)
- Rating aggregation and statistics
- Public access for community benefit
- Search and filtering by name or company
- Sorting by difficulty rating

**API Endpoints**:
- `POST /api/interviewers` - Add new interviewer (requires auth)
- `GET /api/interviewers` - List all interviewers with optional search/filter (public)
- `GET /api/interviewers/{id}` - Get specific interviewer details with ratings (public)

**Business Rules**:
- Interviewer uniqueness is determined by (name, company) combination
- New interviewers start with 0.0 rating and 0 reviews
- Interviewers can be linked to interview rounds via foreign key
- Interviewer list can be sorted by average_difficulty (descending by default)

### Interviewer Rating User Interface

**Purpose**: Provides intuitive web interface for managing and rating interviewers

**Key Components**:
- Interviewer management page with add/list functionality
- Rating submission form with 1-5 scale selector
- Rating history display with comments and timestamps
- Search and filter interface
- Visual difficulty indicators (color coding)
- Integration with interview rounds

**UI Pages**:
- `/interviewers` - Main interviewer list and management page
- `/interviewers/{id}` - Individual interviewer detail page with ratings

**UI Features**:
- Add interviewer form (name, company fields)
- Interviewer table (name, company, avg rating, total reviews)
- Rating form (1-5 star selector, optional comment textarea)
- Rating display (rating value, comment, date, username)
- Search/filter bar (filter by name or company)
- Difficulty color coding:
  - Easy (1.0-2.0): Green
  - Medium (2.0-4.0): Yellow/Orange
  - Hard (4.0-5.0): Red
- Quick rate button from interview rounds view

**User Interactions**:
- Click "Add Interviewer" button → Show modal/form
- Submit interviewer form → Add to database, refresh list
- Click interviewer row → Navigate to detail page
- Submit rating → Update average, show success message
- Search input → Filter table in real-time
- Click "Rate" from interview round → Pre-populate interviewer selection

### Rating and Review System

**Purpose**: Collects and aggregates interviewer difficulty ratings with duplicate prevention

**Key Components**:
- 1-5 scale rating collection (1=easiest, 5=most difficult)
- Real-time average calculation
- Review count tracking
- Optional comment system
- User attribution and timestamps
- Duplicate rating prevention (one rating per user per interviewer)
- Rating history display

**API Endpoints**:
- `POST /api/interviewers/{id}/ratings` - Submit rating (requires auth)
- `GET /api/interviewers/{id}/ratings` - View all ratings for an interviewer (public)
- `GET /api/interviewers/{id}/user-rating` - Check if current user has rated this interviewer (requires auth)

**Business Rules**:
- Users can only rate each interviewer once
- Ratings must be integers between 1 and 5 (inclusive)
- Average rating is calculated as: (sum of all ratings) / (total number of ratings)
- Ratings are displayed in reverse chronological order (newest first)

## Data Models

### User Model
```
User {
  id: Integer (Primary Key)
  username: String (Unique, Required)
  email: String (Unique, Required)
  password_hash: String (Required)
  created_at: DateTime (Auto-generated)
}
```

### Interview Model
```
Interview {
  id: Integer (Primary Key)
  user_id: Integer (Foreign Key -> User.id)
  company_name: String (Required)
  job_title: String (Required)
  recruiter_name: String (Optional)
  job_url: String (Optional)
  comments: Text (Optional)
  status: String (Default: "Applied")
  created_at: DateTime (Auto-generated)
}
```

### PhoneScreen Model
```
PhoneScreen {
  id: Integer (Primary Key)
  interview_id: Integer (Foreign Key -> Interview.id)
  interviewer_id: Integer (Foreign Key -> Interviewer.id, Optional)
  date: Date (Required)
  round_number: Integer (Required)
  created_at: DateTime (Auto-generated)
}
```

### OnsiteInterview Model
```
OnsiteInterview {
  id: Integer (Primary Key)
  interview_id: Integer (Foreign Key -> Interview.id)
  interviewer_id: Integer (Foreign Key -> Interviewer.id, Optional)
  date: Date (Required)
  round_number: Integer (Required)
  created_at: DateTime (Auto-generated)
}
```

### Interviewer Model
```
Interviewer {
  id: Integer (Primary Key)
  name: String (Required)
  company: String (Required)
  average_difficulty: Float (Default: 0.0)  // Renamed from difficulty_rating
  total_reviews: Integer (Default: 0)
  created_at: DateTime (Auto-generated)  // To be added
  
  Unique Constraint: (name, company)  // To be added
}
```

### InterviewerRating Model (Renamed from InterviewerComment)
```
InterviewerRating {
  id: Integer (Primary Key)
  interviewer_id: Integer (Foreign Key -> Interviewer.id)
  user_id: Integer (Foreign Key -> User.id)
  rating: Integer (Required, 1-5 scale)
  comments: Text (Optional)  // Renamed from comment
  created_at: DateTime (Auto-generated)
  
  Unique Constraint: (interviewer_id, user_id)  // To be added - prevents duplicate ratings
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User Registration and Duplicate Prevention
*For any* valid user registration data (username, email, password), the system should create a new user account with encrypted password storage, and for any attempt to register with existing credentials, the system should prevent duplicate creation and return an error.
**Validates: Requirements 1.1, 1.2**

### Property 2: Authentication and Token Management
*For any* valid user credentials, the system should authenticate the user and return a valid JWT token, and for any invalid credentials or expired tokens, the system should reject access and return appropriate errors.
**Validates: Requirements 1.3, 1.4, 1.5, 9.4**

### Property 3: Interview Creation and Association
*For any* authenticated user and valid interview data, the system should create a new interview record with default status "Applied", automatic timestamp, and proper user association.
**Validates: Requirements 2.1, 2.2, 2.3, 2.5**

### Property 4: Interview Round Management
*For any* valid interview round data (phone screen or onsite), the system should record the date, round number, and optional interviewer association while maintaining referential integrity with the parent interview.
**Validates: Requirements 3.1, 3.2, 3.4**

### Property 5: Multiple Rounds Per Interview
*For any* interview, the system should allow multiple phone screens and onsite interviews to be associated with it.
**Validates: Requirements 3.3**

### Property 6: Interviewer Database Management and Uniqueness
*For any* valid interviewer data, the system should create new interviewer records with zero initial ratings, prevent duplicates based on name and company combination, and allow linking to interview rounds.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 10.6**

### Property 7: Interviewer List Sorting
*For any* list of interviewers, when sorted by difficulty rating, each interviewer's average_difficulty should be greater than or equal to the next interviewer's average_difficulty.
**Validates: Requirements 4.5**

### Property 8: Interviewer Search and Filtering
*For any* search query and interviewer database, all returned results should contain the search term in either the name or company field.
**Validates: Requirements 4.6**

### Property 9: Rating Input Validation
*For any* rating submission, the system should accept integer values from 1 to 5 (inclusive) and reject any values outside this range with an appropriate error.
**Validates: Requirements 5.1**

### Property 10: Rating Calculation and Update
*For any* valid rating submission (1-5 scale), the system should update the interviewer's average difficulty rating correctly using the formula (sum of all ratings) / (total number of ratings), and increment the review count.
**Validates: Requirements 5.2, 5.3**

### Property 11: Duplicate Rating Prevention
*For any* user and interviewer combination, the system should allow only one rating submission, and any subsequent rating attempts by the same user for the same interviewer should be rejected with an error.
**Validates: Requirements 5.7**

### Property 12: Rating Display Completeness and Ordering
*For any* interviewer with ratings, when retrieving the ratings list, all ratings should be returned with complete data (rating value, comments, timestamp, user identity), and they should be ordered with the most recent ratings first (descending chronological order).
**Validates: Requirements 5.6, 5.8, 6.5, 7.5, 7.6**

### Property 13: Optional Data Fields
*For any* interview or rating creation, the system should properly handle optional fields (job URLs, comments, recruiter names) without requiring them.
**Validates: Requirements 2.4, 5.4**

### Property 14: Public Interviewer Information Access
*For any* request for interviewer information, the system should return all interviewers with properly formatted data (names, companies, ratings rounded to two decimal places, review counts) without requiring authentication.
**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 9.5**

### Property 15: Difficulty Level Visual Indicators
*For any* interviewer with an average difficulty rating, the system should apply the correct visual indicator: green for ratings 1.0-2.0 (easy), yellow/orange for ratings 2.0-4.0 (medium), and red for ratings 4.0-5.0 (hard).
**Validates: Requirements 6.6**

### Property 16: Interviewer Table Data Display
*For any* interviewer list display, each row should contain the interviewer name, company, average rating (rounded to 2 decimals), and total review count.
**Validates: Requirements 7.2**

### Property 17: Rating Submission Feedback
*For any* rating submission attempt, the system should provide immediate visual feedback indicating either success (with confirmation message) or error (with descriptive error message).
**Validates: Requirements 7.4**

### Property 18: Interview Round and Interviewer Association
*For any* interview round with a linked interviewer, the system should display the interviewer's name and company, and maintain this association even after ratings are submitted.
**Validates: Requirements 8.3, 8.5**

### Property 19: Authentication Requirements for Modifications
*For any* request to submit ratings or add interviewers, the system should require valid JWT authentication and reject unauthenticated requests with a 401 error.
**Validates: Requirements 9.6**

### Property 20: Data Security and Access Control
*For any* protected endpoint access, the system should require valid JWT authentication, and for any user accessing interview data, the system should only return data belonging to that user with properly hashed passwords.
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 21: Database Integrity Constraints
*For any* database operation, the system should enforce foreign key constraints, require unique usernames and emails, and prevent deletion of referenced records.
**Validates: Requirements 10.1, 10.2, 10.3**

## Error Handling

### Authentication Errors
- **Invalid Credentials**: Return 401 Unauthorized with descriptive error message
- **Expired Tokens**: Return 401 Unauthorized with token expiration notice
- **Missing Authentication**: Return 401 Unauthorized for protected endpoints

### Validation Errors
- **Duplicate Registration**: Return 409 Conflict with specific field information
- **Invalid Rating Scale**: Return 400 Bad Request for ratings outside 1-5 range
- **Missing Required Fields**: Return 400 Bad Request with field-specific messages
- **Invalid Data Types**: Return 400 Bad Request with type validation errors

### Database Errors
- **Foreign Key Violations**: Return 400 Bad Request with relationship information
- **Unique Constraint Violations**: Return 409 Conflict with constraint details
- **Connection Errors**: Return 500 Internal Server Error with retry guidance

### Resource Errors
- **Interview Not Found**: Return 404 Not Found for non-existent interviews
- **Interviewer Not Found**: Return 404 Not Found for non-existent interviewers
- **Unauthorized Access**: Return 403 Forbidden for accessing other users' data

## Testing Strategy

### Dual Testing Approach

The application will use both unit testing and property-based testing to ensure comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
- Authentication flow with known credentials
- Interview creation with specific data sets
- Rating calculations with predetermined values
- Error handling for specific failure scenarios

**Property Tests**: Verify universal properties across all inputs
- User registration with randomly generated valid data
- Interview management across various data combinations
- Rating system behavior with random rating sequences
- Database integrity across random operation sequences

### Property-Based Testing Configuration

- **Testing Framework**: Hypothesis (Python property-based testing library)
- **Minimum Iterations**: 100 iterations per property test
- **Test Tagging**: Each property test references its design document property
- **Tag Format**: **Feature: interview-tracker, Property {number}: {property_text}**

### Testing Coverage Areas

**Authentication and Security**:
- Property tests for user registration and login flows
- Unit tests for specific JWT token scenarios
- Security validation for password hashing and token expiration

**Data Management**:
- Property tests for interview and interviewer CRUD operations
- Unit tests for specific data validation scenarios
- Integration tests for database constraint enforcement

**Business Logic**:
- Property tests for rating calculations and aggregations
- Unit tests for specific business rule implementations
- End-to-end tests for complete user workflows

**API Endpoints**:
- Property tests for request/response validation
- Unit tests for specific endpoint behaviors
- Integration tests for authentication middleware

The testing strategy ensures that both specific use cases and general system behaviors are thoroughly validated, providing confidence in the system's correctness and reliability.