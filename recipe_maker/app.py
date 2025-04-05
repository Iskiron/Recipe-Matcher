from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests
import os
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Configurations
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "database.db")}'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)  # Explicitly initialize login manager
login_manager.login_view = "login_page"

# Spoonacular API Key
SPOONACULAR_API_KEY = "KEY"

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/signup", methods=["POST"])
def signup():
    print("Form data received:", request.form)
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    terms_agreed = request.form.get("terms")  

    # Validate required fields
    if not all([username, email, password]):
        flash("All fields are required!", "danger")
        return redirect(url_for("signup_page"))

    # Check password length
    if len(password) < 8:
        flash("Password must be at least 8 characters", "danger")
        return redirect(url_for("signup_page"))

    # Check terms agreement
    if not terms_agreed:  # Add this block
        flash("You must agree to the terms and conditions", "danger")
        return redirect(url_for("signup_page"))

    # Check existing user
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        flash("Username or email already exists. Please log in.", "warning")
        return redirect(url_for("login_page"))

    # Create user
    try:
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login_page"))  # Redirect to login page
    except Exception as e:
        db.session.rollback()
        flash("Error creating account. Please try again.", "danger")
        return redirect(url_for("signup_page"))

# Login Route
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for("index"))
    else:
        flash("Invalid email or password", "danger")
        return redirect(url_for("login_page"))

@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return f"Welcome, {current_user.username}! <a href='/logout'>Logout</a>"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login_page"))

# Signup Page
@app.route("/signup-page")
def signup_page():
    return render_template("signup.html")

@app.route("/login-page")
def login_page():
    return render_template("login.html") 

@app.route('/')
def home():
    return render_template('landingpage.html')  # Your main page template

@app.route('/dietary')
def dietary():
    return render_template('dietary.html')  # your dietary template name

@app.route('/about')
def about():
    return render_template('about.html')  # your about template name

@app.route('/community')
def community():
    return render_template('community.html')  # your community template name

# Valid dietary filters 
VALID_DIETS = {
    'Vegetarian', 'Vegan', 'Gluten Free', 'Ketogenic', 'Lacto-Vegetarian',
    'Ovo-Vegetarian', 'Pescetarian', 'Paleo', 'Primal', 'Low FODMAP',
    'Whole30', 'Dairy Free', 'Nut Free'
}

# Recipe Search Route
@app.route("/search", methods=["GET"])
def search_recipes():
    ingredients = request.args.get("ingredients", "")
    diet = request.args.get("diet", "").strip()  # Get single diet

    # Validate diet against correct Spoonacular options
    VALID_DIETS = {
        'Vegetarian', 'Vegan', 'Gluten Free', 'Ketogenic', 'Lacto-Vegetarian',
        'Ovo-Vegetarian', 'Pescetarian', 'Paleo', 'Primal', 'Low FODMAP',
        'Whole30', 'Dairy Free', 'Nut Free'
    }

    # validate diet parameter
    diet = diet if diet in VALID_DIETS else None
    offset = request.args.get("offset", default=0, type=int)
    params = {
        "random": str(uuid.uuid4())[:8],  
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ingredients,
        "number": 12,
        "diet": diet,
        "instructionsRequired": True,
        "addRecipeInformation": True,
        "offset": offset
    }

    try:
        response = requests.get(
            "https://api.spoonacular.com/recipes/complexSearch",
            params={k: v for k, v in params.items() if v is not None}
        )
        response.raise_for_status()
        data = response.json()
        recipes = data.get('results', [])
        
        return render_template(
        "results.html",
        ingredients=ingredients,
        recipes=recipes,
        diet=diet,
        offset=offset  # Pass offset to template
        )

    except requests.HTTPError as e:
        flash(f"API Error: {e.response.status_code} - {e.response.text}", "danger")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for("index"))

@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    try:
        # Get main recipe data
        recipe_response = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/information",
            params={"apiKey": SPOONACULAR_API_KEY, "includeNutrition": True}
        )
        recipe_response.raise_for_status()
        recipe_data = recipe_response.json()

        # Get analyzed instructions
        instructions_response = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions",
            params={"apiKey": SPOONACULAR_API_KEY}
        )
        instructions_data = instructions_response.json() if instructions_response.ok else []

        # Get nutrition data
        nutrition_response = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json",
            params={"apiKey": SPOONACULAR_API_KEY}
        )
        nutrition_data = nutrition_response.json() if nutrition_response.ok else {}

        return render_template(
            "recipe_detail.html",
            recipe=recipe_data,
            instructions=instructions_data,
            nutrition=nutrition_data.get('nutrients', [])
        )
        
    except requests.exceptions.HTTPError as e:
        return render_template("error.html", error_message="Recipe not found"), 404
    except Exception as e:
        return render_template("error.html", error_message=str(e)), 500
    

if __name__ == "__main__":
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    with app.app_context():
        db.create_all()
        print(f"Database path: {os.path.join(app.instance_path, 'database.db')}")    
    app.run(debug=True)

