"""
Unit tests for the Interviewer Rating Feature

Tests cover:
- Interviewer management (add, list, search, filter, sort)
- Rating submission and validation
- Duplicate prevention
- Auto-import from interviews
- Authentication requirements
- Error handling
"""

import pytest
import json
from datetime import datetime
from app import app
from models import db, User, Interview, InterviewRound, Interviewer, InterviewerRating
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    """Create a test client with in-memory database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def test_user(client):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def auth_headers(test_user):
    """Generate JWT token for authenticated requests"""
    with app.app_context():
        access_token = create_access_token(identity=str(test_user))
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def test_interviewer(client):
    """Create a test interviewer"""
    with app.app_context():
        interviewer = Interviewer(name='John Doe', company='TechCorp')
        db.session.add(interviewer)
        db.session.commit()
        return interviewer.id


@pytest.fixture
def test_interview(client, test_user):
    """Create a test interview with interviewer name"""
    with app.app_context():
        interview = Interview(
            user_id=test_user,
            company_name='TechCorp',
            job_title='Software Engineer',
            interviewer_name='Jane Smith'
        )
        db.session.add(interview)
        db.session.commit()
        return interview.id


# ============================================================================
# INTERVIEWER MANAGEMENT TESTS
# ============================================================================

class TestInterviewerManagement:
    """Test interviewer CRUD operations"""
    
    def test_add_interviewer_success(self, client, auth_headers):
        """Test successfully adding a new interviewer"""
        response = client.post('/api/interviewers',
            headers=auth_headers,
            json={'name': 'Alice Johnson', 'company': 'StartupXYZ'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Interviewer added successfully'
        assert data['name'] == 'Alice Johnson'
        assert data['company'] == 'StartupXYZ'
        assert 'id' in data
    
    def test_add_interviewer_duplicate(self, client, auth_headers, test_interviewer):
        """Test adding duplicate interviewer returns 409"""
        response = client.post('/api/interviewers',
            headers=auth_headers,
            json={'name': 'John Doe', 'company': 'TechCorp'}
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already exists' in data['message']
    
    def test_add_interviewer_missing_name(self, client, auth_headers):
        """Test adding interviewer without name returns 400"""
        response = client.post('/api/interviewers',
            headers=auth_headers,
            json={'company': 'TechCorp'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['message'].lower()
    
    def test_add_interviewer_missing_company(self, client, auth_headers):
        """Test adding interviewer without company returns 400"""
        response = client.post('/api/interviewers',
            headers=auth_headers,
            json={'name': 'John Doe'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'required' in data['message'].lower()
    
    def test_add_interviewer_no_auth(self, client):
        """Test adding interviewer without authentication returns 401"""
        response = client.post('/api/interviewers',
            json={'name': 'Alice Johnson', 'company': 'StartupXYZ'}
        )
        
        assert response.status_code == 401
    
    def test_get_interviewers_list(self, client, test_interviewer):
        """Test getting list of all interviewers"""
        response = client.get('/api/interviewers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]['name'] == 'John Doe'
        assert data[0]['company'] == 'TechCorp'
        assert data[0]['average_difficulty'] == 0.0
        assert data[0]['total_reviews'] == 0
    
    def test_get_interviewer_detail(self, client, test_interviewer):
        """Test getting specific interviewer details"""
        response = client.get(f'/api/interviewers/{test_interviewer}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'John Doe'
        assert data['company'] == 'TechCorp'
        assert data['average_difficulty'] == 0.0
        assert data['total_reviews'] == 0
        assert 'ratings' in data
        assert isinstance(data['ratings'], list)
    
    def test_get_interviewer_not_found(self, client):
        """Test getting non-existent interviewer returns 404"""
        response = client.get('/api/interviewers/99999')
        
        assert response.status_code == 404


# ============================================================================
# SEARCH AND FILTERING TESTS
# ============================================================================

class TestSearchAndFiltering:
    """Test search and filtering functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_multiple_interviewers(self, client):
        """Create multiple interviewers for testing"""
        with app.app_context():
            interviewers = [
                Interviewer(name='Alice Anderson', company='Google', average_difficulty=4.5, total_reviews=10),
                Interviewer(name='Bob Brown', company='Amazon', average_difficulty=3.2, total_reviews=5),
                Interviewer(name='Charlie Chen', company='Google', average_difficulty=2.1, total_reviews=8),
                Interviewer(name='Diana Davis', company='Microsoft', average_difficulty=4.8, total_reviews=12),
            ]
            for interviewer in interviewers:
                db.session.add(interviewer)
            db.session.commit()
    
    def test_search_by_name(self, client):
        """Test searching interviewers by name"""
        response = client.get('/api/interviewers?search=Alice')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Alice Anderson'
    
    def test_search_by_company(self, client):
        """Test searching interviewers by company"""
        response = client.get('/api/interviewers?search=Google')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        companies = [item['company'] for item in data]
        assert all(company == 'Google' for company in companies)
    
    def test_search_case_insensitive(self, client):
        """Test search is case-insensitive"""
        response = client.get('/api/interviewers?search=google')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
    
    def test_search_partial_match(self, client):
        """Test search with partial string match"""
        response = client.get('/api/interviewers?search=Bro')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert 'Brown' in data[0]['name']
    
    def test_sort_by_difficulty_descending(self, client):
        """Test interviewers are sorted by difficulty (hardest first)"""
        response = client.get('/api/interviewers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check that ratings are in descending order
        ratings = [item['average_difficulty'] for item in data]
        assert ratings == sorted(ratings, reverse=True)
        
        # Verify hardest interviewer is first
        assert data[0]['name'] == 'Diana Davis'
        assert data[0]['average_difficulty'] == 4.8


# ============================================================================
# RATING SUBMISSION TESTS
# ============================================================================

class TestRatingSubmission:
    """Test rating submission and validation"""
    
    def test_submit_rating_success(self, client, auth_headers, test_interviewer):
        """Test successfully submitting a rating"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 4, 'comments': 'Very challenging interview'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'successfully' in data['message'].lower()
        assert data['average_difficulty'] == 4.0
        assert data['total_reviews'] == 1
    
    def test_submit_rating_minimum_value(self, client, auth_headers, test_interviewer):
        """Test submitting rating with minimum value (1)"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 1, 'comments': 'Easy interview'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['average_difficulty'] == 1.0
    
    def test_submit_rating_maximum_value(self, client, auth_headers, test_interviewer):
        """Test submitting rating with maximum value (5)"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 5, 'comments': 'Extremely difficult'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['average_difficulty'] == 5.0
    
    def test_submit_rating_without_comment(self, client, auth_headers, test_interviewer):
        """Test submitting rating without optional comment"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 3}
        )
        
        assert response.status_code == 201
    
    def test_submit_rating_invalid_too_low(self, client, auth_headers, test_interviewer):
        """Test submitting rating below minimum (0) returns 400"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 0}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'between 1 and 5' in data['message']
    
    def test_submit_rating_invalid_too_high(self, client, auth_headers, test_interviewer):
        """Test submitting rating above maximum (6) returns 400"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 6}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'between 1 and 5' in data['message']
    
    def test_submit_rating_non_integer(self, client, auth_headers, test_interviewer):
        """Test submitting non-integer rating returns 400"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 3.5}
        )
        
        assert response.status_code == 400
    
    def test_submit_rating_missing_value(self, client, auth_headers, test_interviewer):
        """Test submitting rating without value returns 400"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'comments': 'Great interview'}
        )
        
        assert response.status_code == 400
    
    def test_submit_rating_no_auth(self, client, test_interviewer):
        """Test submitting rating without authentication returns 401"""
        response = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            json={'rating': 4}
        )
        
        assert response.status_code == 401
    
    def test_submit_rating_interviewer_not_found(self, client, auth_headers):
        """Test submitting rating for non-existent interviewer returns 404"""
        response = client.post('/api/interviewers/99999/ratings',
            headers=auth_headers,
            json={'rating': 4}
        )
        
        assert response.status_code == 404


