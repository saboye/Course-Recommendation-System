import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask, request, jsonify, render_template

# Load the dataset
file_path = 'cleaned_dataset.csv'  # Ensure this path is correct
df = pd.read_csv(file_path)

# Initialize the Flask application
app = Flask(__name__)

# Define a TF-IDF Vectorizer Object. Remove all english stop words such as 'the', 'a'
tfidf = TfidfVectorizer(stop_words='english')

# Replace NaN in the course description with an empty string
df['Course Description'] = df['Course Description'].fillna('')

# Construct the TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(df['Course Description'])

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Function that takes in a keyword as input and outputs the top 5 recommended courses
def get_recommendations_by_keyword(keyword, cosine_sim=cosine_sim, n_recommendations=5):
    # Find courses that match the keyword in their description
    matches = df[df['Course Description'].str.contains(keyword, case=False, na=False)]
    
    if matches.empty:
        return []
    
    # Get the indices of the matched courses
    matched_indices = matches.index.tolist()
    
    # Calculate similarity scores for the matched courses
    sim_scores = []
    for idx in matched_indices:
        scores = list(enumerate(cosine_sim[idx]))
        sim_scores.extend(scores)
    
    # Sort the courses based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Remove duplicate courses and keep the top n recommendations
    seen = set()
    top_recommendations = []
    for i in sim_scores:
        if i[0] not in seen:
            top_recommendations.append(i)
            seen.add(i[0])
        if len(top_recommendations) == n_recommendations:
            break
    
    # Get the course details for the recommended courses
    recommended_courses = []
    for i in top_recommendations:
        course_details = {
            "title": df['Course Name'].iloc[i[0]],
            "url": df['Course URL'].iloc[i[0]],
            "description": df['Course Description'].iloc[i[0]],
            "university": df['University'].iloc[i[0]],
            "rating": df['Course Rating'].iloc[i[0]],
            "skills": df['Skills'].iloc[i[0]]
        }
        recommended_courses.append(course_details)
    
    return recommended_courses

# Define the home route
@app.route('/')
def home():
    return render_template('index.html')

# Define the route for recommendations
@app.route('/recommend', methods=['GET'])
def recommend():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400
    
    recommendations = get_recommendations_by_keyword(keyword)
    return jsonify({"recommendations": recommendations})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
