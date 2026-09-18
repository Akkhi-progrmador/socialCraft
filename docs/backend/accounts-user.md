SocialCraft — Implementação da Autenticação e Modelo User

Status: Concluído
Fase: Backend Base — Accounts
Componente: User + UserManager
Stack: Django + Django REST Framework + PostgreSQL planejado
Ambiente atual de desenvolvimento: SQLite

1. Objetivo deste documento

Este documento registra a implementação inicial do sistema de usuários do SocialCraft.

A intenção não é apenas documentar o código final, mas registrar:

o que foi implementado;
por que cada decisão foi tomada;
conceitos importantes aprendidos;
problemas encontrados;
como foram resolvidos;
decisões arquiteturais;
comandos utilizados;
pontos que devem ser lembrados no futuro.

Este documento serve como referência para manutenção do projeto e para recuperar rapidamente o contexto caso essa parte do sistema precise ser modificada posteriormente.

2. Contexto do projeto

O SocialCraft é uma rede social criada exclusivamente para a comunidade Minecraft.

O sistema terá usuários, perfis, posts, seguidores, servidores, notificações, moderação e outras funcionalidades.

A arquitetura definida para o backend utiliza:

Django
Django REST Framework
PostgreSQL
Redis
Object Storage para mídia
WebSockets posteriormente
arquitetura de monólito modular

O primeiro domínio implementado foi accounts.

3. Por que começamos pelo User?

O usuário é uma entidade central do sistema.

Várias outras entidades dependem dele:

User
├── Profile
├── MinecraftAccount
├── Post
├── Comment
├── Like
├── Follow
├── Server
├── Notification
└── Report

Por isso, antes de construir Profile, Posts ou Social, precisávamos estabelecer corretamente a identidade e autenticação do usuário.

4. Criação do projeto Django

Foi criado o ambiente virtual Python:

python3 -m venv .venv

Depois o ambiente foi ativado.

As principais dependências instaladas foram:

Django
Django REST Framework
psycopg
Redis

O projeto Django foi criado com:

django-admin startproject config .

Depois foram criadas as aplicações:

accounts
profiles
minecraft
posts
social
servers
notifications
moderation
core 5. Configuração do User personalizado

O Django possui um modelo de usuário padrão, mas o SocialCraft precisa de uma identidade diferente.

Por isso foi utilizado:

AbstractUser

em vez de criar o sistema de autenticação inteiro do zero.

Por que AbstractUser?

AbstractUser já fornece grande parte da infraestrutura necessária:

senha;
autenticação;
last_login;
is_active;
is_staff;
is_superuser;
groups;
permissions;
integração com Django Admin;
integração com o sistema de autenticação.

Assim podemos personalizar o usuário sem reimplementar mecanismos fundamentais do Django.

6. Definição do AUTH_USER_MODEL

No settings.py foi definido:

AUTH_USER_MODEL = 'accounts.User'

Isso informa ao Django que o modelo oficial de usuário da aplicação é:

accounts.User

e não:

django.contrib.auth.models.User
Importância

Essa configuração é extremamente importante quando se utiliza um User customizado.

Ela deve ser definida desde o início do projeto, antes que muitas migrations e relações com o usuário sejam criadas.

7. Estrutura do User

O modelo foi definido com os seguintes conceitos:

User
├── id
├── username
├── email
├── status
├── email_verified_at
├── created_at
├── updated_at
└── campos herdados de AbstractUser 8. UUID como Primary Key

O identificador principal escolhido foi UUID v4:

id = UUIDField(primary_key=True, default=uuid4, editable=False)
Por que UUID?

Em vez de IDs sequenciais:

1
2
3
4
5

o sistema utiliza identificadores como:

550e8400-e29b-41d4-a716-446655440000

Vantagens:

difícil de enumerar;
adequado para sistemas distribuídos;
não revela facilmente a quantidade de usuários;
facilita futuras integrações entre serviços;
reduz dependência de IDs sequenciais.

O UUID é gerado através de:

uuid4

Importante:

default=uuid4

e não:

default=uuid4()

O Django precisa receber a função para executá-la quando criar cada objeto.

9. Username

O username possui:

max_length = 40

e utiliza:

UnicodeUsernameValidator
O que o validator faz?

Ele valida o formato/caracteres permitidos no username.

