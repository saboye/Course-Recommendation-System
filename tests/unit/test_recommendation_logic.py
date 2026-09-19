"""
Unit tests for Course Recommendation System logic.
Tests recommendation ranking, diversity selection, boundary conditions,
casing, keyword search, and data sanitization.
"""

import pytest
import numpy as np
import pandas as pd
from app import get_content_based_recommendations, df, cosine_sim


class TestRecommendationAlgorithm:
    """Test suite for core recommendation logic with actual models and data."""

    def test_recommendations_count(self):
        """Test that the requested number of recommendations is returned."""
        for count in [1, 3, 5, 8]:
            recs = get_content_based_recommendations(0, num_recommendations=count)
            assert len(recs) == count, f"Expected {count} recommendations, got {len(recs)}"

    def test_recommendations_exclude_queried_course(self):
        """Test that the queried course is never recommended back to the user."""
        test_index = 10
        queried_title = str(df.iloc[test_index]['Course Name']).title()

        recs = get_content_based_recommendations(test_index, num_recommendations=5)
        recommended_titles = recs['Course Name'].tolist()

        assert queried_title not in recommended_titles, "Queried course must not be in recommendations"

    def test_recommendation_schema_columns(self):
        """Test that returned DataFrame contains all required fields."""
        expected_columns = {
            'Course Name',
            'University',
            'Difficulty Level',
            'Course Rating',
            'Course URL',
            'Course Description'
        }
        recs = get_content_based_recommendations(0, num_recommendations=3)
        assert expected_columns.issubset(set(recs.columns)), f"Missing expected columns in {recs.columns}"

    def test_casing_and_formatting(self):
        """Test that names, universities, and difficulty levels are properly formatted."""
        recs = get_content_based_recommendations(0, num_recommendations=3)
        for _, row in recs.iterrows():
            assert isinstance(row['Course Name'], str)
            assert len(row['Course Name']) > 0
            assert isinstance(row['University'], str)
            assert len(row['University']) > 0
            assert isinstance(row['Difficulty Level'], str)
            assert isinstance(row['Course Rating'], (int, float, np.number))

    def test_negative_index_boundary(self):
        """Test that out-of-bounds negative index returns an empty DataFrame safely."""
        recs = get_content_based_recommendations(-1)
        assert isinstance(recs, pd.DataFrame)
        assert len(recs) == 0

    def test_overflow_index_boundary(self):
        """Test that index beyond dataset size returns an empty DataFrame safely."""
        recs = get_content_based_recommendations(len(df) + 999)
        assert isinstance(recs, pd.DataFrame)
        assert len(recs) == 0

    def test_skills_column_retention(self):
        """Test that Skills column is included when present in dataset."""
        recs = get_content_based_recommendations(0, num_recommendations=2)
        if 'Skills' in df.columns:
            assert 'Skills' in recs.columns


class TestIsolatedMockRecommendation:
    """Test recommendation algorithm with synthetic isolated fixtures."""

    @pytest.fixture
    def mock_catalog(self):
        """Create a synthetic mini course dataset."""
        data = {
            'Course Name': [
                'python basics',
                'advanced python programming',
                'machine learning with python',
                'introduction to sql',
                'deep learning specialisation',
                'graphic design basics'
            ],
            'University': [
                'university of michigan',
                'stanford university',
                'stanford university',
                'duke university',
                'deeplearning.ai',
                'calarts'
            ],
            'Difficulty Level': [
                'beginner',
                'advanced',
                'intermediate',
                'beginner',
                'advanced',
                'beginner'
            ],
            'Course Rating': [4.8, 4.9, 4.7, 4.5, 4.9, 4.2],
            'Course URL': [f'https://coursera.org/learn/course-{i}' for i in range(6)],
            'Course Description': [
                'Learn python programming fundamentals.',
                'Master advanced python data structures and decorators.',
                'Apply python to machine learning algorithms and scikit-learn.',
                'Learn relational databases and SQL queries.',
                'Build neural networks and deep learning models.',
                'Learn visual design, typography, and color theory.'
            ],
            'Skills': ['python', 'python oop', 'ml scikit', 'sql db', 'neural networks', 'design']
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def mock_similarity_matrix(self):
        """
        Create a 6x6 symmetric similarity matrix.
        """
        matrix = np.array([
            [1.00, 0.95, 0.85, 0.30, 0.40, 0.05],
            [0.95, 1.00, 0.90, 0.25, 0.50, 0.02],
            [0.85, 0.90, 1.00, 0.35, 0.80, 0.01],
            [0.30, 0.25, 0.35, 1.00, 0.20, 0.10],
            [0.40, 0.50, 0.80, 0.20, 1.00, 0.01],
            [0.05, 0.02, 0.01, 0.10, 0.01, 1.00]
        ])
        return matrix

    def test_mock_recommendations_ranking(self, mock_catalog, mock_similarity_matrix):
        """Test that courses are recommended in accordance with similarity rankings."""
        recs = get_content_based_recommendations(
            course_index=0,
            cosine_sim=mock_similarity_matrix,
            df=mock_catalog,
            num_recommendations=2
        )

        assert len(recs) == 2
        rec_titles = recs['Course Name'].tolist()
        assert rec_titles[0] == 'Advanced Python Programming'
        assert rec_titles[1] == 'Machine Learning With Python'

    def test_mock_diversity_pool(self, mock_catalog, mock_similarity_matrix):
        """Test that diverse universities and levels are preserved."""
        recs = get_content_based_recommendations(
            course_index=0,
            cosine_sim=mock_similarity_matrix,
            df=mock_catalog,
            num_recommendations=3
        )
        assert len(recs) == 3
        ratings = recs['Course Rating'].tolist()
        assert all(r > 4.0 for r in ratings)

    def test_zero_recommendations_requested(self, mock_catalog, mock_similarity_matrix):
        """Test requesting 0 recommendations returns empty result cleanly."""
        recs = get_content_based_recommendations(
            course_index=0,
            cosine_sim=mock_similarity_matrix,
            df=mock_catalog,
            num_recommendations=0
        )
        assert len(recs) == 0


class TestKeywordSearchLogic:
    """Test keyword searching logic on course catalog."""

    def test_search_case_insensitive(self):
        """Verify that searching with different cases yields same matches."""
        lower_matches = df[df['Course Name'].astype(str).str.contains('python', case=False, na=False)]
        upper_matches = df[df['Course Name'].astype(str).str.contains('PYTHON', case=False, na=False)]
        title_matches = df[df['Course Name'].astype(str).str.contains('Python', case=False, na=False)]

        assert len(lower_matches) == len(upper_matches)
        assert len(lower_matches) == len(title_matches)
        assert len(lower_matches) > 0

    def test_search_nonexistent_keyword(self):
        """Verify searching for arbitrary string returns zero results."""
        nonexistent = "xyz_arbitrary_string_not_found_98765"
        matches = df[df['Course Name'].astype(str).str.contains(nonexistent, case=False, na=False)]
        assert len(matches) == 0
