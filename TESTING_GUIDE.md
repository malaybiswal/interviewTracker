# Testing Guide - Quick Reference

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
./run_tests.sh

# Or use pytest directly
pytest test_interviewer_rating.py -v
```

## Test Organization

### 📁 Test File Structure

```
test_interviewer_rating.py
├── Fixtures (setup/teardown)
│   ├── client          - Test client with in-memory DB
│   ├── test_user       - Creates test user
│   ├── auth_headers    - JWT authentication
│   ├── test_interviewer - Creates test interviewer
│   └── test_interview  - Creates test interview
│
└── Test Classes (50+ tests)
    ├── TestInterviewerManagement (8 tests)
    ├── TestSearchAndFiltering (5 tests)
    ├── TestRatingSubmission (10 tests)
    ├── TestDuplicateRatingPrevention (3 tests)
    ├── TestRatingCalculation (3 tests)
    ├── TestRatingDisplay (2 tests)
    ├── TestAutoImport (5 tests)
    ├── TestSuggestions (3 tests)
    └── TestPublicAccess (2 tests)
```

## Common Test Commands

### Run Specific Test Categories

```bash
# All interviewer management tests
pytest test_interviewer_rating.py::TestInterviewerManagement -v

# All rating submission tests
pytest test_interviewer_rating.py::TestRatingSubmission -v

# All search/filter tests
pytest test_interviewer_rating.py::TestSearchAndFiltering -v
```

### Run Tests by Pattern

```bash
# All tests with "duplicate" in name
pytest test_interviewer_rating.py -k "duplicate" -v

# All tests with "auth" in name
pytest test_interviewer_rating.py -k "auth" -v

# All tests with "rating" in name
pytest test_interviewer_rating.py -k "rating" -v
```

### Run Single Test

```bash
# Specific test by full path
pytest test_interviewer_rating.py::TestRatingSubmission::test_submit_rating_success -v
```

## Test Coverage by Feature

### ✅ Interviewer CRUD Operations
- `test_add_interviewer_success` - Add new interviewer
- `test_add_interviewer_duplicate` - Duplicate prevention
- `test_add_interviewer_missing_name` - Validation
- `test_add_interviewer_missing_company` - Validation
- `test_add_interviewer_no_auth` - Auth requirement
- `test_get_interviewers_list` - List all
- `test_get_interviewer_detail` - Get single
- `test_get_interviewer_not_found` - 404 handling

### 🔍 Search & Filter
- `test_search_by_name` - Name search
- `test_search_by_company` - Company search
- `test_search_case_insensitive` - Case handling
- `test_search_partial_match` - Partial matching
- `test_sort_by_difficulty_descending` - Sorting

### ⭐ Rating Submission
- `test_submit_rating_success` - Valid submission
- `test_submit_rating_minimum_value` - Min value (1)
- `test_submit_rating_maximum_value` - Max value (5)
- `test_submit_rating_without_comment` - Optional field
- `test_submit_rating_invalid_too_low` - Below min
- `test_submit_rating_invalid_too_high` - Above max
- `test_submit_rating_non_integer` - Type validation
- `test_submit_rating_missing_value` - Required field
- `test_submit_rating_no_auth` - Auth requirement
- `test_submit_rating_interviewer_not_found` - 404

### 🚫 Duplicate Prevention
- `test_duplicate_rating_same_user` - Prevent duplicates
- `test_check_user_rating_exists` - Check existing
- `test_check_user_rating_not_exists` - Check non-existing

### 🧮 Rating Calculation
- `test_average_calculation_single_rating` - Single rating
- `test_average_calculation_multiple_ratings` - Multiple ratings
- `test_rating_rounded_to_two_decimals` - Rounding

### 📊 Rating Display
- `test_ratings_ordered_newest_first` - Chronological order
- `test_rating_includes_username` - Complete data

### 📥 Auto-Import
- `test_import_from_interview_table` - Import from interviews
- `test_import_from_interview_round_table` - Import from rounds
- `test_import_skips_duplicates` - Skip existing
- `test_import_ignores_null_names` - Handle nulls
- `test_import_requires_auth` - Auth requirement

### 💡 Suggestions
- `test_suggestions_from_interviews` - Show suggestions
- `test_suggestions_exclude_existing` - Exclude DB entries
- `test_suggestions_with_search` - Filter suggestions

### 🌐 Public Access
- `test_get_interviewers_no_auth` - Public list
- `test_get_interviewer_detail_no_auth` - Public detail

## Understanding Test Results

### ✅ Passing Test
```
test_interviewer_rating.py::TestRatingSubmission::test_submit_rating_success PASSED [100%]
```

### ❌ Failing Test
```
test_interviewer_rating.py::TestRatingSubmission::test_submit_rating_success FAILED [100%]
E       AssertionError: assert 400 == 201
```

### ⚠️ Skipped Test
```
test_interviewer_rating.py::TestRatingSubmission::test_submit_rating_success SKIPPED [100%]
```

## Debugging Failed Tests

### 1. Run with verbose output
```bash
pytest test_interviewer_rating.py -v
```

### 2. Run with print statements visible
```bash
pytest test_interviewer_rating.py -v -s
```

### 3. Run with full traceback
```bash
pytest test_interviewer_rating.py -v --tb=long
```

### 4. Run single failing test
```bash
pytest test_interviewer_rating.py::TestClass::test_name -v
```

### 5. Drop into debugger on failure
```bash
pytest test_interviewer_rating.py --pdb
```

## Test Data

All tests use isolated in-memory SQLite database:
- **Fresh database** for each test
- **No impact** on production data
- **Automatic cleanup** after tests

### Default Test Data
- **User**: username='testuser', email='test@example.com'
- **Interviewer**: name='John Doe', company='TechCorp'
- **Interview**: company='TechCorp', interviewer='Jane Smith'

## Common Issues & Solutions

### Issue: Import errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: Run from project root directory
```bash
cd /path/to/interviewTracker
pytest test_interviewer_rating.py
```

### Issue: Database errors
```
sqlalchemy.exc.OperationalError
```
**Solution**: Check that models.py and app.py are in same directory

### Issue: JWT errors
```
RuntimeError: Working outside of application context
```
**Solution**: Tests use app context automatically via fixtures

### Issue: Tests pass locally but fail in CI
**Solution**: Ensure requirements.txt includes all test dependencies

## Best Practices

### ✅ DO
- Run tests before committing code
- Add tests for new features
- Keep tests isolated and independent
- Use descriptive test names
- Test both success and failure cases

### ❌ DON'T
- Modify production database in tests
- Make tests depend on each other
- Skip writing tests for "simple" code
- Ignore failing tests
- Test implementation details

## Performance

Typical test execution times:
- **All tests**: ~2-5 seconds
- **Single test class**: ~0.5-1 second
- **Single test**: ~0.1-0.2 seconds

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest test_interviewer_rating.py -v
```

## Next Steps

1. **Run the tests**: `./run_tests.sh`
2. **Check coverage**: `./run_tests.sh coverage`
3. **Fix any failures**: Debug with `-v` flag
4. **Add new tests**: For new features
5. **Integrate with CI**: Add to deployment pipeline

## Support

For issues or questions:
1. Check TEST_README.md for detailed documentation
2. Review test output for specific error messages
3. Run with `-v` flag for more details
4. Check that all dependencies are installed
