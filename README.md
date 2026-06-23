# 1. Visão geral da aplicação

* **Nome provável da aplicação:** `DeliveryFastAPI`
* **Objetivo principal:** fornecer uma API para cadastro/autenticação de usuários e gerenciamento básico de pedidos de delivery, com itens, preço total e status do pedido.
* **Tipo de aplicação:** API
* **Frameworks principais:** FastAPI, SQLAlchemy, Alembic, Pydantic
* **Linguagem e versão Python sugerida:** Python `3.12.13`, confirmado por `.python-version` e `pyproject.toml`.
* **Público-alvo ou usuário final:** usuários/clientes de um sistema simples de pedidos e administradores que podem listar e gerenciar pedidos.
* **Resumo do funcionamento em 5 a 10 linhas:**

A aplicação expõe uma API REST com rotas de autenticação e rotas de pedidos. O usuário pode criar conta, realizar login e receber tokens JWT. As rotas de pedidos exigem autenticação via Bearer Token. Um pedido pertence a um usuário, inicia com status `PENDENTE` e preço `0`. É possível adicionar e remover itens do pedido, recalculando o preço total com base em quantidade e preço unitário. Usuários comuns só podem acessar/modificar seus próprios pedidos; administradores têm acesso ampliado. O banco usado é SQLite local, por meio do arquivo `banco.db`. A aplicação contém configuração via `.env`, mas o banco está hardcoded em `models.py`.

---

# 2. Estrutura do projeto

```text
/DeliveryFastAPI
  .env
  .gitignore
  .python-version
  README.md
  __init__.py
  main.py
  auth_routes.py
  order_routes.py
  dependencies.py
  models.py
  schemas.py
  teste.py
  banco.db
  requirements.txt
  pyproject.toml
  uv.lock
  alembic.ini
  /alembic
    env.py
    README
    script.py.mako
    /versions
      e9b4b5830922_initial_migration.py
  /.git
  /__pycache__
```

## Função de cada pasta/arquivo importante

| Arquivo/Pasta                                        | Função identificada                                                                                            | Status     |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------- |
| `main.py`                                            | Cria a instância FastAPI e registra os routers de autenticação e pedidos.                                      | Confirmado |
| `auth_routes.py`                                     | Define rotas de cadastro, login, login via formulário OAuth2 e refresh de token.                               | Confirmado |
| `order_routes.py`                                    | Define rotas protegidas para criar, listar, visualizar, cancelar, finalizar pedidos e adicionar/remover itens. | Confirmado |
| `dependencies.py`                                    | Centraliza dependências de sessão SQLAlchemy, hashing bcrypt, OAuth2 Bearer e validação JWT.                   | Confirmado |
| `models.py`                                          | Define conexão SQLite, `Base` SQLAlchemy e modelos `Usuario`, `Pedido`, `ItemPedido`.                          | Confirmado |
| `schemas.py`                                         | Define schemas Pydantic de entrada e resposta.                                                                 | Confirmado |
| `banco.db`                                           | Banco SQLite local já incluído no projeto, com tabelas e dados.                                                | Confirmado |
| `.env`                                               | Contém configurações de JWT/token. Valores não expostos por segurança.                                         | Confirmado |
| `requirements.txt`                                   | Lista dependências Python para instalação via pip.                                                             | Confirmado |
| `pyproject.toml`                                     | Define projeto, versão, Python mínimo e dependências, provavelmente para uso com `uv`.                         | Confirmado |
| `uv.lock`                                            | Lockfile do gerenciador `uv`.                                                                                  | Confirmado |
| `alembic.ini`                                        | Configuração do Alembic apontando para SQLite `banco.db`.                                                      | Confirmado |
| `alembic/env.py`                                     | Configura migrations Alembic usando `Base.metadata` dos modelos.                                               | Confirmado |
| `alembic/versions/e9b4b5830922_initial_migration.py` | Migration inicial criando tabelas `usuarios`, `pedidos` e `itens_pedido`.                                      | Confirmado |
| `teste.py`                                           | Script manual usando `requests` para chamar `/auth/refresh` com Bearer Token hardcoded.                        | Confirmado |
| `README.md`                                          | Arquivo existe, mas está vazio.                                                                                | Confirmado |
| `.git/`                                              | Metadados Git incluídos no ZIP. Não fazem parte da aplicação em si.                                            | Confirmado |
| `__pycache__/`                                       | Arquivos compilados Python. Não são necessários para reconstrução.                                             | Confirmado |

---

# 3. Dependências e ambiente

| Item                  | Valor identificado                                                  | Fonte                                           | Observação                                                  |
| --------------------- | ------------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------- |
| Framework web         | FastAPI                                                             | `main.py`, `requirements.txt`, `pyproject.toml` | Confirmado                                                  |
| Servidor ASGI         | Uvicorn                                                             | `requirements.txt`, `pyproject.toml`            | Confirmado                                                  |
| ORM                   | SQLAlchemy                                                          | `models.py`, `dependencies.py`                  | Confirmado                                                  |
| Migrations            | Alembic                                                             | `alembic.ini`, `/alembic`                       | Confirmado                                                  |
| Banco                 | SQLite                                                              | `models.py`, `alembic.ini`, `banco.db`          | Confirmado                                                  |
| Autenticação          | OAuth2 Bearer + JWT                                                 | `dependencies.py`, `auth_routes.py`             | Confirmado                                                  |
| JWT                   | `python-jose`                                                       | `auth_routes.py`, `dependencies.py`             | Confirmado                                                  |
| Hash de senha         | Passlib + bcrypt                                                    | `dependencies.py`, `auth_routes.py`             | Confirmado                                                  |
| Validação de dados    | Pydantic                                                            | `schemas.py`                                    | Confirmado                                                  |
| Variáveis de ambiente | `.env` com `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | `.env`, `dependencies.py`                       | Valores não expostos                                        |
| Python                | `3.12.13`                                                           | `.python-version`, `pyproject.toml`             | Confirmado                                                  |
| Gerenciador possível  | `uv`                                                                | `uv.lock`, `pyproject.toml`                     | Inferido                                                    |
| Testes automatizados  | Não encontrado                                                      | Estrutura do projeto                            | Não há pasta `tests` nem pytest/unittest                    |
| Docker                | Não encontrado                                                      | Estrutura do projeto                            | Não há `Dockerfile` nem `docker-compose.yml`                |
| Cache/Fila            | Não encontrado                                                      | Código                                          | Não confirmado                                              |
| Serviços externos     | Não encontrados                                                     | Código                                          | A aplicação só usa SQLite local; `teste.py` chama API local |

## Dependências Python identificadas

Principais dependências relevantes:

* `fastapi`
* `uvicorn`
* `sqlalchemy`
* `alembic`
* `pydantic`
* `python-dotenv`
* `python-jose`
* `passlib`
* `bcrypt`
* `python-multipart`
* `requests`

Observações:

* `requirements.txt` não lista `requests`, mas `teste.py` usa `requests`.
* `pyproject.toml` lista `requests`, então há divergência entre `requirements.txt` e `pyproject.toml`.
* `sqlalchemy-utils` aparece no `pyproject.toml`, mas não foi identificado uso direto no código principal.
* O projeto não possui `.env.example`.

## Comandos prováveis para instalar e executar

### Com pip

```bash
cd DeliveryFastAPI
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate no Windows

