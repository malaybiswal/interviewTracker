# Interview Tracker - Test Suite

Comprehensive unit tests for the Interviewer Rating Feature.

## Test Coverage

The test suite covers all major use cases:

### 1. Interviewer Management (TestInterviewerManagement)
- ✅ Add new interviewer successfully
- ✅ Prevent duplicate interviewers (409 Conflict)
- ✅ Validate required fields (name, company)
- ✅ Require authentication for adding
- ✅ Get list of all interviewers
- ✅ Get specific interviewer details
- ✅ Handle non-existent interviewers (404)

### 2. Search and Filtering (TestSearchAndFiltering)
- ✅ Search by interviewer name
- ✅ Search by company name
- ✅ Case-insensitive search
- ✅ Partial string matching
- ✅ Sort by difficulty rating (descending)

### 3. Rating Submission (TestRatingSubmission)
- ✅ Submit valid ratings (1-5 scale)
- ✅ Test minimum value (1)
- ✅ Test maximum value (5)
- ✅ Optional comments field
- ✅ Reject ratings below 1 (400 Bad Request)
- ✅ Reject ratings above 5 (400 Bad Request)
- ✅ Reject non-integer ratings
- ✅ Reject missing rating value
- ✅ Require authentication (401)
- ✅ Handle non-existent interviewer (404)

### 4. Duplicate Rating Prevention (TestDuplicateRatingPrevention)
- ✅ Prevent duplicate ratings from same user (409 Conflict)
- ✅ Check if user has already rated
- ✅ Return 404 for non-existent user rating

### 5. Rating Calculation (TestRatingCalculation)
- ✅ Calculate average with single rating
- ✅ Calculate average with multiple ratings
- ✅ Round to 2 decimal places
- ✅ Update total review count

### 6. Rating Display (TestRatingDisplay)
- ✅ Display ratings in reverse chronological order (newest first)
- ✅ Include username with each rating
- ✅ Include all rating fields (rating, comments, timestamp)

### 7. Auto-Import (TestAutoImport)
- ✅ Import from interview table
- ✅ Import from interview_round table
- ✅ Skip duplicate entries
- ✅ Ignore null interviewer names
- ✅ Require authentication

### 8. Suggestions Feature (TestSuggestions)
- ✅ Show suggestions from existing interview data
- ✅ Exclude interviewers already in database
- ✅ Apply search filter to suggestions

### 9. Public Access (TestPublicAccess)
- ✅ Public access to interviewer list
- ✅ Public access to interviewer details

## Installation

Install test dependencies:

```bash
pip install -r requirements.txt
```

Or install pytest separately:

```bash
pip install pytest pytest-flask
```

## Running Tests

### Run all tests:
```bash
pytest test_interviewer_rating.py
```

### Run with verbose output:
```bash
pytest test_interviewer_rating.py -v
```

### Run specific test class:
```bash
pytest test_interviewer_rating.py::TestInterviewerManagement
```

### Run specific test:
```bash
pytest test_interviewer_rating.py::TestRatingSubmission::test_submit_rating_success
```

### Run with coverage report:
```bash
pytest test_interviewer_rating.py --cov=routes --cov=models --cov-report=html
```

### Run tests matching a pattern:
```bash
pytest test_interviewer_rating.py -k "rating"
```

## Test Structure

Each test class focuses on a specific feature area:

```
test_interviewer_rating.py
├── TestInterviewerManagement     # CRUD operations
├── TestSearchAndFiltering        # Search and sort functionality
├── TestRatingSubmission          # Rating validation and submission
├── TestDuplicateRatingPrevention # Duplicate prevention logic
├── TestRatingCalculation         # Average calculation
├── TestRatingDisplay             # Rating display and ordering
├── TestAutoImport                # Auto-import from interviews
├── TestSuggestions               # Suggestion feature
└── TestPublicAccess              # Public endpoint access
```

## Fixtures

The test suite uses pytest fixtures for setup:

- `client`: Test client with in-memory SQLite database
- `test_user`: Creates a test user
- `auth_headers`: JWT authentication headers
- `test_interviewer`: Creates a test interviewer
- `test_interview`: Creates a test interview with interviewer name

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test
- Isolated from production data
- Automatically cleaned up after tests

## Continuous Integration

To run tests in CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest test_interviewer_rating.py -v --junitxml=test-results.xml
```

## Expected Output

When all tests pass, you should see:

```
test_interviewer_rating.py::TestInterviewerManagement::test_add_interviewer_success PASSED
test_interviewer_rating.py::TestInterviewerManagement::test_add_interviewer_duplicate PASSED
...
========================= 50 passed in 2.34s =========================
```

## Troubleshooting

### Import Errors
If you get import errors, make sure you're in the project root directory:
```bash
cd /path/to/interviewTracker
pytest test_interviewer_rating.py
```

### Database Errors
The tests use SQLite in-memory database. If you see database errors, check that:
- SQLAlchemy is properly installed
- The `app.py` file is in the same directory
- Models are correctly imported

### JWT Errors
If authentication tests fail, verify:
- Flask-JWT-Extended is installed
- JWT_SECRET_KEY is set in test configuration

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all existing tests still pass
3. Add new test cases for edge cases
4. Update this README with new test coverage

## Test Metrics

Current test coverage:
- **Total Tests**: 50+
- **Test Classes**: 9
- **Lines Covered**: Routes (interviewer endpoints), Models (Interviewer, InterviewerRating)
- **Edge Cases**: Invalid inputs, authentication, duplicates, null values
