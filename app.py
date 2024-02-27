from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Assuming 'dataset/movies.csv' and 'dataset/ratings.csv' exist and are formatted correctly.


def load_and_preprocess_data():
    # Loading datasets
    ratings = pd.read_csv('dataset/ratings.csv')
    movies = pd.read_csv('dataset/movies.csv')
    # Merging and preprocessing
    merged_data = pd.merge(movies, ratings, on='movieId').drop(
        ['genres', 'timestamp'], axis=1)
    user_ratings = merged_data.pivot_table(
        index='userId', columns='title', values='rating')
    # Drop movies with less than 10 ratings to improve recommendation quality
    user_ratings = user_ratings.dropna(thresh=10, axis=1).fillna(0)
    # Calculate similarity between movies based on user ratings
    similarity_matrix = user_ratings.corr(method='pearson')
    return movies, similarity_matrix


movies_df, similarity_matrix = load_and_preprocess_data()


def get_similar_movies(movie_name, n_recommendations=10):
    # Check if the movie is in the similarity matrix
    if movie_name not in similarity_matrix:
        return [], "Movie not found."
    # Get similarity scores, sort them, and remove the first one (self-comparison)
    scores = similarity_matrix[movie_name].sort_values(ascending=False)[
        1:n_recommendations+1]
    # Get movie titles
    movie_titles = scores.index.tolist()
    return movie_titles, None


@app.route('/')
def home():
    # Ensure the 'index.html' template exists in the 'templates' directory
    return render_template('index.html')


@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    suggestions = movies_df[movies_df['title'].str.contains(
        query, case=False, na=False)]['title'].tolist() if query else []
    return jsonify(suggestions)


@app.route('/recommend', methods=['GET'])
def recommend():
    movie_name = request.args.get('movieName', '')
    recommendations, error = get_similar_movies(movie_name)
    if error:
        return jsonify({"error": error}), 404
    # Return ranked recommendations
    ranked_recommendations = [{"rank": i+1, "title": title}
                              for i, title in enumerate(recommendations)]
    return jsonify(ranked_recommendations)


@app.route('/')
def hello():
    return 'Hello, NextFlix viewers!'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
