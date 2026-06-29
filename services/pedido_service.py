from models import Pedido, Usuario, ItensPedido
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
from fastapi import status
from schemas import ItemPedidoSchema

class PedidoService:
    def __init__(self, db: Session):
        self.db = db

    def _calcular_total_pedido(self, pedido: Pedido) -> Pedido:
        pedido.preco = sum([float(item.preco_unitario) * int(item.quantidade) for item in pedido.itens])
        
        self.db.commit()
        self.db.refresh(pedido)
        
        return pedido


    def _obtendo_pedido(self, id_pedido: int) -> Pedido | None:
        pedido_db = select(Pedido).where(Pedido.id == id_pedido)
        pedido = self.db.scalar(pedido_db)
        return pedido

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
        
    def adicionando_item_pedido(self, id_pedido: int, usuario: Usuario, item_pedido: ItemPedidoSchema) -> tuple[Pedido, ItensPedido]:
        try:
            pedido = self._obtendo_pedido(id_pedido)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao buscar pedido! Tente novamente mais tarde.")
        if not pedido:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado!")
        
        if not usuario.admin and usuario.id != pedido.usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario não autorizado!")
        
        novo_item_pedido = ItensPedido(quantidade=item_pedido.quantidade
                                       ,sabor=item_pedido.sabor
                                       ,tamanho=item_pedido.tamanho
                                       ,preco_unitario=item_pedido.preco_unitario
                                       ,pedido=pedido.id)
        

        self.db.add(novo_item_pedido)
        self.db.commit()

        pedido_atualizado = self._calcular_total_pedido(pedido)

        return pedido_atualizado, novo_item_pedido

        



        