Ele não é responsável pela unicidade case-insensitive.

Essa distinção é importante.

10. Unicidade case-insensitive do username

O SocialCraft deve considerar:

Akkhi
akkhi
AKKHI

como o mesmo username.

Porém queremos preservar a forma digitada pelo usuário para exibição.

Por isso foi utilizada uma constraint baseada em:

Lower('username')

A regra é:

Lower(username) → unique

Assim:

Akkhi → akkhi
AKKHI → akkhi
akkhi → akkhi

e dois usuários não podem ocupar a mesma identidade lógica.

Conceito importante

Existem duas responsabilidades diferentes:

UnicodeUsernameValidator
↓
validação de formato

Lower(username)
↓
unicidade case-insensitive 11. Email como identificador de autenticação

O Django normalmente utiliza:

username

como identificador de login.

No SocialCraft decidimos utilizar:

email

como identificador.

A configuração foi:

USERNAME_FIELD = 'email'

Isso representa uma decisão arquitetural importante.

Separação de responsabilidades
username
↓
identidade pública

email
↓
identidade de autenticação

Isso permite que o username seja tratado como identidade social enquanto o email funciona como identificador de login.

12. REQUIRED_FIELDS

Foi definido:

REQUIRED_FIELDS = ['username']

Como email virou o USERNAME_FIELD, o Django já o considera obrigatório para autenticação/criação.

O username continua sendo necessário para criar a conta.

Isso faz com que o comando:

python3 manage.py createsuperuser

solicite:

Email
Username
Password

Esse comportamento foi testado com sucesso.

13. Status da conta

Foi criado um TextChoices:

ACTIVE
SUSPENDED
BANNED

A ideia é separar o estado de negócio da conta do mecanismo interno de autenticação do Django.

Status do SocialCraft
ACTIVE
SUSPENDED
BANNED
Estado técnico do Django
is_active

Esses conceitos não são a mesma coisa.

Status

Representa a regra de negócio da plataforma.

is_active

É utilizado pelo sistema de autenticação do Django.

No futuro será necessário definir claramente como esses dois campos serão sincronizados durante suspensão e banimento.

14. Verificação de email

Foi criado:

email_verified_at

com:

null=True
blank=True

A ideia é:

NULL

→ email ainda não verificado.

Uma data:

2026-09-18 10:00...

→ email verificado.

Por que timestamp em vez de Boolean?

Porque além de sabermos se foi verificado, podemos saber:

Quando foi verificado?

Isso pode ser útil para auditoria e segurança.

O campo não deve ser unique.

Vários usuários podem possuir valores de verificação diferentes.

15. Timestamps

Foram adicionados:

created_at
updated_at
created_at

Utiliza:

auto_now_add=True

Registra quando o objeto foi criado.

updated_at

Utiliza:

auto_now=True

Atualiza automaticamente quando o objeto é salvo.

16. Por que não criamos password_hash?

Foi decidido não criar manualmente:

password_hash

porque AbstractUser já fornece o sistema de senha do Django.

A senha é processada através do mecanismo de hashing do Django.

O código de criação utiliza:

set_password()

Assim a senha não é armazenada diretamente em texto puro.

17. Problema encontrado: USERNAME_FIELD

Durante a primeira execução de:

python3 manage.py makemigrations

o Django apresentou:

auth.E003
'User.username' must be unique because it is named as the 'USERNAME_FIELD'
Causa

O AbstractUser possui:

USERNAME_FIELD = 'username'

por padrão.

Como o username não deveria ser unique=True diretamente no campo, o Django reclamou.

Solução

Foi definido:

USERNAME_FIELD = 'email'

Agora:

email → identificador de login
username → identidade pública

e o username pode utilizar a constraint:

Lower(username) 18. Criação do UserManager

Como o identificador de autenticação foi alterado, foi criado um manager personalizado.

Arquivo:

accounts/manager.py

O manager herda de:

BaseUserManager

e fornece:

create_user()
create_superuser() 19. Responsabilidades do UserManager

O UserManager é responsável pela criação técnica de usuários.

create_user()

Responsabilidades:

exigir email;
exigir username;
normalizar o email;
criar a instância;
processar a senha através de set_password;
salvar o usuário.
create_superuser()

Responsabilidades:

