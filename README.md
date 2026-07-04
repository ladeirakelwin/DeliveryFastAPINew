# 1. Resumo do projeto analisado

* **Nome provável do projeto:** `DeliveryFastAPINew`
* **Tipo de aplicação:** API REST simples de delivery/pedidos.
* **Framework:** FastAPI.
* **Banco de dados:** SQLite local via `base.db`, configurado por `DATABASE_URL` no `.env`.
* **Principais dependências:** `fastapi[standard]`, `sqlalchemy`, `alembic`, `pydantic`, `pyjwt`, `python-jose`, `python-dotenv`, `pwdlib`, `passlib`, `uvicorn`, `requests`, `sqlalchemy-utils`.
* **Estrutura geral:**

  * `main.py`
  * `routes/auth.py`
  * `routes/orders.py`
  * `services/auth_service.py`
  * `services/usuario_service.py`
  * `services/pedido_service.py`
  * `models.py`
  * `schemas.py`
  * `database.py`
  * `dependencies.py`
  * `utils/senha.py`
  * `alembic/`
* **Existe Docker?** Não.
* **Existe teste?** Não há pasta `tests/` nem testes automatizados.
* **Existe autenticação?** Sim, com Bearer Token/JWT.
* **Existe documentação?** Sim, há `README.md`, mas ele está parcialmente desatualizado em relação ao código atual.
* **Estado atual em 5 a 10 linhas:**

A aplicação já tem uma base boa para estudo: usa FastAPI, routers, camada de services, SQLAlchemy 2.x, Alembic, Pydantic e autenticação com JWT. As rotas principais permitem criar conta, fazer login, gerar refresh token, criar pedido, adicionar/remover item, finalizar/cancelar pedido e listar pedidos. O projeto ainda não está pronto para deploy profissional porque não tem Dockerfile, health check, testes automatizados, CI/CD, logs mínimos estruturados e `.env.example`. Há pontos de segurança importantes: o cadastro permite enviar `admin`, o refresh token pode ser aceito como token de acesso nas rotas protegidas, e o `.env` foi incluído no `.zip` enviado, embora não pareça estar versionado no Git. Também há bugs de regra de negócio e inconsistências: busca de usuário por `nome` em vez de `email`, expiração de token calculada na definição da classe, tipos inconsistentes no model de itens e rotas com prefixo duplicado.

---

# 2. Diagnóstico geral

| Área         | Situação atual | Risco | Observação                                                                                                                             |
| ------------ | -------------: | ----: | -------------------------------------------------------------------------------------------------------------------------------------- |
| Organização  |          Média | Médio | Há separação em `routes/`, `services/`, `models.py` e `schemas.py`, mas ainda falta padronização de nomes, config e responsabilidades. |
| Validação    |    Média/Fraca | Médio | Usa Pydantic, mas faltam `EmailStr`, validações de quantidade/preço/senha e schemas separados para criação/retorno/admin.              |
| Banco        |          Média | Médio | SQLAlchemy e Alembic existem, mas há tipo incorreto em `quantidade`, transações sem rollback e SQLite local incluído no pacote.        |
| Testes       |          Fraca |  Alto | Não há testes automatizados para login, autorização, pedidos, erros e banco.                                                           |
| Segurança    |          Fraca |  Alto | Cadastro aceita `admin`, refresh token pode autenticar rotas protegidas, `.env` veio no zip e faltam validações fortes.                |
| Documentação |          Média | Médio | README existe, mas está inconsistente com a estrutura real do projeto e com as rotas atuais.                                           |
| Deploy       |          Fraca |  Alto | Sem Dockerfile, sem health check, sem logs, sem comando claro de produção e sem separação segura de ambiente.                          |

---

# 3. Requisitos de melhoria

## RM-001 — Corrigir identificação do usuário por email no cadastro e login

* **Categoria:** Segurança / Autenticação / Banco
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** O método `_obtendo_usuario` recebe um parâmetro genérico, mas busca por `Usuario.nome`. No cadastro, ele é chamado passando `email`, o que faz a verificação de duplicidade ficar inconsistente. No login, o `username` do formulário acaba sendo tratado como nome, não email.
* **Por que melhorar:** Login e cadastro precisam usar um identificador claro e único. O email já está marcado como `unique=True`, então deve ser o principal identificador.
* **Requisito de melhoria:** “O sistema deve autenticar e localizar usuários pelo email, mantendo o email como identificador único de conta.”
* **Como aplicar de forma simples:**

  1. Renomear `_obtendo_usuario` para `_obter_usuario_por_email`.
  2. Alterar o filtro para `Usuario.email == email`.
  3. Ajustar `autenticar_usuario` para receber `email`.
  4. No login, considerar `form_data.username` como email.
  5. Manter `Usuario.nome` apenas como dado de exibição.
* **Critério de aceite:** Um usuário cadastrado com email consegue fazer login usando esse email; tentativa de cadastrar email repetido retorna erro 409 controlado.
* **Arquivos provavelmente envolvidos:** `services/usuario_service.py`, `routes/auth.py`, `schemas.py`.
* **O que evitar:** Não usar `nome` como identificador de login se ele não for único.
* **Fonte do porquê:** A própria documentação do FastAPI usa fluxos OAuth2/JWT com identificação clara do usuário e validação de credenciais antes de emitir tokens. ([FastAPI][1])
* **Referências de estudo:**

  * Inglês: FastAPI — OAuth2 with Password and JWT.
  * Português: FastAPI em português — segurança e autenticação, quando disponível.

---

## RM-002 — Impedir criação pública de usuário administrador

* **Categoria:** Segurança
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** O schema de criação de usuário aceita o campo `admin`, e a rota pública `/auth/criar-conta` repassa esse valor para o banco.
* **Por que melhorar:** Um usuário comum não deve conseguir se tornar administrador apenas enviando `"admin": true` no corpo da requisição.
* **Requisito de melhoria:** “O sistema deve impedir que usuários criem contas administrativas pela rota pública de cadastro.”
* **Como aplicar de forma simples:**

  1. Criar `UsuarioCreateSchema` sem o campo `admin`.
  2. No service, definir `admin=False` por padrão.
  3. Criar conta admin apenas manualmente, por seed controlado ou rota protegida para admin.
* **Critério de aceite:** Mesmo que o cliente envie `admin: true`, o usuário criado continua com `admin=False`.
* **Arquivos provavelmente envolvidos:** `schemas.py`, `routes/auth.py`, `services/usuario_service.py`.
* **O que evitar:** Não confiar em campos sensíveis vindos diretamente do cliente.
* **Fonte do porquê:** A OWASP classifica exposição/alteração indevida de propriedades sensíveis como risco de autorização em APIs, especialmente quando o cliente consegue manipular campos internos. ([OWASP][2])
* **Referências de estudo:**

  * Inglês: OWASP API3:2023 — Broken Object Property Level Authorization.
  * Português: OWASP API Security Top 10, quando houver tradução confiável.

---

## RM-003 — Diferenciar access token e refresh token nas rotas protegidas

