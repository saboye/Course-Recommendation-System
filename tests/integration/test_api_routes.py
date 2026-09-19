"""
Integration tests for Course Recommendation System Flask API endpoints.
Tests routes, query handling, validation, status codes, and JSON responses.
"""

import pytest
from app import app


@pytest.fixture
def client():
    """Create a Flask test client instance."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestApiRoutes:
    """Test suite for Flask endpoints."""

    def test_home_page_status_and_content(self, client):
        """Test GET / returns 200 and loads homepage template."""
        response = client.get('/')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "Course Recommendation System" in html
        assert "keyword" in html
        assert "course-title" in html

    def test_health_endpoint(self, client):
        """Test GET /api/health returns healthy status and metadata."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "total_courses" in data
        assert data["total_courses"] > 0
        assert data["has_models"] is True

    def test_courses_search_success(self, client):
        """Test GET /courses?keyword=python returns matching courses."""
        response = client.get('/courses?keyword=python')
        assert response.status_code == 200
        data = response.get_json()
        assert "courses" in data
        assert "count" in data
        assert data["count"] > 0
        assert len(data["courses"]) == data["count"]
        # Ensure results contain Python
        assert any("Python" in title for title in data["courses"])

    def test_courses_search_missing_keyword(self, client):
        """Test GET /courses without keyword returns 400 error."""
        response = client.get('/courses')
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Keyword is required"

    def test_courses_search_empty_keyword(self, client):
        """Test GET /courses with whitespace keyword returns 400 error."""
        response = client.get('/courses?keyword=   ')
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Keyword is required"

    def test_courses_search_no_matches(self, client):
        """Test GET /courses with non-matching string returns empty list."""
        response = client.get('/courses?keyword=xyz_non_existent_course_string_999')
        assert response.status_code == 200
        data = response.get_json()
        assert data["courses"] == []
        assert data["count"] == 0

    def test_recommend_success(self, client):
        """Test GET /recommend with valid course returns 5 recommendations with full schema."""
        # Find a real course title first
        courses_res = client.get('/courses?keyword=python')
        course_title = courses_res.get_json()["courses"][0]

        response = client.get(f'/recommend?course_title={course_title}')
        assert response.status_code == 200
        data = response.get_json()

        assert "recommendations" in data
        assert "selected_course" in data
        assert "count" in data
        assert data["count"] == 5
        assert len(data["recommendations"]) == 5

        # Check schema of first recommendation
        first_rec = data["recommendations"][0]
        required_keys = ['Course Name', 'University', 'Difficulty Level', 'Course Rating', 'Course URL', 'Course Description']
        for key in required_keys:
            assert key in first_rec, f"Missing {key} in recommendation"
            assert first_rec[key] is not None

        # Check university and difficulty are human-readable strings
        assert isinstance(first_rec['University'], str)
        assert len(first_rec['University']) > 0
        assert isinstance(first_rec['Difficulty Level'], str)
        assert isinstance(first_rec['Course Rating'], (int, float))

    def test_recommend_custom_count(self, client):
        """Test GET /recommend with custom count n parameter."""
        courses_res = client.get('/courses?keyword=python')
        course_title = courses_res.get_json()["courses"][0]

        response = client.get(f'/recommend?course_title={course_title}&n=3')
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 3
        assert len(data["recommendations"]) == 3

    def test_recommend_missing_title(self, client):
        """Test GET /recommend without course_title returns 400 error."""
        response = client.get('/recommend')
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Course title is required"

    def test_recommend_nonexistent_title(self, client):
        """Test GET /recommend with invalid course title returns 400 error."""
        response = client.get('/recommend?course_title=NonExistentCourseName12345')
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "No matching courses found"

    def test_not_found_route(self, client):
        """Test requesting nonexistent route returns 404."""
        response = client.get('/nonexistent-path-for-testing')
        assert response.status_code == 404