pip install -r requirements.txt
uvicorn main:app --reload
```

### Com uv

```bash
cd DeliveryFastAPI
uv sync
uv run uvicorn main:app --reload
```

### Com Alembic

```bash
cd DeliveryFastAPI
alembic upgrade head
```

Observação: como `main.py` usa imports diretos como `from auth_routes import ...`, a forma mais segura é executar o Uvicorn a partir da pasta `DeliveryFastAPI`.

---

# 4. Arquitetura técnica

## Estilo arquitetural

A aplicação usa uma arquitetura simples e monolítica, baseada em FastAPI com separação mínima por arquivos:

* `main.py`: composição da aplicação.
* `auth_routes.py`: rotas de autenticação.
* `order_routes.py`: rotas de pedidos.
* `models.py`: modelos ORM e conexão com banco.
* `schemas.py`: schemas Pydantic.
* `dependencies.py`: dependências compartilhadas, sessão e autenticação.

Não há camada explícita de serviço, repositório, domínio ou use cases. As rotas acessam diretamente os modelos SQLAlchemy e manipulam regras de negócio dentro dos endpoints.

## Diagrama textual

```text
Cliente HTTP
   ↓
FastAPI / main.py
   ↓
Routers
   ├── auth_routes.py
   └── order_routes.py
        ↓
Dependências
   ├── pegar_sessao()
   ├── verificar_token()
   └── bcrypt_context / OAuth2 / JWT
        ↓
Modelos SQLAlchemy
   ├── Usuario
   ├── Pedido
   └── ItemPedido
        ↓
SQLite
   └── banco.db
```

## Camadas identificadas

| Camada                   | Arquivos                                       | Responsabilidade                              | Status     |
| ------------------------ | ---------------------------------------------- | --------------------------------------------- | ---------- |
| Entrada HTTP/API         | `main.py`, `auth_routes.py`, `order_routes.py` | Receber requisições e retornar respostas JSON | Confirmado |
| Validação de entrada     | `schemas.py`                                   | Definir formato dos dados esperados           | Confirmado |
| Autenticação/autorização | `dependencies.py`, `auth_routes.py`            | Criar/verificar JWT e restringir acesso       | Confirmado |
| Persistência             | `models.py`, `banco.db`                        | Mapear entidades e persistir em SQLite        | Confirmado |
| Migration                | `alembic/`                                     | Criar schema do banco                         | Confirmado |
| Teste/manual client      | `teste.py`                                     | Chamar endpoint local com token               | Confirmado |

## Padrões usados

* Router por domínio: `auth` e `pedidos`.
* Dependency Injection do FastAPI com `Depends`.
* ORM com Active Record simplificado via SQLAlchemy.
* DTOs/schemas com Pydantic.
* Autenticação por Bearer Token JWT.
* Migrations com Alembic.

## Pontos de acoplamento

* `models.py` contém a URL do banco hardcoded: `sqlite:///banco.db`.
* As rotas dependem diretamente dos modelos SQLAlchemy.
* A regra de autorização está repetida em várias rotas de pedido.
* `dependencies.py` depende diretamente de `Usuario` e da conexão `db`.
* Os status de pedido são strings soltas, sem enum centralizado.

## Pontos de extensão

* Criar camada `services/` para regras de negócio.
* Criar camada `repositories/` para acesso ao banco.
* Mover configurações para `settings.py` usando Pydantic Settings.
* Criar módulo de produtos/cardápio.
* Criar validações de pedido, preço, quantidade e status.
* Adicionar testes automatizados.
* Trocar SQLite por PostgreSQL em produção.
* Adicionar Docker e `.env.example`.

---

# 5. Funcionalidades identificadas

## Funcionalidade: Cadastro de usuário

* **Descrição:** permite criar um usuário com nome, email, senha, ativo e admin.
* **Entrada:** `nome`, `email`, `senha`, `ativo`, `admin`.
* **Processamento:** verifica se email já existe; criptografa senha com bcrypt; salva usuário.
* **Saída:** mensagem de sucesso com email.
* **Arquivos/módulos relacionados:** `auth_routes.py`, `schemas.py`, `models.py`, `dependencies.py`.
* **Regras de negócio:** email não pode estar previamente cadastrado; senha deve ser armazenada criptografada.
* **Evidência no código:** `POST /auth/criar_conta`.
* **Status:** Confirmado.

## Funcionalidade: Login via JSON

* **Descrição:** autentica usuário por email e senha.
* **Entrada:** `email`, `senha`.
* **Processamento:** busca usuário por email; valida senha com bcrypt; gera access token e refresh token.
* **Saída:** `access_token`, `refresh_token`, `token_type`.
* **Arquivos/módulos relacionados:** `auth_routes.py`, `dependencies.py`.
* **Regras de negócio:** credenciais inválidas retornam erro; token contém `sub` com ID do usuário e expiração.
* **Evidência no código:** `POST /auth/login`.
* **Status:** Confirmado.

## Funcionalidade: Login via formulário OAuth2

* **Descrição:** autentica via `OAuth2PasswordRequestForm`.
* **Entrada:** `username` usado como email e `password` como senha.
* **Processamento:** autentica usuário e gera access token.
* **Saída:** `access_token`, `token_type`.
* **Arquivos/módulos relacionados:** `auth_routes.py`, `dependencies.py`.
* **Regras de negócio:** usado pelo fluxo OAuth2 Bearer do FastAPI.
* **Evidência no código:** `POST /auth/login-form`.
* **Status:** Confirmado.

## Funcionalidade: Refresh de access token

* **Descrição:** gera novo access token para usuário autenticado.
* **Entrada:** Bearer Token válido.
* **Processamento:** valida token, identifica usuário e cria novo access token.
* **Saída:** novo `access_token`.
* **Arquivos/módulos relacionados:** `auth_routes.py`, `dependencies.py`, `teste.py`.
* **Regras de negócio:** depende de token válido e usuário existente.
* **Evidência no código:** `GET /auth/refresh`.
* **Status:** Confirmado.

## Funcionalidade: Criar pedido

* **Descrição:** cria pedido para um usuário informado.
* **Entrada:** `usuario` com ID do usuário.
* **Processamento:** cria `Pedido` com status padrão `PENDENTE` e preço inicial `0`.
* **Saída:** mensagem com ID do pedido criado.
* **Arquivos/módulos relacionados:** `order_routes.py`, `schemas.py`, `models.py`.
* **Regras de negócio:** pedido pertence a um usuário; preço inicial é zero.
* **Evidência no código:** `POST /pedidos/pedido`.
* **Status:** Confirmado.

Observação importante: a rota é protegida por token, mas o usuário dono do pedido vem do corpo da requisição. Não foi confirmada validação garantindo que o usuário autenticado seja o mesmo usuário informado no body.

