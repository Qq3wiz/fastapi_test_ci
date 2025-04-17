from sqlalchemy import delete, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import RecipesIngredients, RecipesRaw
from src.models import RecipeIn


async def get_recipes(session: AsyncSession):
    recipes = await session.execute(
        select(RecipesRaw).order_by(
            RecipesRaw.views.desc(), RecipesRaw.cook_time.asc()
        )
    )

    return recipes.unique().scalars().all()


async def get_recipe_with_id(session: AsyncSession, id: int):
    recipe = await session.execute(
        select(RecipesRaw).filter(RecipesRaw.idx == id)
    )

    return recipe.unique().scalars().one()


async def post_new_recipe(session: AsyncSession, data: RecipeIn):
    recipe = RecipesRaw(**data.model_dump())
    writable_ingredients = []

    session.add(recipe)
    await session.flush()

    for ingredient in data.ingredients:
        if not hasattr(ingredient, 'recipe_id'):
           setattr(ingredient, 'recipe_id', recipe.idx) 

        writable_ingredients.append(
            RecipesIngredients(**ingredient.model_dump())
        )

    session.add_all(writable_ingredients)

    await session.commit()

    return recipe.idx


async def delete_recipe_by_id(session: AsyncSession, id: int):
    query = await session.execute(
        delete(RecipesRaw)
        .filter(RecipesRaw.idx == id)
        .returning(RecipesRaw.idx)
    )
    recipe = query.one()

    if recipe[0] == id:
        await session.commit()
        return {"idx": recipe[0], "status": "deleted"}
    else:
        await session.rollback()
        raise NoResultFound
