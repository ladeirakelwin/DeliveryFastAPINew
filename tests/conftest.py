from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.utils.senha import criptografar_senha
from models import Usuario, Pedido
from database import Base
import pytest

TEST_DATABASE_URL = "sqlite:///./test.db"


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
def order_seeded_db(user_seeded_db):
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