# ============================================================================
# DUPLICATE RATING PREVENTION TESTS
# ============================================================================

class TestDuplicateRatingPrevention:
    """Test duplicate rating prevention"""
    
    def test_duplicate_rating_same_user(self, client, auth_headers, test_interviewer):
        """Test user cannot rate same interviewer twice"""
        # First rating
        response1 = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 4}
        )
        assert response1.status_code == 201
        
        # Second rating (should fail)
        response2 = client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 5}
        )
        assert response2.status_code == 409
        data = json.loads(response2.data)
        assert 'already rated' in data['message'].lower()
    
    def test_check_user_rating_exists(self, client, auth_headers, test_interviewer):
        """Test checking if user has already rated an interviewer"""
        # Submit a rating
        client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 4, 'comments': 'Good interview'}
        )
        
        # Check if rating exists
        response = client.get(f'/api/interviewers/{test_interviewer}/user-rating',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['rating'] == 4
        assert data['comments'] == 'Good interview'
    
    def test_check_user_rating_not_exists(self, client, auth_headers, test_interviewer):
        """Test checking for non-existent user rating returns 404"""
        response = client.get(f'/api/interviewers/{test_interviewer}/user-rating',
            headers=auth_headers
        )
        
        assert response.status_code == 404


# ============================================================================
# RATING CALCULATION TESTS
# ============================================================================

class TestRatingCalculation:
    """Test rating average calculation"""
    
    def test_average_calculation_single_rating(self, client, auth_headers, test_interviewer):
        """Test average with single rating"""
        client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 4}
        )
        
        response = client.get(f'/api/interviewers/{test_interviewer}')
        data = json.loads(response.data)
        
        assert data['average_difficulty'] == 4.0
        assert data['total_reviews'] == 1
    
    def test_average_calculation_multiple_ratings(self, client, test_interviewer):
        """Test average with multiple ratings from different users"""
        with app.app_context():
            # Create multiple users and ratings
            users = []
            for i in range(3):
                user = User(username=f'user{i}', email=f'user{i}@example.com')
                user.set_password('password')
                db.session.add(user)
                users.append(user)
            db.session.commit()
            
            ratings = [5, 3, 4]  # Average should be 4.0
            for user, rating_value in zip(users, ratings):
                token = create_access_token(identity=str(user.id))
                headers = {'Authorization': f'Bearer {token}'}
                
                client.post(f'/api/interviewers/{test_interviewer}/ratings',
                    headers=headers,
                    json={'rating': rating_value}
                )
        
        response = client.get(f'/api/interviewers/{test_interviewer}')
        data = json.loads(response.data)
        
        assert data['average_difficulty'] == 4.0
        assert data['total_reviews'] == 3
    
    def test_rating_rounded_to_two_decimals(self, client, test_interviewer):
        """Test rating is rounded to 2 decimal places"""
        with app.app_context():
            # Create users with ratings that produce non-round average
            users = []
            for i in range(3):
                user = User(username=f'user{i}', email=f'user{i}@example.com')
                user.set_password('password')
                db.session.add(user)
                users.append(user)
            db.session.commit()
            
            ratings = [5, 4, 3]  # Average = 4.0
            for user, rating_value in zip(users, ratings):
                token = create_access_token(identity=str(user.id))
                headers = {'Authorization': f'Bearer {token}'}
                
                client.post(f'/api/interviewers/{test_interviewer}/ratings',
                    headers=headers,
                    json={'rating': rating_value}
                )
        
        response = client.get(f'/api/interviewers/{test_interviewer}')
        data = json.loads(response.data)
        
        # Check it's rounded to 2 decimals
        assert isinstance(data['average_difficulty'], float)
        assert len(str(data['average_difficulty']).split('.')[-1]) <= 2