## Funcionalidade: Cancelar pedido

* **Descrição:** altera o status do pedido para `CANCELADO`.
* **Entrada:** `id_pedido`.
* **Processamento:** busca pedido; verifica se usuário é admin ou dono do pedido; altera status.
* **Saída:** mensagem de sucesso e objeto do pedido.
* **Arquivos/módulos relacionados:** `order_routes.py`.
* **Regras de negócio:** apenas admin ou dono pode cancelar.
* **Evidência no código:** `POST /pedidos/pedido/cancelar/{id_pedido}`.
* **Status:** Confirmado.

## Funcionalidade: Finalizar pedido

* **Descrição:** altera o status do pedido para `FINALIZADO`.
* **Entrada:** `id_pedido`.
* **Processamento:** busca pedido; verifica autorização; altera status.
* **Saída:** mensagem de sucesso e objeto do pedido.
* **Arquivos/módulos relacionados:** `order_routes.py`.
* **Regras de negócio:** apenas admin ou dono pode finalizar.
* **Evidência no código:** `POST /pedidos/pedido/finalizar/{id_pedido}`.
* **Status:** Confirmado.

## Funcionalidade: Adicionar item ao pedido

* **Descrição:** adiciona item a um pedido.
* **Entrada:** `id_pedido`, `quantidade`, `sabor`, `tamanho`, `preco_unitario`.
* **Processamento:** busca pedido; verifica autorização; cria `ItemPedido`; recalcula preço total.
* **Saída:** mensagem, ID do item e preço atualizado do pedido.
* **Arquivos/módulos relacionados:** `order_routes.py`, `schemas.py`, `models.py`.
* **Regras de negócio:** preço do pedido é a soma de `quantidade * preco_unitario` dos itens.
* **Evidência no código:** `POST /pedidos/pedido/adicionar-item/{id_pedido}`.
* **Status:** Confirmado.

Observação técnica: quando o pedido não existe, o código instancia `HTTPException`, mas não usa `raise`, o que pode causar erro posterior.

## Funcionalidade: Remover item do pedido

* **Descrição:** remove um item de pedido.
* **Entrada:** `id_item_pedido`.
* **Processamento:** busca item; busca pedido associado; verifica autorização; remove item; recalcula preço.
* **Saída:** mensagem, quantidade de itens e pedido.
* **Arquivos/módulos relacionados:** `order_routes.py`, `models.py`.
* **Regras de negócio:** apenas admin ou dono pode remover item.
* **Evidência no código:** `POST /pedidos/pedido/remover-item/{id_item_pedido}`.
* **Status:** Confirmado, com falha potencial.

Observação técnica: o código acessa `item_pedido.pedido` antes de validar se `item_pedido` existe. Se o item não existir, tende a gerar erro 500.

## Funcionalidade: Visualizar pedido

* **Descrição:** consulta um pedido específico.
* **Entrada:** `id_pedido`.
* **Processamento:** busca pedido; valida se usuário é admin ou dono.
* **Saída:** quantidade de itens e objeto do pedido.
* **Arquivos/módulos relacionados:** `order_routes.py`.
* **Regras de negócio:** apenas admin ou dono pode visualizar.
* **Evidência no código:** `GET /pedidos/pedido/{id_pedido}`.
* **Status:** Confirmado.

## Funcionalidade: Listar todos os pedidos

* **Descrição:** retorna todos os pedidos do sistema.
* **Entrada:** Bearer Token de usuário admin.
* **Processamento:** valida token; verifica se `admin=True`; consulta todos os pedidos.
* **Saída:** lista de pedidos.
* **Arquivos/módulos relacionados:** `order_routes.py`.
* **Regras de negócio:** apenas administradores podem listar todos os pedidos.
* **Evidência no código:** `GET /pedidos/listar`.
* **Status:** Confirmado.

## Funcionalidade: Listar pedidos do usuário autenticado

* **Descrição:** retorna pedidos vinculados ao usuário autenticado.
* **Entrada:** Bearer Token.
* **Processamento:** identifica usuário pelo token; consulta pedidos com `Pedido.usuario == usuario.id`.
* **Saída:** lista de pedidos com itens.
* **Arquivos/módulos relacionados:** `order_routes.py`, `schemas.py`.
* **Regras de negócio:** cada usuário comum só lista seus próprios pedidos.
* **Evidência no código:** `GET /pedidos/listar/pedido-usuario/`.
* **Status:** Confirmado.

---

# 6. Requisitos funcionais

| ID     | Requisito funcional                                         | Descrição                                                                                         | Prioridade | Evidência                                   |
| ------ | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | ---------- | ------------------------------------------- |
| RF-001 | O sistema deve permitir cadastro de usuários.               | Deve receber nome, email, senha, ativo e admin, validar duplicidade de email e persistir usuário. | Alta       | `auth_routes.py`, `schemas.py`, `models.py` |
| RF-002 | O sistema deve criptografar senhas.                         | A senha deve ser salva usando hash bcrypt.                                                        | Alta       | `auth_routes.py`, `dependencies.py`         |
| RF-003 | O sistema deve autenticar usuários por email e senha.       | Deve validar credenciais e retornar tokens JWT.                                                   | Alta       | `auth_routes.py`                            |
| RF-004 | O sistema deve emitir access token JWT.                     | O token deve conter identificador do usuário e expiração.                                         | Alta       | `auth_routes.py`                            |
| RF-005 | O sistema deve emitir refresh token.                        | O login JSON deve retornar refresh token com duração maior.                                       | Média      | `auth_routes.py`                            |
| RF-006 | O sistema deve permitir renovação de access token.          | Usuário autenticado deve conseguir obter novo access token.                                       | Média      | `auth_routes.py`                            |
| RF-007 | O sistema deve proteger rotas de pedidos.                   | Todas as rotas sob `/pedidos` devem exigir Bearer Token.                                          | Alta       | `order_routes.py`, `dependencies.py`        |
| RF-008 | O sistema deve permitir criar pedido.                       | Deve criar pedido para um usuário com status inicial `PENDENTE`.                                  | Alta       | `order_routes.py`, `models.py`              |
| RF-009 | O sistema deve permitir adicionar item ao pedido.           | Deve adicionar quantidade, sabor, tamanho e preço unitário.                                       | Alta       | `order_routes.py`, `models.py`              |
| RF-010 | O sistema deve recalcular preço do pedido.                  | O preço total deve ser soma de quantidade vezes preço unitário dos itens.                         | Alta       | `models.py`, `order_routes.py`              |
| RF-011 | O sistema deve permitir remover item do pedido.             | Deve remover item e recalcular o preço total.                                                     | Alta       | `order_routes.py`                           |
| RF-012 | O sistema deve permitir cancelar pedido.                    | Deve alterar status para `CANCELADO`.                                                             | Média      | `order_routes.py`                           |
| RF-013 | O sistema deve permitir finalizar pedido.                   | Deve alterar status para `FINALIZADO`.                                                            | Média      | `order_routes.py`                           |
| RF-014 | O sistema deve permitir visualizar pedido.                  | Deve retornar pedido e quantidade de itens.                                                       | Alta       | `order_routes.py`                           |
| RF-015 | O sistema deve permitir listar pedidos do próprio usuário.  | Deve filtrar pedidos pelo usuário autenticado.                                                    | Alta       | `order_routes.py`                           |
| RF-016 | O sistema deve permitir listagem administrativa de pedidos. | Apenas usuários admin devem listar todos os pedidos.                                              | Média      | `order_routes.py`                           |
| RF-017 | O sistema deve validar autorização por dono ou admin.       | Modificações/consultas de pedido devem ser permitidas apenas ao dono ou admin.                    | Alta       | `order_routes.py`                           |
| RF-018 | O sistema deve possuir migrations de banco.                 | Deve usar Alembic para criação das tabelas.                                                       | Média      | `alembic/`                                  |

