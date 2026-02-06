# Implementation Plan: Interview Tracker - Interviewer Rating Feature

## Overview

This task list focuses on implementing the interviewer rating feature for the existing Flask interview tracker application. The current codebase has basic Interviewer and InterviewerComment models, but needs significant enhancements for the rating system, UI integration, and proper API endpoints.

The implementation will add:
- Complete interviewer management UI
- Rating submission and display functionality
- Search and filtering capabilities
- Integration with interview rounds
- Duplicate rating prevention
- Visual difficulty indicators

## Tasks

- [x] 1. Update database models for interviewer rating feature
  - [x] 1.1 Add unique constraint to Interviewer model
    - Add unique constraint on (name, company) combination
    - Add created_at timestamp field
    - Rename difficulty_rating to average_difficulty for consistency
    - _Requirements: 4.2, 10.6_

  - [x] 1.2 Rename and enhance InterviewerComment model to InterviewerRating
    - Rename model from InterviewerComment to InterviewerRating
    - Rename comment field to comments (plural)
    - Add unique constraint on (interviewer_id, user_id) to prevent duplicate ratings
    - Ensure rating field has validation for 1-5 scale
    - _Requirements: 5.1, 5.7_

  - [x] 1.3 Create database migration for model changes
    - Generate migration for Interviewer model updates
    - Generate migration for InterviewerComment to InterviewerRating rename
    - Test migration on development database
    - _Requirements: 10.4_

- [x] 2. Implement interviewer management API endpoints
  - [x] 2.1 Fix and enhance POST /api/interviewers endpoint
    - Change route from /interviewer to /api/interviewers
    - Add proper error handling for duplicate interviewers (409 Conflict)
    - Add input validation for name and company fields
    - Require JWT authentication
    - Return created interviewer with ID in response
    - _Requirements: 4.1, 4.2, 9.6_

  - [x] 2.2 Enhance GET /api/interviewers endpoint
    - Change route from /interviewers to /api/interviewers
    - Add optional search query parameter (filter by name or company)
    - Add sorting by average_difficulty (descending by default)
    - Keep public access (no authentication required)
    - Return properly formatted data with ratings rounded to 2 decimals
    - _Requirements: 4.5, 4.6, 6.1, 6.2, 6.3, 9.5_

  - [x] 2.3 Implement GET /api/interviewers/{id} endpoint
    - Create endpoint to get specific interviewer details
    - Include all ratings with comments and timestamps
    - Sort ratings by created_at descending (newest first)
    - Keep public access (no authentication required)
    - _Requirements: 5.6, 5.8, 6.5, 9.5_

  - [ ]* 2.4 Write unit tests for interviewer management endpoints
    - Test duplicate prevention
    - Test search and filtering
    - Test sorting functionality
    - Test public access
    - _Requirements: 4.1, 4.2, 4.5, 4.6_

- [x] 3. Implement rating submission and management API endpoints
  - [x] 3.1 Fix and enhance POST /api/interviewers/{id}/ratings endpoint
    - Change route from GET /interviewer/{id}/rate to POST /api/interviewers/{id}/ratings
    - Add input validation for rating (must be 1-5 integer)
    - Check for duplicate ratings (same user, same interviewer)
    - Return 409 Conflict if user already rated this interviewer
    - Update average_difficulty calculation correctly
    - Increment total_reviews count
    - Require JWT authentication
    - Return success message with updated interviewer stats
    - _Requirements: 5.1, 5.2, 5.3, 5.7, 9.6_

  - [x] 3.2 Implement GET /api/interviewers/{id}/user-rating endpoint
    - Create endpoint to check if current user has rated this interviewer
    - Return rating data if exists, or 404 if not
    - Require JWT authentication
    - Used by UI to show/hide rating form
    - _Requirements: 5.7_

  - [ ]* 3.3 Write property-based tests for rating system
    - **Property 9: Rating Input Validation**
    - **Property 10: Rating Calculation and Update**
    - **Property 11: Duplicate Rating Prevention**
    - Test rating validation, calculation, and duplicate prevention with random data
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.7**

  - [ ]* 3.4 Write unit tests for rating edge cases
    - Test rating with minimum value (1)
    - Test rating with maximum value (5)
    - Test rating with invalid values (0, 6, non-integer)
    - Test rating without authentication
    - Test duplicate rating attempts
    - _Requirements: 5.1, 5.7, 9.6_

- [x] 4. Create interviewer management UI
  - [x] 4.1 Create interviewers.html page
    - Create HTML template for interviewer management
    - Include page header and navigation
    - Add container for interviewer list table
    - Add "Add Interviewer" button
    - Add search/filter input field
    - _Requirements: 7.1, 7.7_

  - [x] 4.2 Create interviewers.css stylesheet
    - Style interviewer table (responsive design)
    - Style add interviewer button and form
    - Style search/filter input
    - Add difficulty color coding classes:
      - .difficulty-easy (green) for 1.0-2.0
      - .difficulty-medium (yellow/orange) for 2.0-4.0
      - .difficulty-hard (red) for 4.0-5.0
    - Style rating display components
    - _Requirements: 6.6, 7.2_

  - [x] 4.3 Create interviewers.js for interviewer list functionality
    - Fetch and display interviewer list on page load
    - Implement search/filter functionality (filter by name or company)
    - Implement table sorting by difficulty rating
    - Apply difficulty color coding based on average_difficulty value
    - Handle "Add Interviewer" button click (show modal/form)
    - Handle interviewer row click (navigate to detail page)
    - Display error messages for failed operations
    - _Requirements: 4.5, 4.6, 6.6, 7.2, 7.4_

  - [x] 4.4 Implement add interviewer modal/form
    - Create modal dialog or inline form for adding interviewers
    - Add input fields for name and company
    - Add form validation (required fields)
    - Handle form submission (POST to /api/interviewers)
    - Show success message and refresh list on success
    - Show error message on failure (e.g., duplicate)
    - Close modal after successful submission
    - _Requirements: 4.1, 4.2, 7.1, 7.4_

