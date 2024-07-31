<div align="center">
  <h1>Course Recommendation System</h1>
</div>

<p align="center">
    <img src="https://img.shields.io/github/contributors/saboye/Course-Recommendation-System?color=blue&logo=github&style=for-the-badge" alt="GitHub contributors" />
    <img src="https://img.shields.io/github/forks/saboye/Course-Recommendation-System?logo=github&style=for-the-badge" alt="GitHub forks" />
    <img src="https://img.shields.io/github/issues-raw/saboye/Course-Recommendation-System?style=for-the-badge" alt="GitHub issues" />
    <img src="https://img.shields.io/github/license/saboye/Course-Recommendation-System?style=for-the-badge" alt="GitHub license" />
    <img src="https://img.shields.io/github/last-commit/saboye/Course-Recommendation-System?style=for-the-badge" alt="GitHub last commit" />
    <img src="https://img.shields.io/badge/flask-2.1.2-blue?style=for-the-badge&logo=flask" alt="Flask" />
    <img src="https://img.shields.io/badge/scikit--learn-0.24.2-blue?style=for-the-badge&logo=scikit-learn" alt="scikit-learn" />
    <img src="https://img.shields.io/badge/pandas-1.3.5-blue?style=for-the-badge&logo=pandas" alt="Pandas" />
    <img src="https://img.shields.io/badge/numpy-1.20.3-blue?style=for-the-badge&logo=numpy" alt="NumPy" />

</p>



This Python Flask application is designed to provide personalized course recommendations based on course descriptions. The application leverages a content-based filtering approach using TF-IDF Vectorization and Cosine Similarity to identify and recommend courses similar to a keyword entered by the user.

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.x
- pip (Python package installer)

## Project Structure

![image](https://github.com/user-attachments/assets/9586a2e3-8036-4a94-b183-8f401a254fab)

## Setup Instructions

1. **Clone the repository or download the project files**.
    ```bash
    git clone https://github.com/saboye/Course-Recommendation-System.git
    cd Course-Recommendation-System
    ```

2. **Create and activate a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Windows
    # source venv/bin/activate  # On macOS/Linux
    ```

3. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Ensure the dataset (`cleaned_dataset.csv`) is in the project directory**.

## Running the Application

1. **Run the Flask application**:
    ```bash
    python app.py
    ```

2. **Access the application**:
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Application Usage

- **Homepage**: The homepage will display an input field where you can enter a keyword related to the course you are looking for.
- **Recommendations**: After entering a keyword and submitting the form, the application will display a list of recommended courses that match the keyword.

## Example

1. **Start the Flask server**:
    ```bash
    python app.py
    ```

2. **Open your web browser** and navigate to `http://127.0.0.1:5000/`.

3. **Enter a keyword** (e.g., "Python") in the input field and click the "Get Recommendations" button.

4. **View the recommended courses**: The application will display a list of courses that match the entered keyword, including details such as course title, URL, description, university, rating, and skills.

## Additional Information

- **TF-IDF Vectorization**: This technique is used to convert course descriptions into numerical vectors, highlighting the importance of words in each description.
- **Cosine Similarity**: This metric measures the similarity between course descriptions to provide relevant recommendations.
- **Flask Framework**: The application is built using Flask, a lightweight web framework for Python.