---

# 7. Regras de negócio

| ID     | Regra de negócio                                                                | Onde aparece                               | Observação                                                  |
| ------ | ------------------------------------------------------------------------------- | ------------------------------------------ | ----------------------------------------------------------- |
| RN-001 | Um email não deve ser cadastrado mais de uma vez.                               | `auth_routes.py`                           | Confirmado no código, mas não há constraint única no banco. |
| RN-002 | A senha deve ser armazenada como hash bcrypt.                                   | `auth_routes.py`, `dependencies.py`        | Confirmado                                                  |
| RN-003 | Login só deve ser aceito se email existir e senha conferir.                     | `auth_routes.py`                           | Confirmado                                                  |
| RN-004 | JWT deve carregar o ID do usuário no campo `sub`.                               | `auth_routes.py`                           | Confirmado                                                  |
| RN-005 | JWT deve possuir expiração.                                                     | `auth_routes.py`                           | Confirmado                                                  |
| RN-006 | Rotas de pedidos exigem autenticação.                                           | `order_routes.py`                          | Confirmado                                                  |
| RN-007 | Pedido novo começa com status `PENDENTE`.                                       | `models.py`                                | Confirmado                                                  |
| RN-008 | Pedido novo começa com preço `0`.                                               | `models.py`                                | Confirmado                                                  |
| RN-009 | O preço do pedido é calculado por soma dos itens.                               | `models.py`                                | Confirmado                                                  |
| RN-010 | Cada item calcula subtotal por `preco_unitario * quantidade`.                   | `models.py`                                | Confirmado                                                  |
| RN-011 | Apenas admin ou dono do pedido pode cancelar pedido.                            | `order_routes.py`                          | Confirmado                                                  |
| RN-012 | Apenas admin ou dono do pedido pode finalizar pedido.                           | `order_routes.py`                          | Confirmado                                                  |
| RN-013 | Apenas admin ou dono do pedido pode visualizar pedido.                          | `order_routes.py`                          | Confirmado                                                  |
| RN-014 | Apenas admin ou dono do pedido pode adicionar/remover item.                     | `order_routes.py`                          | Confirmado                                                  |
| RN-015 | Apenas admin pode listar todos os pedidos.                                      | `order_routes.py`                          | Confirmado                                                  |
| RN-016 | Usuário comum só lista seus próprios pedidos na rota `/listar/pedido-usuario/`. | `order_routes.py`                          | Confirmado                                                  |
| RN-017 | Status conhecidos são `PENDENTE`, `CANCELADO` e `FINALIZADO`.                   | `models.py`, `order_routes.py`, `banco.db` | Confirmado                                                  |
| RN-018 | O campo `ativo` existe, mas não é usado para bloquear login ou acesso.          | `models.py`, `auth_routes.py`              | Confirmado como lacuna                                      |
| RN-019 | O cliente consegue enviar `admin` no cadastro.                                  | `schemas.py`, `auth_routes.py`             | Confirmado; risco de segurança                              |
| RN-020 | Ao criar pedido, o ID do usuário vem do corpo da requisição.                    | `schemas.py`, `order_routes.py`            | Confirmado; risco de autorização                            |

---

# 8. Requisitos não funcionais

| ID      | Requisito não funcional            | Descrição                                                                           | Evidência                                     | Prioridade |
| ------- | ---------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------------- | ---------- |
| RNF-001 | Segurança de senhas                | Senhas devem ser protegidas com bcrypt.                                             | `dependencies.py`, `auth_routes.py`           | Alta       |
| RNF-002 | Autenticação por token             | Rotas protegidas devem usar Bearer Token JWT.                                       | `dependencies.py`, `order_routes.py`          | Alta       |
| RNF-003 | Configuração sensível via ambiente | Segredo JWT, algoritmo e expiração devem vir de variáveis de ambiente.              | `.env`, `dependencies.py`                     | Alta       |
| RNF-004 | Não exposição de segredos          | `.env`, tokens e banco com hashes não devem ser versionados/publicados.             | `.env`, `teste.py`, `banco.db`                | Alta       |
| RNF-005 | Persistência local                 | A aplicação deve persistir dados em SQLite.                                         | `models.py`, `banco.db`                       | Média      |
| RNF-006 | Migração de schema                 | Schema deve ser reproduzível via Alembic.                                           | `alembic/`                                    | Média      |
| RNF-007 | Manutenibilidade                   | O sistema deveria separar regras de negócio de rotas.                               | Rotas acessam ORM diretamente                 | Média      |
| RNF-008 | Tratamento de erros HTTP           | Erros de autenticação, autorização e não encontrado devem retornar HTTPException.   | `auth_routes.py`, `order_routes.py`           | Alta       |
| RNF-009 | Observabilidade                    | Aplicação deveria usar logs estruturados.                                           | Não encontrado; há apenas `print` em uma rota | Média      |
| RNF-010 | Performance                        | Listagens deveriam ter paginação.                                                   | `GET /pedidos/listar` usa `.all()`            | Média      |
| RNF-011 | Escalabilidade                     | SQLite local é adequado para desenvolvimento, mas limitado para produção.           | `models.py`                                   | Média      |
| RNF-012 | Portabilidade                      | Projeto deve rodar em Python 3.12.13.                                               | `.python-version`                             | Média      |
| RNF-013 | Configuração por ambiente          | URL do banco deveria ser configurável por ambiente.                                 | Banco hardcoded em `models.py`                | Média      |
| RNF-014 | Idempotência                       | Operações de status deveriam tratar chamadas repetidas.                             | Não encontrado                                | Baixa      |
| RNF-015 | Testabilidade                      | Projeto deveria ter testes automatizados.                                           | Não encontrado                                | Alta       |
| RNF-016 | Usabilidade da API                 | API deve expor documentação Swagger automática do FastAPI.                          | Inferido pelo uso de FastAPI                  | Média      |
| RNF-017 | Validação de entrada               | Quantidade e preço deveriam ter validações mínimas.                                 | Schemas aceitam tipos, mas não limites        | Alta       |
| RNF-018 | Autorização robusta                | Usuário comum não deve poder criar pedido para outro usuário nem criar conta admin. | Lacuna em `schemas.py` e `order_routes.py`    | Alta       |

---

# 9. Banco de dados e persistência

## Tipo de banco