* **Categoria:** Segurança / Autenticação
* **Prioridade:** Alta
* **Dificuldade:** Média
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** O token carrega `"type": "access"` ou `"type": "refresh"`, mas `obter_usuario_atual` não valida se o token usado nas rotas protegidas é realmente do tipo `access`.
* **Por que melhorar:** Refresh token deve servir apenas para renovar tokens, não para acessar endpoints protegidos.
* **Requisito de melhoria:** “O sistema deve aceitar apenas access token em rotas protegidas e aceitar refresh token somente na rota de renovação.”
* **Como aplicar de forma simples:**

  1. Em `obter_usuario_atual`, decodificar o token.
  2. Verificar `payload.get("type") == "access"`.
  3. Se for `refresh`, retornar 401.
  4. Na rota `/auth/refresh`, validar `type == "refresh"`.
* **Critério de aceite:** Usar refresh token em `/pedidos/listar` retorna 401; usar access token válido funciona.
* **Arquivos provavelmente envolvidos:** `services/auth_service.py`, `services/usuario_service.py`, `routes/auth.py`.
* **O que evitar:** Não tratar access token e refresh token como equivalentes.
* **Fonte do porquê:** A documentação do FastAPI mostra uso de JWT assinado e com expiração para autenticação; a OWASP reforça que fluxos de autenticação precisam ser bem compreendidos e padronizados. ([FastAPI][1]) ([OWASP][3])
* **Referências de estudo:**

  * Inglês: FastAPI OAuth2/JWT; OWASP API2:2023 Broken Authentication.
  * Português: Auth0 Brasil — JWT em Python.

---

## RM-004 — Calcular expiração do token no momento da criação

* **Categoria:** Segurança / Autenticação
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** `expiracao_token` e `refresh_expiracao_token` são atributos de classe calculados quando a classe `AuthService` é carregada, não quando cada token é criado.
* **Por que melhorar:** Depois de algum tempo de aplicação no ar, novos tokens podem nascer com expiração antiga.
* **Requisito de melhoria:** “O sistema deve calcular a expiração de cada token no momento exato em que o token é criado.”
* **Como aplicar de forma simples:**

  1. Remover `expiracao_token` e `refresh_expiracao_token` como atributos de classe.
  2. Dentro de `criar_token`, calcular `datetime.now(timezone.utc) + timedelta(...)`.
  3. Criar testes para confirmar que dois tokens emitidos em momentos diferentes têm `exp` diferente.
* **Critério de aceite:** Um token gerado agora recebe expiração futura correta, mesmo que a aplicação esteja rodando há horas.
* **Arquivos provavelmente envolvidos:** `services/auth_service.py`, testes futuros.
* **O que evitar:** Não usar datas dinâmicas como atributo estático de classe.
* **Fonte do porquê:** JWT usa claims assinadas e expiração para limitar validade do token; a documentação do FastAPI explica que a expiração é parte importante do fluxo de segurança. ([FastAPI][1])
* **Referências de estudo:**

  * Inglês: FastAPI OAuth2/JWT; PyJWT documentation.
  * Português: Auth0 Brasil — JWT em Python.

---

## RM-005 — Tratar exceções de token expirado ou inválido de forma padronizada

* **Categoria:** Segurança / Tratamento de erros
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** `AuthService.decodificar_token` chama `jwt.decode`, mas nem sempre as exceções de token expirado/inválido são capturadas no ponto correto. A rota `/auth/refresh` pode devolver erro não padronizado.
* **Por que melhorar:** A API deve retornar 401 previsível, sem stack trace e sem detalhes internos.
* **Requisito de melhoria:** “O sistema deve retornar erro 401 padronizado para token inválido, expirado ou de tipo incorreto.”
* **Como aplicar de forma simples:**

  1. Capturar exceções do PyJWT, como token expirado e token inválido.
  2. Retornar `HTTPException(status_code=401, detail="Token inválido ou expirado")`.
  3. Aplicar o mesmo padrão em access e refresh.
* **Critério de aceite:** Token expirado, token malformado e refresh token usado no lugar errado retornam 401.
* **Arquivos provavelmente envolvidos:** `services/auth_service.py`, `services/usuario_service.py`.
* **O que evitar:** Não usar `except Exception` genérico sem log e sem tratamento específico.
* **Fonte do porquê:** PyJWT é a biblioteca usada para codificar/decodificar JWT, e JWT é um padrão de claims assinadas entre partes. ([pyjwt.readthedocs.io][4])
* **Referências de estudo:**

  * Inglês: PyJWT documentation.
  * Português: Auth0 Brasil — Como lidar com JWTs em Python.

---

## RM-006 — Criar schemas separados para criação, resposta e administração de usuário

* **Categoria:** Validação / Segurança
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** `UsuarioSchema` recebe `senha`, `ativo` e `admin`. `UsuarioResponseSchema` remove a senha, o que é bom, mas o schema de entrada ainda permite campos sensíveis.
* **Por que melhorar:** Schemas separados reduzem risco de mass assignment e deixam claro o que o cliente pode enviar.
* **Requisito de melhoria:** “O sistema deve possuir schemas específicos para entrada pública, resposta pública e operações administrativas.”
* **Como aplicar de forma simples:**

  1. Criar `UsuarioCreateSchema` com `nome`, `email`, `senha`.
  2. Criar `UsuarioResponseSchema` com `id`, `nome`, `email`, `ativo`.
  3. Criar `UsuarioAdminUpdateSchema` futuramente, apenas se houver rota admin.
* **Critério de aceite:** A rota pública de cadastro não aceita `admin` nem depende de `ativo`.
* **Arquivos provavelmente envolvidos:** `schemas.py`, `routes/auth.py`.
* **O que evitar:** Não reutilizar o mesmo schema para todos os casos.
* **Fonte do porquê:** Pydantic é usado para declarar e validar a forma dos dados por tipos Python, o que favorece contratos claros de entrada e saída. ([pydantic.dev][5])
* **Referências de estudo:**

  * Inglês: Pydantic documentation; FastAPI Request Body.
  * Português: FastAPI em português — Corpo da requisição.

---

## RM-007 — Validar email, senha, quantidade e preço

* **Categoria:** Validação de dados
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** `email` é `str`, senha aceita qualquer string, `quantidade` e `preco_unitario` não têm validações mínimas.
* **Por que melhorar:** Evita dados inválidos no banco, como email malformado, preço negativo ou quantidade zero.
* **Requisito de melhoria:** “O sistema deve validar os dados de entrada antes de salvar no banco.”
* **Como aplicar de forma simples:**

  1. Usar `EmailStr` para email.
  2. Definir senha com tamanho mínimo.
  3. Usar `Field(gt=0)` para `quantidade`.
  4. Usar `Field(ge=0)` ou `Field(gt=0)` para `preco_unitario`.
  5. Validar tamanho/sabor com tamanho mínimo e máximo.
* **Critério de aceite:** Requisições com email inválido, quantidade negativa ou preço negativo retornam 422.
* **Arquivos provavelmente envolvidos:** `schemas.py`.
* **O que evitar:** Não validar regra de negócio apenas no front-end.
* **Fonte do porquê:** Pydantic valida dados a partir de tipos e campos declarados, e FastAPI usa esses schemas para validar entradas automaticamente. ([pydantic.dev][5])
* **Referências de estudo:**

  * Inglês: Pydantic Fields and Validators.
  * Português: FastAPI em português — Validação de dados.

---

## RM-008 — Corrigir tipo da coluna `quantidade`

