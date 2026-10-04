# SocialCraft — Registro de Implementação: Profile v1.0

**Fase:** Profile  
**Status:** ✅ Estrutura concluída  
**Banco de dados:** PostgreSQL  
**Backend:** Django + Django REST Framework

---

## 1. Objetivo

Implementar a entidade `Profile` responsável pelos dados públicos e complementares associados ao usuário do SocialCraft.

A relação definida foi:

```text
User 1 ───── 1 Profile
```

Cada usuário pode possuir no máximo um perfil.

---

## 2. Model `Profile`

Foi implementado o modelo `Profile` dentro da aplicação `profiles`.

### Identificação

- `id`: UUID como chave primária.
- `user`: relação `OneToOneField` com `accounts.User`.
- `on_delete=models.CASCADE`.

A relação `OneToOneField` garante que um usuário não tenha vários Profiles.

---

## 3. Dados do perfil

O modelo possui:

- `display_name`: nome exibido no perfil, máximo de 50 caracteres.
- `bio`: descrição opcional, máximo de 500 caracteres.
- `avatar_url`: URL opcional para o avatar.
- `country`: país utilizando escolhas controladas.
- `language`: idioma utilizando escolhas controladas.
- `birth_date`: data de nascimento.
- `created_at`: data/hora de criação.
- `updated_at`: data/hora da última atualização.

### Escolhas de país

```text
FR → França
US → Estados Unidos
AO → Angola
ES → Espanha
```

### Escolhas de idioma

```text
FR → Francês
EN → Inglês
PT → Português
ES → Espanhol
```

---

## 4. Privacidade de `birth_date`

Foi tomada uma decisão importante de segurança:

`birth_date` não faz parte da representação pública do Profile.

Para isso foram criados dois serializers diferentes:

```text
ProfileReadSerializer
ProfileWriteSerializer
```

### `ProfileReadSerializer`

Utilizado para leitura.

O campo `birth_date` é excluído da representação enviada ao cliente.

### `ProfileWriteSerializer`

Utilizado para criação e atualização.

Permite que `birth_date` seja recebido durante a criação/edição do próprio perfil.

O campo `user` é `read_only`.

Isso impede que o cliente escolha arbitrariamente a qual usuário o Profile pertence.

---

## 5. Separação Read / Write

A separação dos serializers foi escolhida porque leitura e escrita possuem necessidades diferentes.

```text
GET
 ↓
ProfileReadSerializer
 ↓
não expõe birth_date


POST / PUT / PATCH
 ↓
ProfileWriteSerializer
 ↓
permite os dados necessários para criação/edição
```

Essa abordagem deixa a regra de privacidade explícita e evita depender apenas do frontend para esconder informações.

---

## 6. View

Foi utilizada a combinação:

```text
GenericAPIView
CreateModelMixin
RetrieveModelMixin
UpdateModelMixin
```

A escolha foi feita para manter maior controle sobre o comportamento do endpoint, principalmente porque o Profile utiliza a lógica especial de `/me/`.

Não foi utilizado `ListModelMixin`, pois o endpoint não deve listar todos os Profiles.

---

## 7. Autorização

A View utiliza:

```text
IsAuthenticated
```

Portanto, somente usuários autenticados podem acessar o endpoint.

O primeiro teste confirmou esse comportamento:

```json
{
  "detail": "As credenciais de autenticação não foram fornecidas."
}
```

Isso comprovou que:

```text
URL
 ↓
View
 ↓
permission_classes
 ↓
usuário não autenticado
 ↓
acesso bloqueado
```

A autenticação JWT será implementada posteriormente.

---

## 8. Isolamento do Profile

A View utiliza `request.user` para determinar o proprietário do Profile.

O `get_queryset()` foi configurado para retornar somente:

```text
Profile pertencente ao usuário autenticado
```

Dessa forma, a API não deve permitir que um usuário consulte ou altere diretamente o Profile de outro usuário através desse endpoint.