* **Banco identificado:** SQLite
* **Arquivo:** `banco.db`
* **URL no código:** hardcoded em `models.py`
* **Migrations:** Alembic configurado em `alembic.ini` e `/alembic`

## Tabelas/modelos

### Tabela: `usuarios`

| Campo   | Tipo    | Obrigatório    | Observação                                   |
| ------- | ------- | -------------- | -------------------------------------------- |
| `id`    | Integer | Sim            | Primary key autoincrement                    |
| `nome`  | String  | Não confirmado | Nome do usuário                              |
| `email` | String  | Sim            | Não há unique constraint                     |
| `senha` | String  | Não confirmado | Hash da senha                                |
| `ativo` | Boolean | Não confirmado | Campo existe, mas não é usado nas validações |
| `admin` | Boolean | Não confirmado | Define permissão administrativa              |

### Tabela: `pedidos`

| Campo     | Tipo    | Obrigatório    | Observação                                            |
| --------- | ------- | -------------- | ----------------------------------------------------- |
| `id`      | Integer | Sim            | Primary key autoincrement                             |
| `status`  | String  | Não confirmado | Valores usados: `PENDENTE`, `CANCELADO`, `FINALIZADO` |
| `usuario` | Integer | Não confirmado | FK para `usuarios.id`                                 |
| `preco`   | Float   | Não confirmado | Total do pedido                                       |

### Tabela: `itens_pedido`

| Campo            | Tipo    | Obrigatório    | Observação                                      |
| ---------------- | ------- | -------------- | ----------------------------------------------- |
| `id`             | Integer | Sim            | Primary key autoincrement                       |
| `quantidade`     | Integer | Não confirmado | Quantidade do item                              |
| `sabor`          | String  | Não confirmado | Sabor do item; sugere domínio de pizza/delivery |
| `tamanho`        | String  | Não confirmado | Tamanho do item                                 |
| `preco_unitario` | Float   | Não confirmado | Preço unitário                                  |
| `pedido`         | Integer | Não confirmado | FK para `pedidos.id`                            |

## Relacionamentos

| Relacionamento               | Descrição                                          | Status         |
| ---------------------------- | -------------------------------------------------- | -------------- |
| `usuarios` 1:N `pedidos`     | Um usuário pode ter vários pedidos.                | Confirmado     |
| `pedidos` 1:N `itens_pedido` | Um pedido pode ter vários itens.                   | Confirmado     |
| Cascade ORM                  | `Pedido.itens` possui `cascade="all, delete"`.     | Confirmado     |
| Cascade no banco             | Não há `ON DELETE CASCADE` explícito na migration. | Não confirmado |

## Dados existentes

O arquivo `banco.db` contém dados locais:

| Tabela            | Quantidade encontrada |
| ----------------- | --------------------: |
| `usuarios`        |                     7 |
| `pedidos`         |                     2 |
| `itens_pedido`    |                     2 |
| `alembic_version` |                     1 |

Observação: o banco contém registros de usuários e hashes de senha. Valores não foram expostos por segurança.

## Migrations

* Existe migration inicial criando `usuarios`, `pedidos` e `itens_pedido`.
* Existe arquivo `.pyc` de uma possível migration adicional em `__pycache__`, mas o arquivo `.py` correspondente não foi encontrado.
* A versão registrada no banco é a migration inicial `e9b4b5830922`.

## Operações CRUD identificadas

| Entidade   | Create | Read                    | Update              | Delete         |
| ---------- | ------ | ----------------------- | ------------------- | -------------- |
| Usuário    | Sim    | Indireto no login/token | Não encontrado      | Não encontrado |
| Pedido     | Sim    | Sim                     | Sim, status e preço | Não encontrado |
| ItemPedido | Sim    | Indireto via pedido     | Não encontrado      | Sim            |

---

# 10. APIs, rotas e integrações

## APIs expostas

| Método | Rota                                            | Descrição                          | Entrada                         | Saída                             | Autenticação |
| ------ | ----------------------------------------------- | ---------------------------------- | ------------------------------- | --------------------------------- | ------------ |
| GET    | `/auth/`                                        | Rota simples de autenticação/home. | Nenhuma                         | Mensagem                          | Não          |
| POST   | `/auth/criar_conta`                             | Cria usuário.                      | `UsuarioSchema`                 | Mensagem                          | Não          |
| POST   | `/auth/login`                                   | Login por JSON.                    | `LoginSchema`                   | Access token, refresh token, tipo | Não          |
| POST   | `/auth/login-form`                              | Login via formulário OAuth2.       | `username`, `password`          | Access token, tipo                | Não          |
| GET    | `/auth/refresh`                                 | Gera novo access token.            | Bearer Token                    | Access token, tipo                | Sim          |
| GET    | `/pedidos/`                                     | Rota simples de pedidos/home.      | Bearer Token                    | Mensagem                          | Sim          |
| POST   | `/pedidos/pedido`                               | Cria pedido.                       | `PedidoSchema`                  | Mensagem com ID                   | Sim          |
| POST   | `/pedidos/pedido/cancelar/{id_pedido}`          | Cancela pedido.                    | Path param `id_pedido`          | Mensagem e pedido                 | Sim          |
| GET    | `/pedidos/listar`                               | Lista todos os pedidos.            | Bearer Token admin              | Lista de pedidos                  | Sim/admin    |
| POST   | `/pedidos/pedido/adicionar-item/{id_pedido}`    | Adiciona item ao pedido.           | Path param + `ItemPedidoSchema` | Mensagem, item ID, preço          | Sim          |
| POST   | `/pedidos/pedido/remover-item/{id_item_pedido}` | Remove item do pedido.             | Path param `id_item_pedido`     | Mensagem, quantidade, pedido      | Sim          |
| POST   | `/pedidos/pedido/finalizar/{id_pedido}`         | Finaliza pedido.                   | Path param `id_pedido`          | Mensagem e pedido                 | Sim          |
| GET    | `/pedidos/pedido/{id_pedido}`                   | Visualiza pedido.                  | Path param `id_pedido`          | Quantidade de itens e pedido      | Sim          |
| GET    | `/pedidos/listar/pedido-usuario/`               | Lista pedidos do usuário logado.   | Bearer Token                    | Lista de pedidos                  | Sim          |

## Integrações externas consumidas

| Integração                                     | Finalidade                    | Autenticação   | Arquivos relacionados | Observações                                    |
| ---------------------------------------------- | ----------------------------- | -------------- | --------------------- | ---------------------------------------------- |
| API local `http://localhost:8000/auth/refresh` | Teste manual de refresh token | Bearer Token   | `teste.py`            | Não é integração externa real; é chamada local |
| Serviços externos                              | Não encontrado                | Não encontrado | Código                | Não há consumo confirmado de APIs externas     |

---

# 11. Fluxos principais da aplicação

## Fluxo 1 — Cadastro de usuário

1. Cliente envia `POST /auth/criar_conta`.
2. API recebe `nome`, `email`, `senha`, `ativo`, `admin`.
3. Sistema consulta se já existe usuário com o mesmo email.
4. Se existir, retorna erro.
5. Se não existir, criptografa a senha.
6. Sistema cria o usuário no SQLite.
7. API retorna mensagem de sucesso.

