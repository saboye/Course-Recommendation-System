from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import linear_kernel

# Load the models and data
with open('models/svd_model.pkl', 'rb') as f:
    algo_svd = pickle.load(f)
with open('models/knn_model.pkl', 'rb') as f:
    algo_knn = pickle.load(f)
with open('models/cosine_sim.pkl', 'rb') as f:
    cosine_sim = pickle.load(f)
with open('models/tfidf_vectorizer.pkl', 'rb') as f:
    tfidf = pickle.load(f)
with open('models/df.pkl', 'rb') as f:
    df = pickle.load(f)
with open('models/university_label_encoder.pkl', 'rb') as f:
    university_label_encoder = pickle.load(f)

# Initialize the Flask application
app = Flask(__name__)

# Function to get content-based recommendations based on course index with diversity
def get_content_based_recommendations(course_index, cosine_sim=cosine_sim, df=df, num_recommendations=5):
    sim_scores = list(enumerate(cosine_sim[course_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations * 3 + 1]
    course_indices = [i[0] for i in sim_scores]
    selected_courses = []
    universities = set()
    difficulty_levels = set()
    for idx in course_indices:
        course = df.iloc[idx]
        if len(selected_courses) >= num_recommendations:
            break
        selected_courses.append(idx)
        universities.add(course['University'])
        difficulty_levels.add(course['Difficulty Level'])
    recommendations = df.iloc[selected_courses][['Course Name', 'University', 'Difficulty Level', 'Course Rating', 'Course URL', 'Course Description']]
    
    # Handle unseen labels in the university column
    try:
        recommendations['University'] = university_label_encoder.inverse_transform(recommendations['University'])
    except ValueError as e:
        # Replace unseen labels with 'Unknown University'
        unseen_labels = [label for label in recommendations['University'] if label not in university_label_encoder.classes_]
        if unseen_labels:
            recommendations['University'] = recommendations['University'].apply(
                lambda x: 'Unknown University' if x in unseen_labels else university_label_encoder.inverse_transform([x])[0]
            )
    
    # Convert course names to title case
    recommendations['Course Name'] = recommendations['Course Name'].apply(lambda x: x.title())
    
    return recommendations

# Define the home route
@app.route('/')
def home():
    return render_template('index.html')

# Define the route for recommendations
@app.route('/recommend', methods=['GET'])
def recommend():
    course_title = request.args.get('course_title')

    if not course_title:
        return jsonify({"error": "Course title is required"}), 400
    
    matching_courses = df[df['Course Name'].str.title() == course_title.title()]
    if matching_courses.empty:
        return jsonify({"error": "No matching courses found"}), 400
    
    course_index = matching_courses.index[0]
    recommendations = get_content_based_recommendations(course_index, num_recommendations=5)
    
    response = recommendations.to_dict(orient='records')
    return jsonify({"recommendations": response})

# Define the route for fetching matching courses based on keyword
@app.route('/courses', methods=['GET'])
def get_courses():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400
    
    matching_courses = df[df['Course Name'].str.contains(keyword, case=False, na=False)]
    course_titles = matching_courses['Course Name'].str.title().unique().tolist()
    return jsonify({"courses": course_titles})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
