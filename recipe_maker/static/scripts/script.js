async function fetchRecipes(event) {
    event.preventDefault(); 

    const ingredients = document.getElementById("ingredientInput").value.trim();
    if (!ingredients) {
        alert("Please enter ingredients!");
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:5000/search?ingredients=${ingredients}`);
        
        if (response.ok) {
            const data = await response.json();
            displayRecipes(data);  
        } else {
            console.error("Error fetching recipes");
            alert("Failed to fetch recipes. Please try again.");
        }
    } catch (error) {
        console.error("Fetch error:", error);
        alert("Something went wrong!");
    }
}


document.getElementById('findRecipes').addEventListener('click', fetchRecipes);

function displayRecipes(recipes) {
    const resultsDiv = document.getElementById("results");
    resultsDiv.innerHTML = "";  
    
    if (recipes.length === 0) {
        resultsDiv.innerHTML = "<p>No recipes found. Try different ingredients.</p>";
        return;
    }

    recipes.forEach(recipe => {
        const recipeDiv = document.createElement("div");
        recipeDiv.innerHTML = `
            <h3>${recipe.title}</h3>
            <img src="${recipe.image}" alt="${recipe.title}" width="200">
            <p><strong>Used Ingredients:</strong> ${recipe.usedIngredientCount}</p>
            <p><strong>Missing Ingredients:</strong> ${recipe.missedIngredientCount}</p>
        `;
        resultsDiv.appendChild(recipeDiv);
    });
}