### Exceções

* Email já cadastrado retorna `HTTPException`.
* Dados inválidos retornam validação padrão 422 do FastAPI/Pydantic.

## Fluxo 2 — Login e emissão de token

1. Cliente envia `POST /auth/login` com email e senha.
2. Sistema busca usuário pelo email.
3. Sistema valida senha com bcrypt.
4. Se credenciais forem válidas, gera access token.
5. Também gera refresh token.
6. API retorna tokens e `token_type=Bearer`.

### Exceções

* Usuário inexistente ou senha inválida retorna erro.
* Falha de configuração de `.env` pode quebrar a criação/validação de token.

## Fluxo 3 — Login via formulário OAuth2

1. Cliente envia `POST /auth/login-form`.
2. Campo `username` é interpretado como email.
3. Campo `password` é interpretado como senha.
4. Sistema autentica usuário.
5. API retorna access token.

### Uso provável

Esse fluxo alimenta o mecanismo `OAuth2PasswordBearer` usado pelo Swagger/OpenAPI do FastAPI.

## Fluxo 4 — Criar pedido

1. Cliente autenticado chama `POST /pedidos/pedido`.
2. API recebe ID do usuário no corpo.
3. Sistema cria pedido com status `PENDENTE` e preço `0`.
4. Sistema salva no banco.
5. API retorna ID do pedido criado.

### Ponto de atenção

O código não confirma que o ID do usuário no corpo pertence ao usuário autenticado.

## Fluxo 5 — Adicionar item ao pedido

1. Cliente autenticado chama `POST /pedidos/pedido/adicionar-item/{id_pedido}`.
2. Sistema busca o pedido.
3. Sistema verifica se o usuário é admin ou dono do pedido.
4. Sistema cria item com quantidade, sabor, tamanho e preço unitário.
5. Sistema recalcula o preço total do pedido.
6. API retorna item criado e preço atualizado.

### Exceções

* Pedido inexistente deveria retornar erro, mas há falha no código porque falta `raise` em um `HTTPException`.

## Fluxo 6 — Remover item do pedido

1. Cliente autenticado chama `POST /pedidos/pedido/remover-item/{id_item_pedido}`.
2. Sistema busca item.
3. Sistema busca pedido associado.
4. Sistema verifica autorização.
5. Sistema remove item.
6. Sistema recalcula preço do pedido.
7. API retorna pedido atualizado.

### Exceções

* Se o item não existir, há risco de erro 500 porque o código acessa o pedido antes de validar se o item existe.

## Fluxo 7 — Cancelar ou finalizar pedido

1. Cliente autenticado chama rota de cancelar ou finalizar.
2. Sistema busca pedido pelo ID.
3. Sistema valida se usuário é admin ou dono.
4. Sistema altera status para `CANCELADO` ou `FINALIZADO`.
5. API retorna mensagem e pedido.

## Fluxo 8 — Listar pedidos

### Listagem administrativa

1. Cliente chama `GET /pedidos/listar`.
2. Sistema identifica usuário pelo token.
3. Se usuário não for admin, retorna erro.
4. Se for admin, retorna todos os pedidos.

### Listagem do próprio usuário

1. Cliente chama `GET /pedidos/listar/pedido-usuario/`.
2. Sistema identifica usuário pelo token.
3. Sistema busca pedidos onde `Pedido.usuario == usuario.id`.
4. API retorna lista.

---

# 12. Tratamento de erros

## Exceções tratadas

| Situação                                               | Comportamento                                | Arquivo           | Status     |
| ------------------------------------------------------ | -------------------------------------------- | ----------------- | ---------- |
| Token inválido ou expirado                             | Retorna 401 com mensagem de acesso negado    | `dependencies.py` | Confirmado |
| Usuário do token não existe                            | Retorna 401                                  | `dependencies.py` | Confirmado |
| Login inválido                                         | Retorna erro de usuário não encontrado       | `auth_routes.py`  | Confirmado |
| Email já cadastrado                                    | Retorna erro                                 | `auth_routes.py`  | Confirmado |
| Pedido não encontrado em cancelar/finalizar/visualizar | Retorna 400                                  | `order_routes.py` | Confirmado |
| Usuário sem autorização                                | Retorna 401                                  | `order_routes.py` | Confirmado |
| Payload inválido                                       | FastAPI/Pydantic retorna 422 automaticamente | FastAPI           | Inferido   |

## Falhas ou inconsistências encontradas

| Problema                                                            | Onde                            | Impacto                                               |
| ------------------------------------------------------------------- | ------------------------------- | ----------------------------------------------------- |
| `HTTPException` sem `raise` ao adicionar item se pedido não existe. | `order_routes.py`               | Pode gerar erro 500 em vez de erro controlado.        |
| `HTTPException` sem `raise` ao remover item se item não existe.     | `order_routes.py`               | Pode gerar erro 500.                                  |
| `item_pedido.pedido` é acessado antes de validar se o item existe.  | `order_routes.py`               | Erro 500 em item inexistente.                         |
| Cadastro permite enviar `admin`.                                    | `schemas.py`, `auth_routes.py`  | Usuário pode se tornar admin se rota estiver pública. |
| Criar pedido aceita ID de usuário no corpo.                         | `schemas.py`, `order_routes.py` | Usuário autenticado pode criar pedido para outro ID.  |
| Status é string livre.                                              | `models.py`, `order_routes.py`  | Risco de status inválido em futuras alterações.       |
| Campo `ativo` não é verificado no login.                            | `models.py`, `auth_routes.py`   | Usuário inativo poderia autenticar.                   |
| Não há logs estruturados.                                           | Código                          | Dificulta auditoria e diagnóstico.                    |
| Não há retries.                                                     | Código                          | Falhas externas não aplicável; banco local sem retry. |

---

# 13. Testes existentes

## Framework de testes

* **pytest:** não encontrado.
* **unittest:** não encontrado.
* **Pasta `tests/`:** não encontrada.

## Arquivo de teste/manual

Existe `teste.py`, mas ele é um script manual, não um teste automatizado.

| Item               | Valor                                    |
| ------------------ | ---------------------------------------- |
| Arquivo            | `teste.py`                               |
| Biblioteca         | `requests`                               |
| Endpoint chamado   | `GET http://localhost:8000/auth/refresh` |
| Autenticação       | Bearer Token hardcoded                   |
| Resultado esperado | Imprimir JSON da resposta                |

## O que o script revela

* Existe expectativa de que `/auth/refresh` retorne um novo token.
* A aplicação deve estar rodando localmente na porta `8000`.
* O token usado no arquivo deve ser tratado como sensível.

## Cenários não cobertos

* Cadastro de usuário.
* Login com sucesso e erro.
* Criação de pedido.
* Autorização por dono/admin.
* Adição e remoção de item.
* Recalcular preço.
* Cancelamento/finalização.
* Erros de pedido inexistente.
* Expiração de token.
* Usuário inativo.
* Usuário comum tentando listar todos os pedidos.