---

## 9. `get_object()`

O método `get_object()` foi personalizado para procurar o Profile através do usuário autenticado.

Importante:

`get_object()` apenas procura o Profile.

Ele não cria automaticamente um Profile caso ele não exista.

Isso mantém a separação:

```text
GET / PUT / PATCH
        ↓
procurar Profile


POST
        ↓
criar Profile
```

---

## 10. Criação segura do Profile

Foi utilizado:

```text
perform_create()
```

para associar o Profile ao usuário autenticado.

Conceitualmente:

```text
POST
 ↓
CreateModelMixin
 ↓
serializer
 ↓
perform_create()
 ↓
user = request.user
 ↓
Profile criado
```

Assim, o cliente não precisa e não pode escolher o proprietário do Profile.

Essa responsabilidade pertence ao backend.

---

## 11. Endpoints definidos

A rota final segue a convenção da API:

```text
/api/v1/profile/me/
```

Operações:

```text
GET
```

Recupera o Profile do usuário autenticado.

```text
POST
```

Cria o Profile do usuário autenticado.

```text
PUT
```

Atualiza o Profile.

```text
PATCH
```

Atualiza parcialmente o Profile.

Não foi implementado `DELETE` nesta fase.

---

## 12. URLs

A aplicação `profiles` possui a rota:

```text
me/
```

e ela é incluída pelo `urls.py` principal sob:

```text
/api/v1/profile/
```

Resultando em:

```text
/api/v1/profile/me/
```

---

## 13. Validação

Foi executado:

```bash
python3 manage.py check
```

Resultado:

```text
System check identified no issues (0 silenced).
```

Isso confirmou que a configuração Django relacionada à implementação atual não apresenta erros detectados pelo sistema de checks.

Também foi realizado um teste real do endpoint sem autenticação, que confirmou que `IsAuthenticated` está sendo aplicado.

---

## 14. Estado da implementação

### Concluído

- [x] Model `Profile`
- [x] UUID como PK
- [x] Relação `User 1:1 Profile`
- [x] Campos do Profile
- [x] Choices de país
- [x] Choices de idioma
- [x] `birth_date`
- [x] Timestamps
- [x] Migração do Profile para PostgreSQL
- [x] `ProfileReadSerializer`
- [x] `ProfileWriteSerializer`
- [x] Proteção de `birth_date` na leitura
- [x] `GenericAPIView`
- [x] `CreateModelMixin`
- [x] `RetrieveModelMixin`
- [x] `UpdateModelMixin`
- [x] `IsAuthenticated`
- [x] Isolamento por `request.user`
- [x] `perform_create()`
- [x] GET
- [x] POST
- [x] PUT
- [x] PATCH
- [x] Endpoint `/api/v1/profile/me/`
- [x] `manage.py check`
- [x] Teste de bloqueio para usuário não autenticado

### Ainda dependente de outra fase

- [ ] Autenticação JWT
- [ ] Teste completo autenticado do CRUD
- [ ] Upload real de avatar/Object Storage
- [ ] Configuração futura de privacidade avançada do Profile

---

## 15. Conceitos para lembrar

### View

Controla o comportamento da requisição HTTP.

```text
request
   ↓
View
   ↓
Serializer
   ↓
Model
   ↓
Database
```

### Serializer

Responsável por transformar e validar os dados entre representação externa e objetos Django.

### Model

Representa a estrutura persistente do Profile.

### `request.user`

Representa o usuário autenticado que está realizando a requisição.

### `perform_create()`

É o ponto utilizado pela View para aplicar lógica adicional durante a criação.

No Profile, ele garante que o proprietário seja o usuário autenticado, e não um valor enviado pelo cliente.

---

## Estado final

**Profile v1.0 — estrutura implementada e validada.**

A próxima camada necessária para testar o fluxo autenticado de ponta a ponta é a implementação de **JWT**.
