"""
Simple example test to verify test setup is working correctly.

Run this first to ensure pytest and dependencies are properly installed:
    pytest test_simple_example.py -v
"""

import pytest
from app import app
from models import db, Interviewer


def test_pytest_working():
    """Verify pytest is installed and working"""
    assert True


def test_flask_app_exists():
    """Verify Flask app can be imported"""
    assert app is not None
    assert app.name == 'app'


def test_database_models_exist():
    """Verify database models can be imported"""
    assert Interviewer is not None
    assert hasattr(Interviewer, 'name')
    assert hasattr(Interviewer, 'company')
    assert hasattr(Interviewer, 'average_difficulty')


def test_in_memory_database():
    """Verify in-memory database works"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Create a test interviewer
        interviewer = Interviewer(name='Test Person', company='Test Corp')
        db.session.add(interviewer)
        db.session.commit()
        
        # Query it back
        result = Interviewer.query.filter_by(name='Test Person').first()
        assert result is not None
        assert result.company == 'Test Corp'
        
        # Cleanup
        db.session.remove()
        db.drop_all()


def test_basic_math():
    """Verify basic assertions work"""
    assert 1 + 1 == 2
    assert 'hello'.upper() == 'HELLO'
    assert [1, 2, 3] == [1, 2, 3]


if __name__ == '__main__':
    print("Running simple example tests...")
    print("=" * 50)
    pytest.main([__file__, '-v'])
