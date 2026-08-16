from fastapi.exceptions import HTTPException
from fastapi import status

TOKEN_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Erro ao gerar token! Tente novamente mais tarde.",
)

UNAUTHORIZED_USER = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Usuário não autorizado ou token expirado!",
)

ORDER_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Erro ao buscar pedido! Tente novamente mais tarde.",
)

ORDER_NOT_CREATED = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    detail="Não foi possível criar o pedido, tente novamente mais tarde!",
)

ORDER_NOT_FOUNDED = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado!"
)

ORDER_ITEM_NOT_FOUNDED = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item pedido não encontrado!",
)

ORDER_ITEM_WITH_ORDER_NOT_FOUNDED = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Pedido associado ao item pedido não encontrado!",
)

SQL_ERROR = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Tente novamente mais tarde!",
)


def start_detail_error(initial_error: str, Exception: HTTPException) -> HTTPException:
    Exception.detail = initial_error + Exception.detail
    return Exception
