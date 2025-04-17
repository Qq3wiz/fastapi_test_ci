from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)

from src.config import settings

engine = create_async_engine(settings.DATABASE_URL)
localSession = sessionmaker(  # type: ignore
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    """Session DI for FastAPI."""
    session = localSession()

    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


class Base(DeclarativeBase):
    pass


class RecipesRaw(Base):  # type: ignore
    """
    Таблица данных карточки рецептов в базе: название блюда, время готовки,
    сколько раз просматривали.\n\n
    :param idx: идентификационный номер рецепта.\n
    :param name: название блюда.\n
    :param views: Количество просмотров блюда.\n
    :param cook_time: Время приготовления блюда в минутах.\n
    :param description: Описание блюда.\n
    :param ingredients: Список ингридиентов.\n
    """

    __tablename__ = "recipes_raw"

    idx: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    views: Mapped[int] = mapped_column(nullable=False, default=0)
    cook_time: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=False)

    ingredients = relationship(
        "RecipesIngredients",
        lazy="selectin",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __init__(self, name: str, cook_time: int, description: str, **kwargs):
        self.name = name  # type: ignore
        self.cook_time = cook_time  # type: ignore
        self.description = description  # type: ignore


class RecipesIngredients(Base):  # type: ignore
    __tablename__ = "recipes_ingredients"

    idx: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        ForeignKey("recipes_raw.idx", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    amt: Mapped[int] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)

    def __init__(self, recipe_id: int, name: str, amt: int, unit: str, **kw):
        self.recipe_id = recipe_id
        self.name = name
        self.amt = amt
        self.unit = unit
