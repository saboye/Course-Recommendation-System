# Course Recommendation System

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
