from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

SPOONACULAR_API_KEY = "9517c8b9fb964ce280a752a97f9e26c8"

@app.route("/search", methods=["GET"])
def search_recipes():
    ingredients = request.args.get("ingredients")  # Get ingredients from frontend
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ingredients,
        "number": 5  # Limit results
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch recipes"}), response.status_code

if __name__ == "__main__":
    app.run(debug=True)