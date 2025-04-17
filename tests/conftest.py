import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_session
from src.main import app

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
test_engine.sync_engine.echo = False
test_local_session = sessionmaker(
    test_engine, autoflush=False, class_=AsyncSession, expire_on_commit=False
)


@event.listens_for(test_engine.sync_engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cur = dbapi_connection.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


async def get_test_session():
    """Dependency override for session in FastAPI."""
    test_session = test_local_session()

    try:
        yield test_session
        await test_session.commit()
    except Exception as e:
        await test_session.rollback()
        raise e
    finally:
        await test_session.close()


@pytest_asyncio.fixture(scope="function")
async def db():
    """Fixture with test database."""
    session = test_local_session()

    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Fixture with FastAPI test client."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_session] = get_test_session

    client = AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    )

    yield client

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
