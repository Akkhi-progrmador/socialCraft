from django.contrib.auth.models import BaseUserManager #import tando o base pra echer com o crete user e superuser

from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from accounts.models import User

class UserManager(BaseUserManager['User']):

    def create_user(self, email: str, username: str, password: Optional[str]=None, **extra_fields: Any)-> 'User':
        if not email:
            raise ValueError('O campo de email deve ser preenchido.')
        if not username:
            raise ValueError('O campo de username deve ser preenchido.')

        email = self.normalize_email(email) #tratamento do email pelo django

        #criando a instancia do usuario
        user  = self.model(email=email, username=username, **extra_fields)
        user.set_password(password) #seta a senha do usuario
        user.save(using=self._db) #salva o usuario no banco de dados
        return user #retorna o objecto do usuario criado

    def create_superuser(self, email: str, username: str, password: Optional[str]=None, **extra_fields: Any)-> 'User':

        #setando os campos obrigatorios do superuser
        extra_fields.setdefault('is_staff', True) #seta o is_staff como true
        extra_fields.setdefault('is_superuser', True) #seta o is_superuser como true
        extra_fields.setdefault('status', 'ACTIVE') #seta o status como true

        #verificando os campos obrigatórios do superuser
        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superuser deve ter is_superuser=True.')

        #salvando o objecto
        return self.create_user(email, username, password, **extra_fields)