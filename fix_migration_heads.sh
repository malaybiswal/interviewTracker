#!/bin/bash
# Fix multiple migration heads by merging them

echo "=== Fixing Migration Heads ==="
echo "This will merge the multiple head revisions"

# Run inside Docker container
docker-compose run --rm interview-tracker flask db merge heads -m "Merge migration heads"

echo "=== Now you can run: docker-compose up --build ==="