- [x] 5. Create interviewer detail and rating UI
  - [x] 5.1 Create interviewer-detail.html page
    - Create HTML template for individual interviewer view
    - Display interviewer name and company
    - Display average difficulty rating with visual indicator
    - Display total review count
    - Include rating submission form section
    - Include ratings history section
    - _Requirements: 6.5, 6.6, 7.3_

  - [x] 5.2 Create interviewer-detail.css stylesheet
    - Style interviewer header section
    - Style rating submission form (star selector, comment textarea)
    - Style ratings history list
    - Style individual rating cards (rating, comment, date, user)
    - Apply difficulty color coding
    - _Requirements: 6.6, 7.3_

  - [x] 5.3 Create interviewer-detail.js for rating functionality
    - Fetch and display interviewer details on page load
    - Check if current user has already rated (GET /api/interviewers/{id}/user-rating)
    - Show/hide rating form based on whether user has rated
    - Implement star rating selector (1-5 scale)
    - Handle rating form submission (POST to /api/interviewers/{id}/ratings)
    - Display success message after rating submission
    - Refresh page to show new rating in history
    - Display error messages for failed operations
    - Fetch and display all ratings in chronological order (newest first)
    - _Requirements: 5.1, 5.6, 5.7, 5.8, 7.3, 7.4_

  - [ ]* 5.4 Write integration tests for rating UI flow
    - Test complete flow: view interviewer → submit rating → see updated average
    - Test duplicate rating prevention in UI
    - Test rating form validation
    - _Requirements: 5.7, 7.4_

- [ ] 6. Integrate interviewer rating with interview rounds
  - [ ] 6.1 Update interview rounds UI to show interviewer info
    - Modify interview-rounds.js to display interviewer name and company for rounds with linked interviewers
    - Add "Rate Interviewer" button for rounds with linked interviewers
    - Handle "Rate Interviewer" button click (navigate to interviewer detail page)
    - _Requirements: 8.3, 8.4_

  - [ ] 6.2 Update interview round form to support interviewer selection
    - Add interviewer dropdown/autocomplete to round creation form
    - Fetch interviewer list from /api/interviewers
    - Allow selecting interviewer from database
    - Allow entering free-text interviewer name if not in database
    - Save interviewer_id when interviewer is selected from database
    - _Requirements: 8.1, 8.2_

  - [ ]* 6.3 Write tests for interview round and interviewer integration
    - **Property 18: Interview Round and Interviewer Association**
    - Test that interviewer association persists after rating
    - Test displaying interviewer info in rounds view
    - **Validates: Requirements 8.3, 8.5**

- [x] 7. Add navigation and route integration
  - [x] 7.1 Add interviewer management route to Flask app
    - Add route for GET /interviewers (render interviewers.html)
    - Add route for GET /interviewers/{id} (render interviewer-detail.html)
    - Update routes.py with new routes
    - _Requirements: 7.1, 7.3_

  - [x] 7.2 Update navigation menu
    - Add "Interviewers" link to main navigation
    - Update dashboard to include interviewer management section
    - Add breadcrumb navigation for interviewer detail pages
    - _Requirements: 7.1_

- [ ] 8. Final testing and validation
  - [ ]* 8.1 Write property-based tests for search and filtering
    - **Property 8: Interviewer Search and Filtering**
    - Test search functionality with random queries and data
    - **Validates: Requirements 4.6**

  - [ ]* 8.2 Write property-based tests for sorting
    - **Property 7: Interviewer List Sorting**
    - Test sorting by difficulty rating with random data
    - **Validates: Requirements 4.5**

  - [ ]* 8.3 Write property-based tests for visual indicators
    - **Property 15: Difficulty Level Visual Indicators**
    - Test color coding logic with random ratings
    - **Validates: Requirements 6.6**

  - [ ]* 8.4 Write property-based tests for authentication
    - **Property 19: Authentication Requirements for Modifications**
    - Test that rating/adding requires auth with random requests
    - **Validates: Requirements 9.6**

  - [ ] 8.5 Integration testing and manual validation
    - Test complete user flow: add interviewer → link to round → rate interviewer
    - Test search and filtering with various queries
    - Test duplicate prevention (both interviewer and rating)
    - Verify visual indicators display correctly
    - Test public access to interviewer list
    - Test authentication requirements for modifications
    - _Requirements: All (integration validation)_

  - [ ] 8.6 Final checkpoint - Ensure all tests pass
    - Run complete test suite and ensure all tests pass
    - Validate all requirements are met through testing
    - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- Current implementation has basic models but incomplete API and no UI
- Focus is on the interviewer rating feature - other features are already implemented
- Database migrations are required due to model changes (unique constraints, field renames)
- The rating system uses a 1-5 scale where 1 is easiest and 5 is most difficult
- Duplicate prevention is enforced at both database level (unique constraint) and application level (validation)