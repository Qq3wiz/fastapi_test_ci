import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import RecipesIngredients, RecipesRaw


@pytest.mark.asyncio
async def test_get_all_recipes(client: AsyncClient, db: AsyncSession):
    response = await client.get("/recipes")

    assert response.status_code == 200
    assert response.json() == []

    recipe = RecipesRaw(name="test", cook_time=10, description="test")
    db.add(recipe)
    await db.commit()
    assert recipe.idx == 1

    response = await client.get("/recipes")

    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_recipe_by_id(client: AsyncClient, db: AsyncSession):
    """Test get recipe by id."""
    recipe = RecipesRaw(name="test", cook_time=10, description="test")
    db.add(recipe)
    await db.commit()
    assert recipe.idx == 1

    response = await client.get("/recipes/?id=1")
    print(response.json())

    assert response.status_code == 200
    assert response.json() == {
        "idx": recipe.idx,
        "name": recipe.name,
        "cook_time": recipe.cook_time,
        "description": recipe.description,
        "ingredients": [],
    }


@pytest.mark.asyncio
async def test_post_recipe(client: AsyncClient, db: AsyncSession):
    """Test post new recipe"""
    recipe = {
        "name": "test",
        "cook_time": 10,
        "description": "test",
        "ingredients": [
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
        ],
    }

    response = await client.post("/recipes", json=recipe)

    assert response.status_code == 201
    assert response.json() == {"status": "ok", "idx": 1}

    current_state = await db.execute(select(RecipesRaw))
    current_state = current_state.scalars().all()

    assert len(current_state[0].ingredients) == 5
    assert len(current_state) == 1


@pytest.mark.asyncio
async def test_delete_recipe(client: AsyncClient, db: AsyncSession):
    recipe = {
        "name": "test",
        "cook_time": 10,
        "description": "test",
        "ingredients": [
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
            {"name": "test", "amt": 5, "unit": "test"},
        ],
    }
    temp_response = await client.post("/recipes", json=recipe)
    recipe_idx = temp_response.json()["idx"]

    recipes = await db.execute(select(RecipesRaw))
    recipes = recipes.scalars().all()

    assert len(recipes) == 1
    assert len(recipes[0].ingredients) == len(recipe["ingredients"])

    response = await client.delete(f"/recipes/?id={recipe_idx}")

    assert response.status_code == 200
    assert response.json()["idx"] == recipe_idx

    recipes = await db.execute(select(RecipesRaw))
    assert len(recipes.scalars().all()) == 0

    recipes_details = await db.execute(select(RecipesIngredients))
    assert len(recipes_details.scalars().all()) == 0