## Como executar o teste manual

```bash
cd DeliveryFastAPI
python teste.py
```

Pré-condições:

* API rodando em `localhost:8000`.
* Token válido no script.
* Dependência `requests` instalada.

---

# 14. Segurança e dados sensíveis

## Itens sensíveis identificados

| Item                   | Onde       | Observação                                       |
| ---------------------- | ---------- | ------------------------------------------------ |
| `SECRET_KEY`           | `.env`     | Valor não exposto                                |
| Configurações de JWT   | `.env`     | Valores não expostos                             |
| Token JWT hardcoded    | `teste.py` | Valor não exposto; deve ser removido             |
| Hashes de senha        | `banco.db` | Valores não expostos                             |
| Banco com dados locais | `banco.db` | Não deveria ser publicado em repositório público |

## Autenticação

* JWT com `python-jose`.
* Bearer Token via `OAuth2PasswordBearer`.
* Login por JSON e por formulário OAuth2.
* Senha validada com bcrypt/passlib.

## Autorização

* Rotas `/pedidos` exigem token.
* Algumas operações verificam:

  * usuário admin; ou
  * usuário dono do pedido.

## Riscos identificados

| Risco                                        | Severidade       | Descrição                                            |
| -------------------------------------------- | ---------------- | ---------------------------------------------------- |
| `.env` incluído no projeto                   | Alta             | Segredos não devem ser empacotados/versionados.      |
| Token hardcoded em `teste.py`                | Alta             | Token pode permitir acesso indevido enquanto válido. |
| `banco.db` incluído                          | Alta             | Pode expor dados pessoais e hashes de senha.         |
| Cliente pode definir `admin` no cadastro     | Alta             | Escalada de privilégio.                              |
| Usuário pode criar pedido para outro usuário | Alta             | Falha de autorização.                                |
| Ausência de unique constraint em email       | Média            | Corrida/conflito pode permitir duplicidade.          |
| Ausência de política de senha                | Média            | Senhas fracas podem ser aceitas.                     |
| Campo `ativo` não usado                      | Média            | Usuário inativo continua podendo logar.              |
| Sem rate limiting                            | Média            | Login vulnerável a tentativas repetidas.             |
| Sem logs/auditoria                           | Média            | Difícil rastrear ações sensíveis.                    |
| Sem CORS explícito                           | Baixa/Média      | Depende do ambiente de consumo.                      |
| Sem HTTPS configurado                        | Alta em produção | Deve ser tratado na infraestrutura/deploy.           |

---

# 15. Requisitos para reconstruir aplicação semelhante

## Stack sugerida

* **Python:** 3.12+
* **Framework:** FastAPI
* **Banco:** SQLite para desenvolvimento; PostgreSQL recomendado para produção
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Validação:** Pydantic
* **Autenticação:** JWT com `python-jose`
* **Hash de senha:** passlib + bcrypt
* **Configuração:** `.env` + Pydantic Settings
* **Infraestrutura:** Uvicorn; opcionalmente Docker
* **Deploy:** Render, Railway, Fly.io, VPS, Azure App Service ou container

## Módulos que precisam ser criados

| Módulo             | Responsabilidade                                 | Requisitos relacionados |
| ------------------ | ------------------------------------------------ | ----------------------- |
| `main.py`          | Inicializar FastAPI e registrar routers          | RF-001 a RF-018         |
| `settings.py`      | Carregar variáveis de ambiente e configurações   | RNF-003, RNF-013        |
| `models.py`        | Definir entidades ORM                            | RF-008 a RF-012         |
| `schemas.py`       | Definir schemas de entrada/saída                 | RF-001, RF-003, RF-009  |
| `auth_routes.py`   | Rotas de cadastro/login/refresh                  | RF-001 a RF-006         |
| `order_routes.py`  | Rotas de pedidos e itens                         | RF-007 a RF-017         |
| `auth_service.py`  | Hash, autenticação, criação e validação de token | RF-002 a RF-006         |
| `order_service.py` | Regras de pedido, autorização e cálculo de preço | RF-008 a RF-017         |
| `database.py`      | Engine, sessão e base ORM                        | RNF-005                 |
| `migrations/`      | Controle de schema                               | RF-018                  |
| `tests/`           | Testes automatizados                             | RNF-015                 |

## Ordem recomendada de implementação

1. Configuração do projeto.
2. Configuração de ambiente e banco.
3. Modelagem de dados.
4. Migrations Alembic.
5. Schemas Pydantic.
6. Cadastro e login.
7. Middleware/dependências de autenticação.
8. Criação e consulta de pedidos.
9. Adição/remoção de itens.
10. Cálculo de preço.
11. Regras de autorização dono/admin.
12. Finalização/cancelamento de pedido.
13. Testes automatizados.
14. Logs e tratamento de erros.
15. Hardening de segurança.
16. Docker/deploy.

---

# 16. Backlog de implementação

| ID     | Item                                            | Tipo     | Prioridade | Critério de aceite                                                                                          |
| ------ | ----------------------------------------------- | -------- | ---------- | ----------------------------------------------------------------------------------------------------------- |
| TK-001 | Criar estrutura base FastAPI                    | Técnica  | Alta       | Dado o projeto configurado, quando executar `uvicorn main:app --reload`, então a API deve iniciar sem erro. |
| TK-002 | Configurar banco e sessão SQLAlchemy            | Técnica  | Alta       | Dado o banco configurado, quando uma rota usar sessão, então a sessão deve abrir e fechar corretamente.     |
| TK-003 | Criar modelos `Usuario`, `Pedido`, `ItemPedido` | Técnica  | Alta       | Dado Alembic executado, então as três tabelas devem existir.                                                |
| TK-004 | Criar migrations Alembic                        | Técnica  | Alta       | Dado banco vazio, quando executar `alembic upgrade head`, então o schema deve ser criado.                   |
| US-001 | Como usuário, quero criar conta                 | História | Alta       | Dado email novo, quando cadastrar, então usuário deve ser salvo com senha criptografada.                    |
| US-002 | Como usuário, quero fazer login                 | História | Alta       | Dado credenciais válidas, quando autenticar, então devo receber token Bearer.                               |
| US-003 | Como usuário autenticado, quero criar pedido    | História | Alta       | Dado token válido, quando criar pedido, então pedido deve iniciar como `PENDENTE`.                          |
| US-004 | Como usuário, quero adicionar itens ao pedido   | História | Alta       | Dado pedido meu, quando adicionar item, então preço total deve ser recalculado.                             |
| US-005 | Como usuário, quero remover item do pedido      | História | Alta       | Dado item de pedido meu, quando remover, então item deve sair e preço deve atualizar.                       |
| US-006 | Como usuário, quero visualizar meu pedido       | História | Alta       | Dado pedido meu, quando consultar, então devo ver pedido e itens.                                           |
| US-007 | Como usuário, quero listar meus pedidos         | História | Alta       | Dado token válido, quando listar, então só meus pedidos devem aparecer.                                     |
| US-008 | Como admin, quero listar todos os pedidos       | História | Média      | Dado usuário admin, quando listar todos, então todos os pedidos devem ser retornados.                       |
| US-009 | Como usuário, quero cancelar pedido             | História | Média      | Dado pedido meu, quando cancelar, então status deve virar `CANCELADO`.                                      |
| US-010 | Como usuário, quero finalizar pedido            | História | Média      | Dado pedido meu, quando finalizar, então status deve virar `FINALIZADO`.                                    |
| TK-005 | Corrigir autorização no cadastro                | Técnica  | Alta       | Usuário público não deve conseguir criar conta admin livremente.                                            |
| TK-006 | Corrigir criação de pedido                      | Técnica  | Alta       | Pedido deve ser criado para o usuário autenticado, não para ID arbitrário enviado no body.                  |
| TK-007 | Adicionar validações de item                    | Técnica  | Alta       | Quantidade e preço devem ser positivos.                                                                     |
| TK-008 | Adicionar testes automatizados                  | Técnica  | Alta       | Fluxos principais devem passar em pytest.                                                                   |
| TK-009 | Remover segredos do repositório                 | Técnica  | Alta       | `.env`, tokens e banco local não devem estar versionados.                                                   |
| TK-010 | Criar `.env.example`                            | Técnica  | Média      | Arquivo deve listar variáveis sem valores reais.                                                            |
| TK-011 | Adicionar logs estruturados                     | Técnica  | Média      | Erros e operações sensíveis devem gerar logs.                                                               |
| TK-012 | Adicionar paginação em listagens                | Técnica  | Média      | Listagens devem aceitar `limit` e `offset` ou paginação equivalente.                                        |

