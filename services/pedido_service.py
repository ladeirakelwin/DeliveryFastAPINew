from models import Pedido
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from fastapi import status

class PedidoService:
    def __init__(self, db: Session):
        self.db = db

    def criando_pedido(self, id_usuario: int) -> Pedido:
        status_pedido: str = "PENDENTE"
        preco: int = 0
        try:
            novo_pedido = Pedido(id_usuario, status_pedido, preco)
            
            self.db.add(novo_pedido)
            self.db.commit()

            return novo_pedido
        except Exception:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Não foi possível criar o pedido, tente novamente mais tarde!")
