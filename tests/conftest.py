from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.utils.senha import criptografar_senha
from models import Usuario, Pedido, ItensPedido
from fastapi.testclient import TestClient
from main import app
from database import Base, get_db
import pytest

TEST_DATABASE_URL = "sqlite:///./test.db"
VALID_USERS: list = [
    {"id": 1, "nome": "adm", "email": "adm@adm.com", "senha": "adm"},
    {"id": 2, "nome": "teste", "email": "teste@teste.com", "senha": "teste"},
]
INVALID_USERS: list = [
    {
        "id": 3,
        "nome": "inativoa",
        "email": "inativoa@inativoa.com",
        "senha": "inativoa",
    },
    {
        "id": 4,
        "nome": "inativob",
        "email": "inativob@inativob.com",
        "senha": "inativob",
    },
    {
        "id": 5,
        "nome": "nonecxiste",
        "email": "nonecxiste@nonecxiste.com",
        "senha": "nonecxiste",
    },
]


@pytest.fixture(scope="session")
def db_engine():
    """Criar um base de dados uma vez por sessão de teste"""
    same_thread = False if "sqlite" in TEST_DATABASE_URL else True
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": same_thread}
    )

    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def mock_get_db(db_engine):
    """Provendo uma sessão limpa de banco de dados para um caso individual"""
    connection = db_engine.connect()

    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(autoflush=False, bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def user_seeded_db(mock_get_db) -> Session:
    """Banco com usuários padrões"""

    mock_get_db.add(
        Usuario(
            nome="adm",
            email="adm@adm.com",
            senha=criptografar_senha("adm"),
            admin=True,
            ativo=True,
        )
    )

    mock_get_db.add(
        Usuario(
            nome="teste",
            email="teste@teste.com",
            senha=criptografar_senha("teste"),
            admin=False,
            ativo=True,
        )
    )

    mock_get_db.add(
        Usuario(
            nome="inativoa",
            email="inativoa@inativoa.com",
            senha=criptografar_senha("inativoa"),
            admin=True,
            ativo=False,
        )
    )

    mock_get_db.add(
        Usuario(
            nome="inativob",
            email="inativob@inativob.com",
            senha=criptografar_senha("inativob"),
            admin=False,
            ativo=False,
        )
    )

    mock_get_db.commit()

    return mock_get_db


@pytest.fixture(scope="function")
def order_seeded_db(user_seeded_db) -> Session:
    user_seeded_db.add_all(
        [
            Pedido(1),
            Pedido(2),
            Pedido(1),
            Pedido(2),
        ]
    )
    user_seeded_db.commit()

    return user_seeded_db


@pytest.fixture(scope="function")
def order_item_seeded_db(order_seeded_db):
    order_seeded_db.add_all(
        [
            ItensPedido(1, "marguerita", "G", "70", 1),
            ItensPedido(2, "atum", "GG", "90", 2),
            ItensPedido(3, "portuguesa", "M", "60", 3),
            ItensPedido(4, "calabresa", "P", "50", 4),
        ]
    )
    order_seeded_db.commit()

    return order_seeded_db


@pytest.fixture(scope="function")
def order_item_without_order_seeded_db(user_seeded_db):
    user_seeded_db.add_all(
        [
            ItensPedido(1, "marguerita", "G", "70", 1),
            ItensPedido(2, "atum", "GG", "90", 2),
            ItensPedido(3, "portuguesa", "M", "60", 3),
            ItensPedido(4, "calabresa", "P", "50", 4),
        ]
    )
    user_seeded_db.commit()

    return user_seeded_db


@pytest.fixture(scope="function")
def client(mock_get_db):
    """Overrides the get_db dependency and returns the TestClient."""

    def _override_get_db():
        try:
            yield mock_get_db
        finally:
            pass

    # Inject the mock session into FastAPI
    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)

    # Clean up overrides after the test finishes
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_user(user_seeded_db):
    """Overrides the get_db dependency and returns the TestClient."""

    def _override_get_db():
        try:
            yield user_seeded_db
        finally:
            pass

    # Inject the mock session into FastAPI
    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)

    # Clean up overrides after the test finishes
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_order(order_seeded_db):
    def _override_get_db():
        try:
            yield order_seeded_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_order_item(order_item_seeded_db):
    def _override_get_db():
        try:
            yield order_item_seeded_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_order_item_without_order(order_item_without_order_seeded_db):
    def _override_get_db():
        try:
            yield order_item_without_order_seeded_db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