* **Categoria:** Banco / Modelagem
* **Prioridade:** Alta
* **Dificuldade:** Média
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** Em `models.py`, `quantidade` está anotado como `Mapped[int]`, mas a coluna foi criada como `String`.
* **Por que melhorar:** Quantidade é número inteiro. Guardar como texto obriga conversões e aumenta risco de erro.
* **Requisito de melhoria:** “O sistema deve armazenar quantidade de item como inteiro no banco de dados.”
* **Como aplicar de forma simples:**

  1. Alterar `mapped_column(String)` para `mapped_column(Integer)`.
  2. Criar migration Alembic.
  3. Em SQLite, revisar a migration porque alterações de tipo podem exigir `batch_alter_table`.
  4. Testar criação de item e cálculo de preço.
* **Critério de aceite:** A coluna `ItensPedidos.quantidade` fica como inteiro e o cálculo do pedido não precisa converter `int(item.quantidade)`.
* **Arquivos provavelmente envolvidos:** `models.py`, `alembic/versions/`, `services/pedido_service.py`.
* **O que evitar:** Não alterar banco manualmente sem migration.
* **Fonte do porquê:** SQLAlchemy 2.x documenta o uso moderno de `Mapped`, `mapped_column` e relacionamentos declarativos tipados. ([docs.sqlalchemy.org][6])
* **Referências de estudo:**

  * Inglês: SQLAlchemy 2.0 ORM Mapped Classes; Alembic autogenerate.
  * Português: Artigos introdutórios sobre SQLAlchemy 2.x e Alembic.

---

## RM-009 — Adicionar rollback em operações de escrita no banco

* **Categoria:** Banco / Tratamento de erros
* **Prioridade:** Alta
* **Dificuldade:** Média
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** Os services usam `commit()`, mas em caso de erro não há `rollback()`. Em alguns pontos há `except Exception` retornando erro genérico.
* **Por que melhorar:** Depois de falha em transação, a sessão pode ficar em estado inconsistente.
* **Requisito de melhoria:** “O sistema deve executar rollback em operações de escrita quando ocorrer erro antes ou durante o commit.”
* **Como aplicar de forma simples:**

  1. Em cada `try` de escrita, no `except`, chamar `self.db.rollback()`.
  2. Capturar exceções esperadas, como erro de integridade.
  3. Retornar erro controlado.
  4. Criar teste de email duplicado.
* **Critério de aceite:** Um erro de banco não quebra as próximas operações usando a sessão.
* **Arquivos provavelmente envolvidos:** `services/usuario_service.py`, `services/pedido_service.py`.
* **O que evitar:** Não esconder todos os erros com `except Exception` sem rollback e sem log.
* **Fonte do porquê:** A documentação do SQLAlchemy descreve `rollback()` como forma de reverter a transação atual e liberar recursos de conexão. ([docs.sqlalchemy.org][7])
* **Referências de estudo:**

  * Inglês: SQLAlchemy Session Basics.
  * Português: Tutoriais de SQLAlchemy Session.

---

## RM-010 — Corrigir rotas duplicadas e padronizar URLs

* **Categoria:** Organização / API Design
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Médio
* **Status:** Confirmado pelo código
* **Problema identificado:** O router de pedidos já tem `prefix="/pedidos"`, mas algumas rotas incluem novamente `/pedidos/pedido/...`, gerando caminhos como `/pedidos/pedidos/pedido/finalizar/{id_pedido}`.
* **Por que melhorar:** URLs inconsistentes confundem quem usa a API e dificultam documentação/testes.
* **Requisito de melhoria:** “O sistema deve expor rotas de pedidos com padrão simples e sem prefixos duplicados.”
* **Como aplicar de forma simples:**

  1. Manter `prefix="/pedidos"`.
  2. Alterar finalizar para `PUT /pedido/{id_pedido}/finalizar` ou `PUT /{id_pedido}/finalizar`.
  3. Alterar cancelar para padrão equivalente.
  4. Atualizar README e testes.
* **Critério de aceite:** O Swagger mostra rotas sem duplicação de `/pedidos/pedidos`.
* **Arquivos provavelmente envolvidos:** `routes/orders.py`, `README.md`, testes.
* **O que evitar:** Não misturar singular/plural sem padrão.
* **Fonte do porquê:** FastAPI recomenda organizar aplicações com `APIRouter` e `include_router`, usando prefixos para agrupar rotas. ([FastAPI][8])
* **Referências de estudo:**

  * Inglês: FastAPI Bigger Applications.
  * Português: FastAPI — Aplicações Maiores.

---

## RM-011 — Criar endpoint `/health`

* **Categoria:** Observabilidade / Deploy
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** Não existe endpoint de health check.
* **Por que melhorar:** Plataformas de deploy usam health check para saber se a aplicação está viva.
* **Requisito de melhoria:** “O sistema deve expor um endpoint `/health` simples para verificar disponibilidade.”
* **Como aplicar de forma simples:**

  1. Em `main.py`, adicionar `GET /health`.
  2. Retornar `{"status": "ok"}`.
  3. Opcionalmente, testar conexão com banco em `/health/db`.
* **Critério de aceite:** `GET /health` retorna HTTP 200 sem autenticação.
* **Arquivos provavelmente envolvidos:** `main.py`.
* **O que evitar:** Não colocar lógica pesada no health check simples.
* **Fonte do porquê:** Render permite configurar health check path em serviços web, e deploys profissionais costumam depender desse tipo de endpoint. ([Render][9])
* **Referências de estudo:**

  * Inglês: Render Web Services; FastAPI Deployment.
  * Português: Guias de deploy FastAPI em PaaS.

---

## RM-012 — Criar `.env.example` e remover segredos do pacote compartilhável

* **Categoria:** Configuração / Segurança / Deploy
* **Prioridade:** Alta
* **Dificuldade:** Fácil
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** O `.zip` contém `.env` com segredos reais. Também contém `base.db` com dados locais.
* **Por que melhorar:** Segredos e bancos locais não devem ser compartilhados em pacotes de projeto.
* **Requisito de melhoria:** “O sistema deve possuir `.env.example` sem valores reais e não deve distribuir `.env` nem banco local com dados.”
* **Como aplicar de forma simples:**

  1. Criar `.env.example`.
  2. Manter `.env` no `.gitignore`.
  3. Remover `.env` de zips futuros.
  4. Remover `base.db` de zips futuros ou criar banco vazio via Alembic.
  5. Regenerar `SECRET_KEY`, pois a chave foi exposta no pacote enviado.
* **Critério de aceite:** O repositório/pacote não contém `.env` real, token real nem banco com dados locais.
* **Arquivos provavelmente envolvidos:** `.env.example`, `.gitignore`, README.
* **O que evitar:** Não colocar segredo real em README, teste, print ou zip.
* **Fonte do porquê:** Twelve-Factor recomenda armazenar configuração em variáveis de ambiente, evitando config acoplada ao código e reduzindo risco de vazamento em repositórios. ([Twelve-Factor App][10])
* **Referências de estudo:**

  * Inglês: The Twelve-Factor App — Config.
  * Português: Materiais sobre variáveis de ambiente em Python/FastAPI.

---

## RM-013 — Centralizar configurações com Pydantic Settings

