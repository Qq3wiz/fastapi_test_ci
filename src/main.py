from contextlib import asynccontextmanager
from typing import Dict, List, Union

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.database import Base, engine, get_session
from src.models import (
    RecipeAdd,
    RecipeDelete,
    RecipeErrorBase,
    RecipeIn,
    SingleRecipe,
)
from src.queries import (
    delete_recipe_by_id,
    get_recipe_with_id,
    get_recipes,
    post_new_recipe,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


app = FastAPI(
    title="Кулинарная книга",
    description="API для доступа к базе рецептов",
    lifespan=lifespan,
)


@app.get(
    "/recipes",
    response_model=List[SingleRecipe],
    tags=["Recipes"],
    summary="Получает список всех рецептов в базе.",
    description="".join(
        (
            "Данные полученные из бд отфильтрованы по времени готовки (ASC),",
            "количеству просмотров (DESC)",
        ),
    ),
)
async def get_all_recipes(
    session: Annotated[AsyncSession, Depends(get_session)]
):
    return await get_recipes(session)


@app.get(
    "/recipes/",
    response_model=SingleRecipe,
    responses={status.HTTP_404_NOT_FOUND: {"model": RecipeErrorBase}},
    tags=["Recipes"],
    summary="Получает подробную информацию рецепта из бд",
)
async def get_recipe_by_id(
    session: Annotated[AsyncSession, Depends(get_session)],
    id: int = Query(..., title="id of recipe"),
):
    try:
        return await get_recipe_with_id(session, id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"id": id, "msg": "Item with current id doesn`t exist."},
        ) from None


@app.post(
    "/recipes",
    responses={status.HTTP_201_CREATED: {"model": RecipeAdd}},
    response_model=RecipeAdd,
    tags=["Recipes"],
    summary="Добавляет новый рецепт в бд.",
    status_code=status.HTTP_201_CREATED,
)
async def add_recipe(
    data: RecipeIn, session: Annotated[AsyncSession, Depends(get_session)]
) -> Dict[str, Union[str, int]]:
    recipe_id = await post_new_recipe(session, data)

    return {"status": "ok", "idx": recipe_id}


@app.delete(
    "/recipes/",
    responses={
        status.HTTP_200_OK: {"model": RecipeDelete},
        status.HTTP_409_CONFLICT: {"model": RecipeErrorBase},
    },
    tags=["Recipes"],
    summary="Удаляет рецепт из базы данных.",
)
async def delete_recipe(
    session: Annotated[AsyncSession, Depends(get_session)],
    id: int = Query(..., title="id of recipe"),
):
    try:
        return await delete_recipe_by_id(session, id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"id": id, "msg": "Can`t delete recipe. No such id."},
        ) from None
