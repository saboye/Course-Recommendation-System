import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from surprise import Dataset, Reader, SVD, KNNBasic
from surprise.model_selection import train_test_split
import numpy as np
import pickle

# Load the cleaned dataset
df = pd.read_csv('data/cleaned_dataset.csv')

# Ensure 'Course Rating' is numeric
df['Course Rating'] = pd.to_numeric(df['Course Rating'], errors='coerce')

# Add a 'Popularity' feature based on the Course Rating
df['Popularity'] = df['Course Rating'] * df['Course Rating'].count() / df['Course Rating'].sum()

# Encode categorical variables
label_encoder = LabelEncoder()
df['University'] = label_encoder.fit_transform(df['University'])
df['Difficulty Level'] = label_encoder.fit_transform(df['Difficulty Level'])

# Create mock user IDs and item IDs
df['user_id'] = np.random.randint(1, 101, df.shape[0])  # Assuming 100 unique users
df['item_id'] = df.index  # Using index as a unique item ID

# Extract important features from the 'Course Description' with adjusted parameters
tfidf = TfidfVectorizer(stop_words='english', max_df=0.8, min_df=5, ngram_range=(1, 2))
df['Course Description'] = df['Course Description'].fillna('')
tfidf_matrix = tfidf.fit_transform(df['Course Description'])

# Combine the original features with the TF-IDF features
df_tfidf = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names_out())
df_combined = pd.concat([df, df_tfidf], axis=1)

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Prepare the data for collaborative filtering
cf_df = df[['user_id', 'item_id', 'Course Rating']].dropna()
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(cf_df[['user_id', 'item_id', 'Course Rating']], reader)
trainset, testset = train_test_split(data, test_size=0.2)

# Train the collaborative filtering models
algo_svd = SVD()
algo_knn = KNNBasic()
algo_svd.fit(trainset)
algo_knn.fit(trainset)

# Save the models and necessary data using pickle
with open('models/svd_model.pkl', 'wb') as f:
    pickle.dump(algo_svd, f)
with open('models/knn_model.pkl', 'wb') as f:
    pickle.dump(algo_knn, f)
with open('models/cosine_sim.pkl', 'wb') as f:
    pickle.dump(cosine_sim, f)
with open('models/tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf, f)
with open('models/df.pkl', 'wb') as f:
    pickle.dump(df, f)
with open('models/university_label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