* **Categoria:** Configuração
* **Prioridade:** Média
* **Dificuldade:** Média
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** `dependencies.py` carrega variáveis com `os.getenv`, mas não valida obrigatoriedade de `SECRET_KEY`, `DATABASE_URL` e `ALGORITHM`.
* **Por que melhorar:** Configuração tipada evita aplicação subir com variável ausente ou inválida.
* **Requisito de melhoria:** “O sistema deve centralizar configurações em uma classe `Settings` tipada e validada.”
* **Como aplicar de forma simples:**

  1. Criar `settings.py`.
  2. Usar `pydantic-settings`.
  3. Definir campos obrigatórios: `database_url`, `secret_key`, `algorithm`.
  4. Usar `@lru_cache` para carregar uma vez.
  5. Trocar imports diretos de `dependencies.py`.
* **Critério de aceite:** Se `SECRET_KEY` estiver ausente, a aplicação falha ao iniciar com erro claro.
* **Arquivos provavelmente envolvidos:** `settings.py`, `dependencies.py`, `database.py`, `alembic/env.py`.
* **O que evitar:** Não espalhar `os.getenv` por vários arquivos.
* **Fonte do porquê:** A documentação do FastAPI recomenda Pydantic Settings para lidar com configurações, `.env` e testes de forma organizada. ([FastAPI][11])
* **Referências de estudo:**

  * Inglês: FastAPI Settings and Environment Variables.
  * Português: FastAPI em português — Configurações, quando disponível.

---

## RM-014 — Tornar `connect_args` compatível com outros bancos

* **Categoria:** Banco / Deploy
* **Prioridade:** Média
* **Dificuldade:** Fácil
* **Impacto:** Médio
* **Status:** Confirmado pelo código
* **Problema identificado:** `create_engine` sempre usa `connect_args={"check_same_thread": False}`, opção específica para SQLite.
* **Por que melhorar:** Em deploy com PostgreSQL, essa configuração não faz sentido e pode gerar erro.
* **Requisito de melhoria:** “O sistema deve aplicar configurações específicas de engine apenas quando o banco for SQLite.”
* **Como aplicar de forma simples:**

  1. Verificar se `DATABASE_URL.startswith("sqlite")`.
  2. Usar `connect_args` apenas nesse caso.
  3. Para PostgreSQL, criar engine sem esse argumento.
* **Critério de aceite:** A aplicação inicia com SQLite local e também com PostgreSQL via `DATABASE_URL`.
* **Arquivos provavelmente envolvidos:** `database.py`, `settings.py`.
* **O que evitar:** Não deixar configuração local travar produção.
* **Fonte do porquê:** A estratégia Twelve-Factor favorece que a mesma aplicação rode em diferentes deploys apenas trocando variáveis de ambiente. ([Twelve-Factor App][10])
* **Referências de estudo:**

  * Inglês: SQLAlchemy Engine Configuration; Twelve-Factor App.
  * Português: Tutoriais de SQLAlchemy com PostgreSQL.

---

## RM-015 — Adicionar testes automatizados com pytest e TestClient

* **Categoria:** Testes
* **Prioridade:** Alta
* **Dificuldade:** Média
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** Não há testes automatizados.
* **Por que melhorar:** Sem testes, qualquer correção em autenticação, pedidos ou banco pode quebrar fluxos existentes sem aviso.
* **Requisito de melhoria:** “O sistema deve possuir testes automatizados dos principais fluxos da API.”
* **Como aplicar de forma simples:**

  1. Criar pasta `tests/`.
  2. Adicionar `pytest` e `httpx` como dependências de desenvolvimento.
  3. Criar fixture de banco de teste.
  4. Testar cadastro, login, criação de pedido, adicionar item, remover item, autorização e erros.
* **Critério de aceite:** Rodar `pytest` executa testes principais com sucesso.
* **Arquivos provavelmente envolvidos:** `tests/`, `pyproject.toml`, `database.py`.
* **O que evitar:** Não testar usando banco real `base.db`.
* **Fonte do porquê:** A documentação do FastAPI mostra uso direto de `pytest` e `TestClient` para testar APIs de forma simples. ([FastAPI][12])
* **Referências de estudo:**

  * Inglês: FastAPI Testing; pytest fixtures.
  * Português: Tutoriais de pytest para FastAPI.

---

## RM-016 — Padronizar erros de domínio

* **Categoria:** Tratamento de erros
* **Prioridade:** Média
* **Dificuldade:** Média
* **Impacto:** Médio
* **Status:** Confirmado pelo código
* **Problema identificado:** Existem `HTTPException` espalhadas nos services, algumas genéricas, e alguns `except Exception` escondem a causa.
* **Por que melhorar:** Erros previsíveis deixam a API mais fácil de consumir e testar.
* **Requisito de melhoria:** “O sistema deve retornar erros HTTP padronizados para recursos inexistentes, acesso negado, duplicidade e falha de validação.”
* **Como aplicar de forma simples:**

  1. Criar mensagens consistentes.
  2. Evitar `except Exception` sem necessidade.
  3. Tratar erro de integridade de email duplicado como 409.
  4. Criar testes para cada erro esperado.
* **Critério de aceite:** Pedido inexistente retorna 404; usuário sem permissão retorna 403; email duplicado retorna 409.
* **Arquivos provavelmente envolvidos:** `services/*.py`, `routes/*.py`, testes.
* **O que evitar:** Não retornar 500 para erro conhecido do usuário.
* **Fonte do porquê:** FastAPI usa `HTTPException` para retornar erros HTTP controlados em path operations. ([FastAPI][13])
* **Referências de estudo:**

  * Inglês: FastAPI Handling Errors.
  * Português: FastAPI em português — Tratamento de erros.

---

## RM-017 — Adicionar logs básicos

* **Categoria:** Observabilidade
* **Prioridade:** Média
* **Dificuldade:** Fácil
* **Impacto:** Médio
* **Status:** Confirmado pelo código
* **Problema identificado:** Não há logging explícito da aplicação.
* **Por que melhorar:** Em deploy, logs são a primeira forma de entender falhas.
* **Requisito de melhoria:** “O sistema deve registrar logs básicos de inicialização, erros e operações relevantes.”
* **Como aplicar de forma simples:**

  1. Configurar `logging` padrão do Python.
  2. Registrar erro antes de devolver 500.
  3. Não logar senha, token nem segredo.
  4. Em deploy, usar stdout/stderr.
* **Critério de aceite:** Erros internos aparecem no log sem expor dados sensíveis.
* **Arquivos provavelmente envolvidos:** `main.py`, `services/*.py`, `settings.py`.
* **O que evitar:** Não logar corpo completo de login.
* **Fonte do porquê:** Plataformas como Render expõem logs e dependem de comando de start/serviço configurado corretamente; logs em stdout ajudam na operação básica. ([Render][9])
* **Referências de estudo:**

  * Inglês: Python logging documentation; Render Web Services.
  * Português: Tutoriais de logging em Python.

---

## RM-018 — Adicionar paginação em listagem de pedidos

* **Categoria:** Performance / API Design
* **Prioridade:** Média
* **Dificuldade:** Fácil
* **Impacto:** Médio
* **Status:** Confirmado pelo código
* **Problema identificado:** `listar_todos_pedidos` retorna todos os pedidos sem limite.
* **Por que melhorar:** Com crescimento do banco, a listagem pode ficar lenta e pesada.
* **Requisito de melhoria:** “O sistema deve permitir paginação nas listagens de pedidos.”
* **Como aplicar de forma simples:**

  1. Adicionar query params `limit` e `offset`.
  2. Definir limite máximo, por exemplo 100.
  3. Aplicar `.limit(limit).offset(offset)` na query.
  4. Atualizar schema de resposta se quiser incluir total futuramente.
