"""
Author: Samuel Aboye
Date: 2024-08-10
Last Modified: 2026-09-18
Description: A modernized Flask web application for a Course Recommendation System,
providing content-based course recommendations with diversity filtering,
restful APIs, and health monitoring.
"""

import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, render_template

# Define base directory for reliable relative path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to models and dataset
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Load the models and data
def load_data_and_models():
    """Load serialized model files and enrich with dataset metadata."""
    with open(os.path.join(MODELS_DIR, 'cosine_sim.pkl'), 'rb') as f:
        cosine_sim = pickle.load(f)

    with open(os.path.join(MODELS_DIR, 'df.pkl'), 'rb') as f:
        df = pickle.load(f)

    # Attempt to load encoders/models if present
    svd_model_path = os.path.join(MODELS_DIR, 'svd_model.pkl')
    algo_svd = pickle.load(open(svd_model_path, 'rb')) if os.path.exists(svd_model_path) else None

    knn_model_path = os.path.join(MODELS_DIR, 'knn_model.pkl')
    algo_knn = pickle.load(open(knn_model_path, 'rb')) if os.path.exists(knn_model_path) else None

    tfidf_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
    tfidf = pickle.load(open(tfidf_path, 'rb')) if os.path.exists(tfidf_path) else None

    encoder_path = os.path.join(MODELS_DIR, 'university_label_encoder.pkl')
    university_label_encoder = pickle.load(open(encoder_path, 'rb')) if os.path.exists(encoder_path) else None

    # Enrich df with raw readable text from cleaned_dataset.csv if available
    csv_path = os.path.join(DATA_DIR, 'cleaned_dataset.csv')
    if os.path.exists(csv_path):
        try:
            df_raw = pd.read_csv(csv_path)
            if len(df_raw) == len(df):
                if 'University' in df_raw.columns:
                    df['University'] = df_raw['University'].astype(str).str.title()
                if 'Difficulty Level' in df_raw.columns:
                    df['Difficulty Level'] = df_raw['Difficulty Level'].astype(str).str.title()
                if 'Skills' in df_raw.columns:
                    df['Skills'] = df_raw['Skills'].fillna('')
                if 'Course URL' in df_raw.columns:
                    df['Course URL'] = df_raw['Course URL'].fillna('')
                if 'Course Description' in df_raw.columns:
                    df['Course Description'] = df_raw['Course Description'].fillna('')
        except Exception as err:
            print(f"Warning: Could not enrich from CSV: {err}")

    return {
        'cosine_sim': cosine_sim,
        'df': df,
        'algo_svd': algo_svd,
        'algo_knn': algo_knn,
        'tfidf': tfidf,
        'university_label_encoder': university_label_encoder
    }

# Initialize data and models
_assets = load_data_and_models()
cosine_sim = _assets['cosine_sim']
df = _assets['df']
algo_svd = _assets['algo_svd']
algo_knn = _assets['algo_knn']
tfidf = _assets['tfidf']
university_label_encoder = _assets['university_label_encoder']

# Initialize Flask application
app = Flask(__name__)