criar usuário através de create_user;
garantir is_staff=True;
garantir is_superuser=True;
definir o status inicial como ACTIVE. 20. Por que usar set_password?

Nunca devemos fazer:

user.password = senha

para salvar uma senha diretamente.

O correto é utilizar:

set_password()

O Django então utiliza seu sistema de hashing de senhas.

Conceito:

senha original
↓
password hasher
↓
hash
↓
database

O banco não deve armazenar a senha original.

21. Normalização do email

O manager utiliza:

normalize_email()

fornecido pelo Django.

Isso permite aplicar o tratamento padrão do Django ao email antes de salvar.

A questão de normalização e unicidade case-insensitive do email poderá ser refinada posteriormente.

22. Problema de import circular

O manager precisa conhecer o tipo User para tipagem.

Porém:

models.py

importa:

manager.py

Portanto seria perigoso fazer diretamente:

manager.py → models.py

porque criaríamos:

models.py
↓
manager.py
↓
models.py
↓
manager.py

Isso é um circular import.

23. Solução: TYPE_CHECKING

Foi utilizado:

TYPE_CHECKING

com uma referência ao User apenas para análise estática.

Conceitualmente:

Python em runtime
↓
não precisa importar User

Pylance/type checker
↓
consegue conhecer User

Assim mantemos:

models.py → manager.py

sem criar uma dependência circular em runtime.

24. Tipagem do BaseUserManager

O manager foi especializado para o nosso modelo:

BaseUserManager[User]

Isso informa ao sistema de tipos que o manager trabalha com:

accounts.User

Essa tipagem ajudou o Pylance a entender a relação entre:

User

e:

UserManager 25. Conflito de tipagem em objects

Ao definir:

objects = UserManager()

o Pylance apresentou um erro relacionado à sobrescrita do manager herdado de AbstractUser.

A solução adotada foi declarar objects com ClassVar e silenciar especificamente o diagnóstico de incompatibilidade de variável do Pyright/Pylance.

Importante:

O ignore foi aplicado somente ao diagnóstico de tipagem e não altera o comportamento do Django.

O funcionamento real foi posteriormente validado através do createsuperuser.

26. Problema com TextChoices

Durante a implementação do create_superuser, foi inicialmente utilizado:

'Active'

para o status.

Isso estava incorreto.

O TextChoices possui:

ACTIVE = 'ACTIVE', 'Active'

Existem duas partes:

'ACTIVE' → valor armazenado
'Active' → label apresentado

Portanto o valor correto para o banco é:

ACTIVE

Esse detalhe foi corrigido.

27. Migrations

Depois da implementação do User foi executado:

python3 manage.py makemigrations

O Django criou:

accounts/migrations/0001_initial.py 28. Problema com migrations apagadas

Durante o desenvolvimento, as pastas de migrations foram apagadas depois de uma aplicação anterior.

Isso provocou:

App 'accounts' does not have migrations

A solução foi recriar:

accounts/migrations/

e:

**init**.py

Depois:

python3 manage.py makemigrations

recriou a migration inicial.

Lição

Não devemos apagar migrations automaticamente quando algo dá errado.

É necessário primeiro identificar se:

a migration foi criada;
foi aplicada;
o banco ainda existe;
o projeto está em desenvolvimento;
existem dados que precisam ser preservados. 29. Aplicação das migrations

Depois da recriação das migrations foi executado:

python3 manage.py migrate

O Django aplicou:

contenttypes
auth
accounts
admin
sessions

com sucesso.

O ponto principal foi:

Applying accounts.0001_initial... OK

Isso criou a tabela:

accounts_user

no banco de desenvolvimento.

30. Teste do sistema de criação de usuário

Foi executado:

python3 manage.py createsuperuser

O Django solicitou:

Email
Username
Password
Password (again)

Isso confirmou que:

USERNAME_FIELD = email

e:

REQUIRED_FIELDS = ['username']

estão funcionando como planejado.

O resultado foi:

Superuser created successfully. 31. Fluxo final validado

O fluxo completo testado foi:

createsuperuser
↓
email
↓
username
↓
password
↓
UserManager.create_superuser()
↓
is_staff = True
is_superuser = True
status = ACTIVE
↓
create_user()
↓
set_password()
↓
save()
↓
accounts_user
↓
Superuser criado 32. Verificação estrutural