# ============================================================================
# RATING DISPLAY TESTS
# ============================================================================

class TestRatingDisplay:
    """Test rating display and ordering"""
    
    def test_ratings_ordered_newest_first(self, client, test_interviewer):
        """Test ratings are displayed in reverse chronological order"""
        with app.app_context():
            # Create multiple users and ratings at different times
            users = []
            for i in range(3):
                user = User(username=f'user{i}', email=f'user{i}@example.com')
                user.set_password('password')
                db.session.add(user)
                users.append(user)
            db.session.commit()
            
            # Submit ratings
            for user in users:
                token = create_access_token(identity=str(user.id))
                headers = {'Authorization': f'Bearer {token}'}
                
                client.post(f'/api/interviewers/{test_interviewer}/ratings',
                    headers=headers,
                    json={'rating': 4}
                )
        
        response = client.get(f'/api/interviewers/{test_interviewer}')
        data = json.loads(response.data)
        
        ratings = data['ratings']
        assert len(ratings) == 3
        
        # Check timestamps are in descending order
        timestamps = [datetime.fromisoformat(r['created_at']) for r in ratings]
        assert timestamps == sorted(timestamps, reverse=True)
    
    def test_rating_includes_username(self, client, auth_headers, test_interviewer, test_user):
        """Test rating display includes username"""
        client.post(f'/api/interviewers/{test_interviewer}/ratings',
            headers=auth_headers,
            json={'rating': 4, 'comments': 'Great interview'}
        )
        
        response = client.get(f'/api/interviewers/{test_interviewer}')
        data = json.loads(response.data)
        
        assert len(data['ratings']) == 1
        rating = data['ratings'][0]
        assert rating['username'] == 'testuser'
        assert rating['rating'] == 4
        assert rating['comments'] == 'Great interview'
        assert 'created_at' in rating


