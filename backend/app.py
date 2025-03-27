import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Use your own Spoonacular API Key
SPOONACULAR_API_KEY = "9517c8b9fb964ce280a752a97f9e26c8"

@app.route('/')
def home():
    return jsonify({"message": "Recipe Matcher Backend is Running"})

@app.route('/search-recipes', methods=['GET'])
def search_recipes():
    ingredients = request.args.get('ingredients')  # Get ingredients from URL
    if not ingredients:
        return jsonify({"error": "Please provide ingredients"}), 400

    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey={SPOONACULAR_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        return jsonify(response.json())  # Return API response
    else:
        return jsonify({"error": "Failed to fetch recipes"}), 500

if __name__ == '__main__':
    app.run(debug=True)