* **Critério de aceite:** `GET /pedidos/listar?limit=10&offset=0` retorna no máximo 10 pedidos.
* **Arquivos provavelmente envolvidos:** `routes/orders.py`, `services/pedido_service.py`.
* **O que evitar:** Não adicionar paginação complexa com cursor agora.
* **Fonte do porquê:** SQLAlchemy permite construir consultas legíveis com `select`, e paginação simples por limite/offset é suficiente para projeto pequeno. ([docs.sqlalchemy.org][14])
* **Referências de estudo:**

  * Inglês: SQLAlchemy querying/select.
  * Português: Tutoriais SQLAlchemy select, limit e offset.

---

## RM-019 — Limpar dependências e padronizar gerenciador de pacote

* **Categoria:** Experiência de desenvolvimento / Qualidade
* **Prioridade:** Média
* **Dificuldade:** Fácil
* **Impacto:** Médio
* **Status:** Confirmado pelo código
* **Problema identificado:** O projeto usa `pyproject.toml` e `uv.lock`, mas há dependências possivelmente redundantes: `pyjwt` e `python-jose`; `pwdlib` e `passlib`; `requests` sem teste automatizado.
* **Por que melhorar:** Menos dependências reduzem confusão, superfície de manutenção e risco de incompatibilidade.
* **Requisito de melhoria:** “O sistema deve manter apenas dependências realmente usadas e documentar o gerenciador oficial.”
* **Como aplicar de forma simples:**

  1. Definir `uv` como padrão.
  2. Remover dependências não usadas após confirmar.
  3. Manter `uv.lock` versionado.
  4. Documentar `uv sync` e `uv run uvicorn main:app --reload`.
* **Critério de aceite:** Um novo dev consegue instalar e rodar o projeto usando somente README + `uv`.
* **Arquivos provavelmente envolvidos:** `pyproject.toml`, `uv.lock`, `README.md`.
* **O que evitar:** Não manter `requirements.txt` e `pyproject.toml` divergentes se não houver necessidade.
* **Fonte do porquê:** O Python Packaging User Guide documenta `pyproject.toml` como arquivo central de configuração de empacotamento e ferramentas. ([packaging.python.org][15])
* **Referências de estudo:**

  * Inglês: Python Packaging User Guide; uv documentation.
  * Português: Guias de `pyproject.toml` e `uv` em Python.

---

## RM-020 — Adicionar Ruff para lint e formatação

* **Categoria:** Qualidade de código
* **Prioridade:** Baixa
* **Dificuldade:** Fácil
* **Impacto:** Médio
* **Status:** Não confirmado
* **Problema identificado:** Não há configuração de linter/formatter no projeto.
* **Por que melhorar:** Padroniza estilo, imports e erros simples antes de virar bug.
* **Requisito de melhoria:** “O sistema deve possuir ferramenta simples de lint e formatação configurada no projeto.”
* **Como aplicar de forma simples:**

  1. Adicionar `ruff` como dependência de desenvolvimento.
  2. Configurar `[tool.ruff]` no `pyproject.toml`.
  3. Usar `uv run ruff check .` e `uv run ruff format .`.
  4. Documentar no README.
* **Critério de aceite:** `ruff check .` e `ruff format --check .` executam sem erros críticos.
* **Arquivos provavelmente envolvidos:** `pyproject.toml`, README.
* **O que evitar:** Não discutir estilo manualmente antes de automatizar.
* **Fonte do porquê:** Ruff é linter e formatter Python oficial da Astral, com suporte a muitas regras e formatação via CLI. ([Astral Docs][16]) ([Astral Docs][17])
* **Referências de estudo:**

  * Inglês: Ruff Docs.
  * Português: Artigos brasileiros introdutórios sobre Ruff.

---

## RM-021 — Criar Dockerfile simples para estudo/deploy

* **Categoria:** Deploy / Experiência de desenvolvimento
* **Prioridade:** Média
* **Dificuldade:** Média
* **Impacto:** Alto
* **Status:** Confirmado pelo código
* **Problema identificado:** Não há `Dockerfile` nem `docker-compose.yml`.
* **Por que melhorar:** Docker ajuda a rodar a API de forma mais parecida com produção e facilita deploy em Render, Cloud Run, VPS e outros.
* **Requisito de melhoria:** “O sistema deve possuir Dockerfile simples para empacotar a aplicação.”
* **Como aplicar de forma simples:**

  1. Criar `Dockerfile`.
  2. Instalar dependências com `uv` ou `pip`.
  3. Copiar código.
  4. Expor porta.
  5. Rodar `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`.
* **Critério de aceite:** `docker build` e `docker run` sobem a API e `/health` responde.
* **Arquivos provavelmente envolvidos:** `Dockerfile`, `.dockerignore`, README.
* **O que evitar:** Não adicionar Kubernetes agora.
* **Fonte do porquê:** A documentação Docker para Python mostra como containerizar uma aplicação Python/FastAPI com Dockerfile e Compose. ([Docker Documentation][18])
* **Referências de estudo:**

  * Inglês: Docker Python Guide.
  * Português: Tutoriais Docker para Python/FastAPI.

---

## RM-022 — Criar CI simples com GitHub Actions

* **Categoria:** CI/CD / Testes / Qualidade
* **Prioridade:** Baixa
* **Dificuldade:** Média
* **Impacto:** Médio
* **Status:** Não confirmado
* **Problema identificado:** Não há workflow de CI.
* **Por que melhorar:** Ajuda a garantir que testes e lint rodem antes de merge/deploy.
* **Requisito de melhoria:** “O sistema deve possuir pipeline simples para instalar dependências, rodar lint e testes.”
* **Como aplicar de forma simples:**

  1. Criar `.github/workflows/ci.yml`.
  2. Usar Python 3.12.
  3. Rodar `uv sync`.
  4. Rodar `ruff check .`.
  5. Rodar `pytest`.
* **Critério de aceite:** Todo push executa CI e falha se testes quebrarem.
* **Arquivos provavelmente envolvidos:** `.github/workflows/ci.yml`, `pyproject.toml`.
* **O que evitar:** Não criar pipeline complexo de deploy antes dos testes existirem.
* **Fonte do porquê:** A documentação do GitHub Actions fornece workflow padrão para build e testes em projetos Python. ([GitHub Docs][19])
* **Referências de estudo:**

  * Inglês: GitHub Actions — Building and testing Python.
  * Português: Tutoriais GitHub Actions com Python.

---

# 4. Requisitos específicos de deploy

## 4.1 Estado atual para deploy

* **A aplicação está pronta para deploy?** Ainda não. Ela pode rodar localmente após instalar dependências, mas faltam requisitos mínimos de produção.
* **Há Dockerfile?** Não.
* **Há `requirements.txt` ou `pyproject.toml` adequado?** Há `pyproject.toml` e `uv.lock`. Não encontrei `requirements.txt` na estrutura real, embora o README antigo mencione.
* **Há configuração por ambiente?** Parcial. Existe `.env`, mas falta `settings.py` tipado e `.env.example`.
* **Há banco externo configurável?** Parcial. `DATABASE_URL` existe, mas `connect_args` está fixo para SQLite.
* **Há logs mínimos?** Não há logging explícito.
* **Há health check?** Não.
* **Há documentação de deploy?** Não de forma confiável. O README está desatualizado em partes.