---

# 17. Critérios de aceite gerais

* Deve executar com `uvicorn main:app --reload` a partir da pasta do projeto.
* Deve expor documentação automática em `/docs`.
* Deve permitir cadastro de usuário com senha criptografada.
* Deve impedir cadastro duplicado por email.
* Deve autenticar usuário por email e senha.
* Deve retornar token JWT em login bem-sucedido.
* Deve bloquear acesso às rotas de pedidos sem Bearer Token.
* Deve criar pedido com status inicial `PENDENTE`.
* Deve associar pedido ao usuário correto.
* Deve permitir adicionar item com quantidade, sabor, tamanho e preço unitário.
* Deve recalcular preço total após adicionar item.
* Deve recalcular preço total após remover item.
* Deve permitir visualizar pedido apenas se usuário for dono ou admin.
* Deve permitir cancelar/finalizar pedido apenas se usuário for dono ou admin.
* Deve permitir admin listar todos os pedidos.
* Deve permitir usuário comum listar apenas os próprios pedidos.
* Deve tratar token inválido com HTTP 401.
* Deve tratar pedido inexistente com erro controlado, não erro 500.
* Deve tratar item inexistente com erro controlado, não erro 500.
* Deve possuir migrations reproduzíveis.
* Deve possuir testes automatizados para autenticação, autorização e pedidos.
* Não deve conter `.env`, tokens reais ou banco com dados reais versionados.
* Deve ter `.env.example` com nomes das variáveis necessárias.
* Deve registrar logs mínimos de erro e operações relevantes.

---

# 18. Lacunas e dúvidas

| Item                | Dúvida                                                             | Impacto                                | Como confirmar                                 |
| ------------------- | ------------------------------------------------------------------ | -------------------------------------- | ---------------------------------------------- |
| Domínio exato       | A aplicação é especificamente de pizza ou delivery genérico?       | Afeta nomes de entidades e validações. | Confirmar com Product Owner ou README ausente. |
| Cardápio/produtos   | Há produtos cadastráveis ou os itens são livres?                   | Afeta modelagem.                       | Definir requisito de catálogo.                 |
| Preço unitário      | O preço deve ser informado pelo cliente ou calculado pelo sistema? | Alto risco de fraude.                  | Definir regra de negócio.                      |
| Criação de admin    | Quem pode criar usuários administradores?                          | Segurança crítica.                     | Definir fluxo administrativo.                  |
| Usuário ativo       | Usuário inativo deve poder logar?                                  | Segurança e operação.                  | Definir regra de autenticação.                 |
| Status do pedido    | Quais status são permitidos e quais transições são válidas?        | Afeta workflow.                        | Criar enum e matriz de transição.              |
| Endereço de entrega | Não há endereço no pedido.                                         | Aplicação de delivery fica incompleta. | Definir dados de entrega.                      |
| Pagamento           | Não há pagamento.                                                  | Fluxo de delivery incompleto.          | Definir se haverá integração de pagamento.     |
| Restaurante/loja    | Não há entidade loja/restaurante.                                  | Limita multiestabelecimento.           | Confirmar escopo.                              |
| Deploy              | Não há Dockerfile ou configuração de produção.                     | Afeta implantação.                     | Definir ambiente alvo.                         |
| Testes              | Não há testes automatizados.                                       | Risco de regressão.                    | Implementar suíte mínima.                      |
| Banco de produção   | SQLite é suficiente?                                               | Escalabilidade e concorrência.         | Definir volume esperado.                       |
| Logs/auditoria      | Não há logs estruturados.                                          | Dificulta suporte.                     | Definir requisitos de observabilidade.         |
| Refresh token       | Não há tipo de token, rotação ou revogação.                        | Segurança.                             | Definir política de sessão.                    |
| Migration ausente   | Há `.pyc` de possível migration sem `.py`.                         | Pode indicar histórico incompleto.     | Revisar repositório original.                  |
| README vazio        | Não há documentação operacional.                                   | Dificulta instalação e manutenção.     | Criar README.                                  |

---

# 19. Resumo executivo

* **O que a aplicação faz:**
  É uma API FastAPI para cadastro/login de usuários e gerenciamento básico de pedidos de delivery. Permite criar pedidos, adicionar/remover itens, recalcular preço, visualizar, listar, cancelar e finalizar pedidos. Usa autenticação JWT e persistência em SQLite.

* **O que é essencial reconstruir:**
  Autenticação JWT, modelos `Usuario`, `Pedido` e `ItemPedido`, rotas de pedidos protegidas, regra de dono/admin, cálculo do preço por itens, migrations e configuração de ambiente.

* **O que é opcional:**
  `teste.py`, banco SQLite com dados locais, arquivos `__pycache__`, metadados `.git`, uso do `uv.lock` se o projeto for reconstruído com outro gerenciador.

* **Principais riscos:**
  `.env`, token e banco incluídos no projeto; criação de admin pelo próprio payload; criação de pedido para usuário arbitrário; ausência de testes; ausência de validações fortes; tratamento de erro incompleto; README vazio; banco hardcoded.

* **Esforço estimado:**
  **Pequeno** para reconstruir uma versão equivalente básica.
  **Médio** para reconstruir com segurança, testes, validações, logs e preparação mínima para produção.

* **Complexidade estimada:**
  **Baixa a média.**
  A lógica atual é simples, mas os ajustes de segurança/autorização e organização arquitetural exigem atenção para evitar reproduzir fragilidades do projeto original.
