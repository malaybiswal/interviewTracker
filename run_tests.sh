#!/bin/bash

# Script to run Interview Tracker tests

echo "🧪 Running Interview Tracker Test Suite"
echo "========================================"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run tests with different options based on argument
case "$1" in
    "verbose"|"-v")
        echo "Running tests in verbose mode..."
        pytest test_interviewer_rating.py -v
        ;;
    "coverage"|"-c")
        echo "Running tests with coverage report..."
        pytest test_interviewer_rating.py --cov=routes --cov=models --cov-report=html --cov-report=term
        echo ""
        echo "📊 Coverage report generated in htmlcov/index.html"
        ;;
    "quick"|"-q")
        echo "Running tests in quiet mode..."
        pytest test_interviewer_rating.py -q
        ;;
    "class")
        if [ -z "$2" ]; then
            echo "❌ Please specify a test class name"
            echo "Example: ./run_tests.sh class TestInterviewerManagement"
            exit 1
        fi
        echo "Running test class: $2"
        pytest test_interviewer_rating.py::$2 -v
        ;;
    "test")
        if [ -z "$2" ]; then
            echo "❌ Please specify a test name"
            echo "Example: ./run_tests.sh test test_add_interviewer_success"
            exit 1
        fi
        echo "Running tests matching: $2"
        pytest test_interviewer_rating.py -k "$2" -v
        ;;
    "help"|"-h"|"--help")
        echo "Usage: ./run_tests.sh [option]"
        echo ""
        echo "Options:"
        echo "  (none)           Run all tests with standard output"
        echo "  verbose, -v      Run with verbose output"
        echo "  coverage, -c     Run with coverage report"
        echo "  quick, -q        Run in quiet mode"
        echo "  class <name>     Run specific test class"
        echo "  test <pattern>   Run tests matching pattern"
        echo "  help, -h         Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh"
        echo "  ./run_tests.sh verbose"
        echo "  ./run_tests.sh coverage"
        echo "  ./run_tests.sh class TestRatingSubmission"
        echo "  ./run_tests.sh test rating"
        ;;
    *)
        echo "Running all tests..."
        pytest test_interviewer_rating.py
        ;;
esac

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Exit code: $exit_code"
fi

exit $exit_code
