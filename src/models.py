from typing import List

from pydantic import BaseModel, ConfigDict


class BaseRecipeOut(BaseModel):
    idx: int
    name: str
    cook_time: int

    model_config = ConfigDict(from_attributes=True, extra="ignore")


class RecipeIngredientsModel(BaseModel):
    name: str
    amt: int
    unit: str

    model_config = ConfigDict(from_attributes=True, extra="allow")


class SingleRecipe(BaseRecipeOut):
    description: str
    ingredients: List[RecipeIngredientsModel]


class ListRecipes(BaseRecipeOut):
    views: int


class RecipeIn(BaseModel):
    name: str
    cook_time: int
    description: str
    ingredients: List[RecipeIngredientsModel]


class RecipeErrorDetail(BaseModel):
    id: int
    msg: str


class RecipeErrorBase(BaseModel):
    detail: RecipeErrorDetail


class RecipeDelete(BaseModel):
    id: int
    msg: str


class RecipeAdd(BaseModel):
    status: str
    idx: int