## 4.2 Melhorias mínimas antes de deploy

Antes de publicar, implementar no mínimo:

* `.env.example`;
* remoção de `.env` real do pacote;
* regeneração de `SECRET_KEY`;
* separação de configuração local/produção;
* validação de `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`;
* servidor ASGI correto com `uvicorn`;
* endpoint `/health`;
* logs básicos;
* README com comandos reais;
* banco configurável por variável de ambiente;
* CORS ajustado somente se houver front-end;
* secrets fora do código;
* Dockerfile, se o caminho escolhido usar container;
* testes mínimos de autenticação e pedidos.

## 4.3 Caminhos de deploy recomendados

### Caminho A — Deploy simples em PaaS gratuito ou low cost

**Opções:** Render, Railway, Fly.io, Azure App Service, Google Cloud Run, AWS App Runner.

**Quando faz sentido:** Para primeiro deploy público, portfólio, estudo e validação rápida.

**Nível de dificuldade:** Fácil a médio.

**Custo aproximado:**

* Render tem workspace Hobby a US$0/mês + compute e web services a partir de US$0/mês, mas serviços gratuitos têm limitações. ([Render][20])
* Railway mostra plano Free US$0/mês e Hobby US$5/mês, com limites por plano. ([Railway Docs][21])
* Fly.io não deve ser tratado como “free tier” permanente para novos usuários; a própria documentação informa que não há conta/free tier gratuito e que allowances não limitam a fatura. ([Fly.io][22])
* Google Cloud Run tem free tier mensal para CPU, memória e requisições, mas exige atenção com billing e região. ([Google Cloud][23])
* AWS App Runner é simples, mas cobra memória provisionada mesmo com aplicação ociosa e cobra CPU quando ativa. ([Amazon Web Services, Inc.][24])

**Vantagens:**

* Menos infra para administrar.
* Deploy por Git.
* HTTPS geralmente simplificado.
* Logs no painel.
* Bom para júnior aprender deploy sem gerenciar servidor.

**Desvantagens:**

* Free tier pode dormir, limitar recursos ou gerar custo se mal configurado.
* Banco SQLite local não é bom para produção nessas plataformas.
* Banco gerenciado pode custar mais que a API.

**Passos mínimos:**

1. Criar `/health`.
2. Criar `.env.example`.
3. Corrigir comando de start.
4. Subir no GitHub sem `.env` e sem `base.db`.
5. Configurar variáveis no painel.
6. Usar SQLite apenas para teste; para algo mais sério, usar PostgreSQL gerenciado ou VPS com volume/backup.

**O que estudar:**

* Uvicorn;
* variáveis de ambiente;
* logs;
* PostgreSQL básico;
* Render/Railway/Cloud Run docs.

### Caminho B — Deploy com Docker em VPS barato ou gratuito

**Opções:** Oracle Cloud Free Tier, DigitalOcean, Hetzner, AWS EC2 Free Tier.

**Quando faz sentido:** Quando o objetivo é aprender operação mais próxima do mundo profissional: Linux, SSH, Docker, logs, proxy reverso, HTTPS e backup.

**Nível de dificuldade:** Médio.

**Vantagens:**

* Mais controle.
* Custo previsível em VPS paga.
* Aprende Linux, Docker, Nginx/Caddy, systemd e segurança básica.
* Permite rodar API + Postgres no mesmo servidor para estudo.

**Desvantagens:**

* Você administra segurança, atualizações e backup.
* Mais chance de erro operacional.
* Precisa cuidar de firewall e HTTPS.

**Custos:**

* Oracle Cloud Free Tier oferece Always Free Services e US$300 de crédito por 30 dias para teste; os serviços Always Free têm limites e podem ter restrições de capacidade. ([Oracle][25])
* DigitalOcean Droplets começam em US$4/mês e são cobrados por segundo com mínimo de 60 segundos; backups são custo adicional. ([DigitalOcean][26]) ([DigitalOcean Docs][27])
* Hetzner costuma ser barato, mas houve ajuste de preços em junho de 2026; confirmar valores atuais antes de contratar. ([docs.hetzner.com][28])

**Cuidados de segurança:**

* SSH com chave, sem senha.
* Firewall liberando só 22, 80 e 443.
* Não rodar app como root.
* HTTPS com Caddy ou Nginx + Certbot.
* Backups do banco.
* Atualizações do sistema.
* Logs e rotação.

**Uso de Nginx/Caddy:**

* Caddy é mais simples para HTTPS automático.
* Nginx é mais tradicional e muito usado em produção.

**systemd ou Docker Compose:**

* Para júnior, Docker Compose é mais didático.
* systemd é útil se rodar sem container.

### Caminho C — Deploy em container gerenciado com free tier

**Opções:** Google Cloud Run, Azure Container Apps, AWS ECS Fargate.

**Quando faz sentido:** Quando o projeto já tem Dockerfile e você quer evitar administrar VPS.

**Nível de dificuldade:** Médio.

**Vantagens:**

* Container gerenciado.
* Escala melhor que VPS simples.
* Pode escalar para zero em alguns cenários.
* Bom caminho profissional sem Kubernetes.

**Desvantagens:**

* Precisa entender imagem Docker, variáveis, registry e billing.
* Banco deve ser externo.
* Logs e rede exigem mais estudo.
* Custo pode surpreender se deixar recursos mínimos sempre ligados.

**Requisitos prévios:**

* Dockerfile funcionando.
* `/health`.
* Config por env vars.
* Banco externo.
* Logs em stdout.
* Secret fora do código.

**Fluxo básico:**

1. Build da imagem.
2. Push para registry.
3. Criar serviço no Cloud Run/Azure Container Apps.
4. Configurar env vars.
5. Configurar porta.
6. Testar `/health`.
7. Configurar domínio depois.

**Observação de custo:** Cloud Run e Azure Container Apps têm free grants mensais para CPU/memória/requisições, mas precisam de billing ativo e controle de consumo. ([Google Cloud][23]) ([Microsoft Azure][29])

### Caminho D — Deploy local/profissional para estudo

**Objetivo:** Montar ambiente local parecido com produção, sem gastar.

Componentes:

* `Dockerfile`;
* `docker-compose.yml`;
* Postgres;
* `.env`;
* `.env.example`;
* Alembic migrations;
* `/health`;
* logs básicos;
* README com comandos.

**Fluxo sugerido:**

1. `docker compose up --build`.
2. API sobe em `localhost:8000`.
3. Postgres sobe em `localhost:5432`.
4. `alembic upgrade head`.
5. `pytest`.
6. Swagger em `/docs`.
7. Health check em `/health`.

Esse é o melhor caminho de aprendizado antes de gastar com cloud.

## 4.4 Recomendação final de deploy para este projeto