def get_content_based_recommendations(course_index, cosine_sim=cosine_sim, df=df, num_recommendations=5):
    """
    Generate content-based recommendations given a course index, incorporating diversity.

    :param course_index: Index of the query course in the dataset.
    :param cosine_sim: Precomputed pairwise cosine similarity matrix.
    :param df: DataFrame containing course catalog information.
    :param num_recommendations: Number of recommendations to return (default: 5).
    :return: DataFrame containing recommended courses.
    """
    if course_index < 0 or course_index >= len(df):
        empty_cols = ['Course Name', 'University', 'Difficulty Level', 'Course Rating', 'Course URL', 'Course Description']
        if 'Skills' in df.columns:
            empty_cols.append('Skills')
        return pd.DataFrame(columns=empty_cols)

    # Compute similarity ranking
    sim_scores = list(enumerate(cosine_sim[course_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Exclude the course itself
    sim_scores = [x for x in sim_scores if x[0] != course_index]

    # Select candidates pool for diversity
    candidates = sim_scores[:num_recommendations * 3]
    selected_courses = []
    universities = set()
    difficulty_levels = set()

    for idx, _ in candidates:
        if len(selected_courses) >= num_recommendations:
            break
        course = df.iloc[idx]
        univ = course.get('University', '')
        diff = course.get('Difficulty Level', '')

        selected_courses.append(idx)
        universities.add(univ)
        difficulty_levels.add(diff)

    # Fallback if fewer selected than requested
    if len(selected_courses) < num_recommendations and len(sim_scores) > len(selected_courses):
        for idx, _ in sim_scores[len(selected_courses):]:
            if len(selected_courses) >= num_recommendations:
                break
            if idx not in selected_courses:
                selected_courses.append(idx)

    cols = ['Course Name', 'University', 'Difficulty Level', 'Course Rating', 'Course URL', 'Course Description']
    if 'Skills' in df.columns:
        cols.append('Skills')

    recommendations = df.iloc[selected_courses][cols].copy()

    # Format Course Name as Title Case
    recommendations['Course Name'] = recommendations['Course Name'].astype(str).str.title()

    # Ensure University is string and formatted nicely
    if recommendations['University'].dtype != object or recommendations['University'].isna().any():
        recommendations['University'] = recommendations['University'].fillna('Unknown University').astype(str)
    recommendations['University'] = recommendations['University'].astype(str).str.title()

    # Ensure Difficulty Level is title cased
    recommendations['Difficulty Level'] = recommendations['Difficulty Level'].astype(str).str.title()

    # Ensure Course Rating is numeric float or formatted
    recommendations['Course Rating'] = pd.to_numeric(recommendations['Course Rating'], errors='coerce').fillna(0.0)

    return recommendations


@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint providing status and dataset metrics."""
    return jsonify({
        "status": "healthy",
        "total_courses": len(df),
        "has_models": cosine_sim is not None
    }), 200


@app.route('/recommend', methods=['GET'])
def recommend():
    """
    Provide course recommendations based on course title.
    Query parameters:
      - course_title: Name of the course (required)
      - n: Number of recommendations (optional, default: 5, max: 20)
    """
    course_title = request.args.get('course_title', '').strip()
    if not course_title:
        return jsonify({"error": "Course title is required"}), 400

    # Parse count parameter
    try:
        num_recommendations = int(request.args.get('n', 5))
        num_recommendations = max(1, min(20, num_recommendations))
    except (ValueError, TypeError):
        num_recommendations = 5

    # Case-insensitive search for course
    matching_courses = df[df['Course Name'].astype(str).str.strip().str.title() == course_title.title()]
    if matching_courses.empty:
        matching_courses = df[df['Course Name'].astype(str).str.strip().str.lower() == course_title.lower()]

    if matching_courses.empty:
        return jsonify({"error": "No matching courses found"}), 400

    course_index = matching_courses.index[0]
    recommendations = get_content_based_recommendations(
        course_index,
        cosine_sim=cosine_sim,
        df=df,
        num_recommendations=num_recommendations
    )

    response = recommendations.to_dict(orient='records')
    selected_course_info = {
        "Course Name": str(df.iloc[course_index]['Course Name']).title(),
        "University": str(df.iloc[course_index].get('University', '')).title(),
        "Difficulty Level": str(df.iloc[course_index].get('Difficulty Level', '')).title(),
        "Course Rating": float(pd.to_numeric(df.iloc[course_index].get('Course Rating', 0.0), errors='coerce') or 0.0)
    }

    return jsonify({
        "query": course_title,
        "selected_course": selected_course_info,
        "count": len(response),
        "recommendations": response
    }), 200


@app.route('/courses', methods=['GET'])
def get_courses():
    """
    Fetch matching course titles based on a search keyword.
    Query parameters:
      - keyword: Keyword substring to match (required)
    """
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    matching_courses = df[df['Course Name'].astype(str).str.contains(keyword, case=False, na=False)]
    course_titles = matching_courses['Course Name'].astype(str).str.title().drop_duplicates().tolist()

    return jsonify({
        "courses": course_titles,
        "count": len(course_titles)
    }), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