Também foi executado:

python3 manage.py check

Resultado:

System check identified no issues (0 silenced).

Isso confirma que o Django não encontrou problemas estruturais no projeto naquele momento.

33. Estado atual

Neste ponto, o domínio accounts possui uma base funcional para usuários.

Está implementado:

┌─────────────────────────────┐
│ User │
├─────────────────────────────┤
│ UUID │
│ username │
│ email │
│ status │
│ email_verified_at │
│ created_at │
│ updated_at │
│ Django auth fields │
└──────────────┬──────────────┘
│
▼
┌──────────────┐
│ UserManager │
├──────────────┤
│ create_user │
│ create_super │
└──────────────┘ 34. O que ainda NÃO foi implementado

Esta implementação não significa que todo o sistema de autenticação do SocialCraft esteja terminado.

Ainda serão necessários posteriormente:

registro através da API;
login através da API;
JWT Access/Refresh;
refresh de tokens;
logout/revogação conforme estratégia escolhida;
recuperação de senha;
verificação de email;
alteração de email;
alteração de senha;
rate limiting;
proteção contra abuso;
confirmação de ações sensíveis;
políticas de sessão;
autenticação social/OAuth futuramente.

Portanto:

User ≠ sistema completo de autenticação

O User é a fundação sobre a qual o sistema de autenticação será construído.

35. Conceitos aprendidos nesta etapa

Esta implementação serviu para consolidar os seguintes conceitos:

Django
AbstractUser
custom user model
AUTH_USER_MODEL
USERNAME_FIELD
REQUIRED_FIELDS
Django permissions
Django migrations
makemigrations
migrate
createsuperuser
manage.py check
Banco de dados
Primary Key
UUID
Unique constraint
case-insensitive uniqueness
migrations
tabela versus migration
Python
classes
herança
managers
BaseUserManager
type hints
generics
Optional
Any
ClassVar
TYPE_CHECKING
import circular
Segurança
password hashing
set_password
autenticação versus autorização
identificação do usuário através do email
estados de conta 36. Decisões arquiteturais registradas

As decisões tomadas nesta etapa foram:

Utilizar AbstractUser.
Utilizar UUID v4 como PK.
Utilizar email como identificador de autenticação.
Manter username como identidade pública.
Garantir username case-insensitive.
Utilizar TextChoices para status.
Separar status de is_active.
Utilizar email_verified_at como timestamp opcional.
Utilizar UserManager personalizado.
Manter manager separado em accounts/manager.py.
Utilizar tipagem com TYPE_CHECKING.
Não armazenar senhas manualmente.
Usar migrations como histórico estrutural do banco.
Não apagar migrations sem entender seu estado.
Manter o User como fundação dos demais domínios. 37. Próxima etapa

Com o User funcionando, o próximo domínio é:

profiles

A relação planejada é:

User 1 ───── 1 Profile

O User continuará responsável principalmente por:

identidade
autenticação
estado da conta

Enquanto Profile será responsável por informações como:

display_name
bio
avatar
country
language
birth_date

Também deverá ser considerada a arquitetura de privacidade, pois o usuário poderá controlar a visibilidade de determinadas informações do perfil.

38. Regra para futuras alterações

Antes de alterar o modelo User, verificar:

O campo representa identidade/autenticação ou perfil?
Precisa realmente pertencer ao User?
Existe alguma regra de unicidade?
A unicidade diferencia maiúsculas/minúsculas?
Existe impacto nas migrations?
Existe impacto no UserManager?
Existe impacto no Django Admin?
Existe impacto na autenticação?
Existe impacto na API?
A alteração precisa de nova migration?

O objetivo é evitar transformar o User em um modelo gigante contendo todas as informações da plataforma.

Conclusão

A primeira fundação do SocialCraft foi concluída.

O projeto agora possui um modelo de usuário personalizado, com email como identificador de autenticação, username como identidade pública, UUID como identificador primário, estados de conta, preparação para verificação de email e um UserManager próprio.

O sistema foi validado estruturalmente com:

python3 manage.py check

e funcionalmente com:

python3 manage.py createsuperuser

Resultado:

System check identified no issues (0 silenced).

Superuser created successfully.

Status: User + UserManager concluídos.