| Caminho                    |              Recomendado agora? | Por quê                                             | Complexidade | Próximo passo                                           |
| -------------------------- | ------------------------------: | --------------------------------------------------- | -----------: | ------------------------------------------------------- |
| Render/Railway simples     | Sim, depois dos ajustes mínimos | Mais fácil para primeiro deploy de portfólio        |  Baixa/Média | Criar `/health`, `.env.example`, corrigir start command |
| Docker Compose local       |             Sim, antes da nuvem | Ensina padrão profissional sem custo                |        Média | Criar Dockerfile + Postgres local                       |
| Google Cloud Run           |           Sim, depois de Docker | Profissional e com free tier mensal                 |        Média | Criar imagem Docker e configurar env vars               |
| Oracle Cloud Free Tier VPS |         Sim, para estudar infra | Gratuito/baixo custo, mais próximo de servidor real |   Média/Alta | Preparar VPS com Docker, firewall e Caddy               |
| AWS App Runner             |                       Não agora | Simples, mas pode custar mesmo parado               |        Média | Usar só quando souber controlar billing                 |
| Kubernetes                 |                             Não | Complexo demais para este projeto                   |         Alta | Estudar apenas no futuro                                |

---

# 5. Roadmap de melhoria para desenvolvedor júnior

## Fase 1 — Rodar, entender e documentar

Objetivo: deixar o projeto fácil de executar e compreender.

Itens:

* RM-012
* RM-019
* RM-011

Entregável:

* projeto roda localmente;
* README atualizado;
* variáveis documentadas;
* comandos básicos definidos;
* `/health` funcionando.

## Fase 2 — Organização e qualidade básica

Objetivo: deixar o código mais limpo, separado e previsível.

Itens:

* RM-001
* RM-006
* RM-010
* RM-020

Entregável:

* login por email corrigido;
* schemas organizados;
* rotas sem duplicação;
* lint e formatação configurados.

## Fase 3 — Testes e segurança básica

Objetivo: garantir que os fluxos principais funcionam e reduzir riscos.

Itens:

* RM-002
* RM-003
* RM-004
* RM-005
* RM-015
* RM-016

Entregável:

* testes dos principais endpoints;
* admin bloqueado no cadastro público;
* access/refresh token separados;
* erros básicos padronizados.

## Fase 4 — Preparação para deploy

Objetivo: deixar a aplicação pronta para rodar fora da máquina local.

Itens:

* RM-013
* RM-014
* RM-017
* RM-021

Entregável:

* configuração centralizada;
* banco configurável;
* logs básicos;
* Dockerfile;
* comando de start de produção.

## Fase 5 — Deploy inicial gratuito ou low cost

Objetivo: publicar a aplicação de forma simples e econômica.

Itens:

* RM-011
* RM-012
* RM-021

Entregável:

* aplicação publicada;
* endpoint `/health` funcionando;
* variáveis configuradas;
* logs acessíveis;
* README com link e instruções.

## Fase 6 — Melhorias futuras

Objetivo: evoluir sem complexidade desnecessária.

Itens:

* RM-018
* RM-022
* melhorias de CORS se houver front-end;
* PostgreSQL em produção;
* refresh token mais robusto com revogação, se o projeto crescer.

---

# 6. Plano semanal sugerido

| Semana | Foco               | Melhorias                      | Entregável                                       | Referências                              |
| -----: | ------------------ | ------------------------------ | ------------------------------------------------ | ---------------------------------------- |
|      1 | Rodar e documentar | RM-012, RM-019, RM-011         | README real + `.env.example` + `/health`         | FastAPI Settings; Twelve-Factor          |
|      2 | Segurança inicial  | RM-001, RM-002, RM-003         | Login por email + bloqueio de admin público      | FastAPI OAuth2/JWT; OWASP                |
|      3 | Token e erros      | RM-004, RM-005, RM-016         | Tokens com expiração correta e erros 401/404/409 | PyJWT; FastAPI errors                    |
|      4 | Banco e validação  | RM-007, RM-008, RM-009, RM-014 | Validações + migration + rollback                | Pydantic; SQLAlchemy; Alembic            |
|      5 | Testes e qualidade | RM-015, RM-020                 | `pytest` + Ruff                                  | FastAPI Testing; Ruff                    |
|      6 | Deploy             | RM-017, RM-021, RM-022         | Dockerfile + CI simples + deploy inicial         | Docker; GitHub Actions; Render/Cloud Run |

---

# 7. Fontes recomendadas

## Inglês

* **FastAPI Documentation** — base principal para rotas, validação, dependências e OpenAPI.
* **FastAPI Bigger Applications** — estudar organização com `APIRouter`, múltiplos arquivos e modularização. ([FastAPI][8])
* **FastAPI Deployment** — estudar conceitos de deploy ASGI, workers e produção.
* **Uvicorn Documentation** — estudar como executar aplicação ASGI e comandos de produção. ([Uvicorn][30])
* **FastAPI OAuth2/JWT** — estudar autenticação, hash de senha e tokens JWT. ([FastAPI][1])
* **Pydantic Documentation** — estudar validação de dados, tipos, campos e schemas. ([pydantic.dev][5])
* **FastAPI Settings and Environment Variables** — estudar `pydantic-settings`, `.env` e config testável. ([FastAPI][11])
* **SQLAlchemy Documentation** — estudar sessão, commit, rollback, models e relacionamentos. ([docs.sqlalchemy.org][7])
* **Alembic Documentation** — estudar migrations versionadas para banco. ([Alembic][31])
* **Pytest Documentation / FastAPI Testing** — estudar testes com `pytest` e `TestClient`. ([FastAPI][12])
* **Docker Python Guide** — estudar Dockerfile e Compose para aplicação Python. ([Docker Documentation][18])
* **Twelve-Factor App** — estudar configuração por variáveis de ambiente. ([Twelve-Factor App][10])
* **OWASP API Security Top 10** — estudar riscos comuns de autenticação e autorização em APIs. ([OWASP][2])
* **GitHub Actions Python** — estudar CI simples para rodar testes e lint. ([GitHub Docs][19])
* **Render Docs / Cloud Run / Railway** — estudar deploy PaaS/containers e custos atuais. ([Render][32])

## Português

* **FastAPI em português — Aplicações maiores** — bom para entender organização com routers em português. ([FastAPI][33])
* **Auth0 Brasil — JWT em Python** — bom material introdutório sobre JWT e PyJWT. ([Auth0][34])
* **Oracle Cloud Free Tier em português** — útil para estudar VPS gratuita/baixo custo. ([Oracle][35])
* **AWS App Runner pricing em português** — útil para entender custo antes de usar AWS. ([Amazon Web Services, Inc.][36])
* **Azure Container Apps preços em português** — útil para estudar container gerenciado com free grant. ([Microsoft Azure][37])

---

# 8. O que não fazer agora

* **Kubernetes:** não faz sentido para uma API pequena sem Docker, testes e logs básicos. Faz sentido no futuro se houver múltiplos serviços e necessidade real de orquestração.
* **Microsserviços:** o projeto é monolítico simples. Separar agora aumentaria complexidade sem ganho.
* **Event sourcing:** complexo demais para um CRUD de pedidos simples.
* **Arquitetura hexagonal completa:** pode ser estudada depois, mas agora basta manter `routes`, `services`, `schemas`, `models` e talvez `repositories` se crescer.
* **DDD pesado:** não há domínio complexo suficiente.
* **Mensageria com RabbitMQ/Kafka:** só faria sentido com processamento assíncrono real, filas de entrega, pagamento ou notificações.
* **CI/CD complexo:** primeiro faça CI simples com testes e lint.
* **Observabilidade pesada com Prometheus/Grafana:** primeiro logs + `/health`.
* **Autenticação sofisticada demais:** primeiro corrigir JWT, roles e refresh token.
* **Cloud complexa demais:** primeiro Render/Railway/Cloud Run ou Docker Compose local.
* **Múltiplos ambientes complexos:** para agora, basta `local`, `test` e `prod` por variáveis.