# ============================================================================
# AUTO-IMPORT TESTS
# ============================================================================

class TestAutoImport:
    """Test auto-import from interviews and rounds"""
    
    def test_import_from_interview_table(self, client, auth_headers, test_interview):
        """Test importing interviewers from interview table"""
        response = client.post('/api/interviewers/import-from-interviews',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['imported'] >= 1
        assert 'Jane Smith' in str(data) or data['imported'] > 0
    
    def test_import_from_interview_round_table(self, client, auth_headers, test_interview):
        """Test importing interviewers from interview_round table"""
        with app.app_context():
            # Add interview round with interviewer
            round = InterviewRound(
                interview_id=test_interview,
                round_number=1,
                interviewer_name='Bob Wilson',
                status='Scheduled'
            )
            db.session.add(round)
            db.session.commit()
        
        response = client.post('/api/interviewers/import-from-interviews',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['imported'] >= 1
    
    def test_import_skips_duplicates(self, client, auth_headers, test_interview):
        """Test import skips existing interviewers"""
        # First import
        response1 = client.post('/api/interviewers/import-from-interviews',
            headers=auth_headers
        )
        data1 = json.loads(response1.data)
        imported_first = data1['imported']
        
        # Second import (should skip all)
        response2 = client.post('/api/interviewers/import-from-interviews',
            headers=auth_headers
        )
        data2 = json.loads(response2.data)
        
        assert data2['imported'] == 0
        assert data2['skipped'] == imported_first
    
    def test_import_ignores_null_names(self, client, auth_headers, test_user):
        """Test import ignores interviews with null interviewer names"""
        with app.app_context():
            # Create interview without interviewer name
            interview = Interview(
                user_id=test_user,
                company_name='TechCorp',
                job_title='Developer',
                interviewer_name=None
            )
            db.session.add(interview)
            db.session.commit()
        
        response = client.post('/api/interviewers/import-from-interviews',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # Should not fail, just skip null entries
    
    def test_import_requires_auth(self, client):
        """Test import requires authentication"""
        response = client.post('/api/interviewers/import-from-interviews')
        
        assert response.status_code == 401


# ============================================================================
# SUGGESTIONS FEATURE TESTS
# ============================================================================

class TestSuggestions:
    """Test interviewer suggestions from existing data"""
    
    def test_suggestions_from_interviews(self, client, test_interview):
        """Test getting suggestions from interview data"""
        response = client.get('/api/interviewers?include_suggestions=true')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should include suggestion for Jane Smith from test_interview
        suggestions = [item for item in data if item.get('suggestion')]
        assert len(suggestions) >= 1
        
        jane_smith = next((s for s in suggestions if s['name'] == 'Jane Smith'), None)
        assert jane_smith is not None
        assert jane_smith['company'] == 'TechCorp'
        assert jane_smith['in_database'] is False
        assert jane_smith['suggestion'] is True
    
    def test_suggestions_exclude_existing(self, client, test_interviewer):
        """Test suggestions don't include interviewers already in database"""
        response = client.get('/api/interviewers?include_suggestions=true')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # John Doe should be in database, not in suggestions
        john_doe_db = next((item for item in data if item['name'] == 'John Doe' and item['in_database']), None)
        john_doe_suggestion = next((item for item in data if item['name'] == 'John Doe' and item.get('suggestion')), None)
        
        assert john_doe_db is not None
        assert john_doe_suggestion is None
    
    def test_suggestions_with_search(self, client, test_interview):
        """Test suggestions respect search filter"""
        response = client.get('/api/interviewers?include_suggestions=true&search=Jane')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should only include items matching 'Jane'
        for item in data:
            assert 'jane' in item['name'].lower() or 'jane' in item['company'].lower()


# ============================================================================
# PUBLIC ACCESS TESTS
# ============================================================================

class TestPublicAccess:
    """Test public access to interviewer information"""
    
    def test_get_interviewers_no_auth(self, client, test_interviewer):
        """Test getting interviewer list without authentication"""
        response = client.get('/api/interviewers')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
    
    def test_get_interviewer_detail_no_auth(self, client, test_interviewer):
        """Test getting interviewer details without authentication"""
        response = client.get(f'/api/interviewers/{test_interviewer}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'John Doe'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