---

# 9. Checklist final para o júnior

* consigo rodar o projeto localmente?
* o README explica como instalar?
* o README explica como executar?
* o README explica como testar?
* as variáveis de ambiente estão documentadas?
* existe `.env.example`?
* os segredos estão fora do código e fora do zip?
* `base.db` local não está sendo distribuído com dados reais?
* as rotas estão organizadas?
* não existe `/pedidos/pedidos/...` por acidente?
* os schemas estão claros?
* a rota pública de cadastro não aceita `admin`?
* há validação de email, senha, quantidade e preço?
* há tratamento básico de erro?
* refresh token não acessa rotas protegidas?
* token novo recebe expiração nova?
* há testes dos fluxos principais?
* o banco está documentado?
* Alembic está funcionando?
* existe health check?
* existem logs básicos?
* existe comando de start para produção?
* existe Dockerfile, se o deploy escolhido precisar?
* existe caminho de deploy gratuito ou low cost recomendado?
* os critérios de aceite de cada melhoria estão claros?

---

# 10. Resumo executivo

As melhorias mais importantes são corrigir autenticação por email, impedir criação pública de admin, separar access token de refresh token, calcular expiração do token no momento correto, criar `.env.example`, remover segredos do pacote, adicionar `/health` e criar testes automatizados.

As melhorias mais fáceis para começar são atualizar README, criar `.env.example`, adicionar `/health`, corrigir rotas duplicadas e bloquear `admin` no schema público de cadastro.

As melhorias que mais aumentam qualidade profissional são testes com pytest, Pydantic Settings, rollback nas transações, validações fortes, logs básicos, Dockerfile e CI simples.

Para deploy, o melhor caminho inicial é **Docker Compose local para estudo** e depois **Render ou Railway** para primeiro deploy simples. O caminho mais profissional ainda low cost é **Google Cloud Run** ou **VPS com Docker + Caddy + Postgres**, dependendo se o objetivo é aprender cloud gerenciada ou administração Linux.

A ordem recomendada é: documentação e `.env.example` → segurança de cadastro/login/token → validações e banco → testes → logs/health → Docker → deploy.

O principal cuidado é não transformar essa aplicação em algo maior do que ela precisa ser. Primeiro corrija o básico com disciplina; depois pense em arquitetura mais avançada somente se o projeto crescer de verdade.

[1]: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ "OAuth2 with Password (and hashing), Bearer with JWT tokens - FastAPI"
[2]: https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/ "API3:2023 Broken Object Property Level Authorization - OWASP API Security Top 10"
[3]: https://owasp.org/API-Security/editions/2023/en/0xa2-broken-authentication/ "API2:2023 Broken Authentication - OWASP API Security Top 10"
[4]: https://pyjwt.readthedocs.io/ "Welcome to PyJWT — PyJWT 2.13.0 documentation"
[5]: https://pydantic.dev/docs/validation/latest/get-started/?utm_source=chatgpt.com "Welcome to Pydantic | Pydantic Docs"
[6]: https://docs.sqlalchemy.org/20/orm/basic_relationships.html "
        
        
    
    Basic Relationship Patterns
 —
    SQLAlchemy 2.0 Documentation

        
    "
[7]: https://docs.sqlalchemy.org/en/latest/orm/session_basics.html "
        
        
    
    Session Basics
 —
    SQLAlchemy 2.1 Documentation

        
    "
[8]: https://fastapi.tiangolo.com/tutorial/bigger-applications/?utm_source=chatgpt.com "Bigger Applications - Multiple Files - FastAPI"
[9]: https://render.com/docs/web-services "Web Services – Render Docs"
[10]: https://12factor.net/config "The Twelve-Factor App "
[11]: https://fastapi.tiangolo.com/advanced/settings/ "Settings and Environment Variables - FastAPI"
[12]: https://fastapi.tiangolo.com/tutorial/testing/ "Testing - FastAPI"
[13]: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/?utm_source=chatgpt.com "OAuth2 with Password (and hashing), Bearer with JWT ..."
[14]: https://docs.sqlalchemy.org/en/latest/orm/session_basics.html?utm_source=chatgpt.com "Session Basics — SQLAlchemy 2.1 Documentation"
[15]: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/?utm_source=chatgpt.com "Writing your pyproject.toml - Python Packaging User Guide"
[16]: https://docs.astral.sh/ruff/?utm_source=chatgpt.com "Ruff - Astral Docs"
[17]: https://docs.astral.sh/ruff/formatter/?utm_source=chatgpt.com "The Ruff Formatter - Astral Docs"
[18]: https://docs.docker.com/guides/python/containerize/ "Python language-specific guide | Docker Docs"
[19]: https://docs.github.com/actions/guides/building-and-testing-python "Building and testing Python - GitHub Docs"
[20]: https://render.com/pricing "Pricing | Render"
[21]: https://docs.railway.com/pricing/plans "Pricing Plans | Railway Docs"
[22]: https://fly.io/docs/about/cost-management/ "Cost Management on Fly.io · Fly Docs"
[23]: https://cloud.google.com/run/pricing "Cloud Run pricing | Google Cloud"
[24]: https://aws.amazon.com/apprunner/pricing/ "AWS App Runner Pricing – Fully managed container application service – Amazon Web Services"
[25]: https://www.oracle.com/cloud/free/ "Oracle Cloud Free Tier | Oracle"
[26]: https://www.digitalocean.com/pricing/droplets?utm_source=chatgpt.com "Droplet Pricing"
[27]: https://docs.digitalocean.com/products/droplets/details/pricing/?utm_source=chatgpt.com "Droplet Pricing | DigitalOcean Documentation"
[28]: https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ "Hetzner Price Adjustment 15 June 2026 - Hetzner Docs"
[29]: https://azure.microsoft.com/en-us/pricing/details/container-apps/ "Azure Container Apps - Pricing | Microsoft Azure"
[30]: https://uvicorn.dev/ "Index - Uvicorn"
[31]: https://alembic.sqlalchemy.org/ "Welcome to Alembic’s documentation! — Alembic 1.18.5 documentation"
[32]: https://render.com/docs/deploy-fastapi "Deploy a FastAPI App – Render Docs"
[33]: https://fastapi.tiangolo.com/pt/tutorial/bigger-applications/?utm_source=chatgpt.com "Aplicações Maiores - Múltiplos Arquivos"
[34]: https://auth0.com/blog/pt-how-to-handle-jwt-in-python/?utm_source=chatgpt.com "Como Lidar com JWTs em Python"
[35]: https://www.oracle.com/br/cloud/free/?utm_source=chatgpt.com "Modo Gratuito da Oracle Cloud"
[36]: https://aws.amazon.com/pt/apprunner/pricing/?utm_source=chatgpt.com "Definição de preços do AWS App Runner"
[37]: https://azure.microsoft.com/pt-br/pricing/details/container-apps/?utm_source=chatgpt.com "Preços do Aplicativos de Contêiner do Azure"
