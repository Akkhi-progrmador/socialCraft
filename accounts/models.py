from django.db import models
from uuid import uuid4 #pra gerar os ids unicos aleatorios e seguros
from django.contrib.auth.models import AbstractUser #AbstractUser usado pra personalizar o user!
from django.contrib.auth.validators import UnicodeUsernameValidator #verifica caracteres validos pra o username
from django.db.models.functions import Lower

from .manager import UserManager
from typing import ClassVar

# My models in accounts

class User(AbstractUser):

    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        BANNED = 'BANNED', 'Banned'

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=40, validators=[UnicodeUsernameValidator()]) # validar quais caracteres/formato o username pode ter
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    email = models.EmailField(unique=True)  #em
    email_verified_at = models.DateTimeField(null=True, blank=True) #email_verified_at é nulo por padrão, mas pode ser preenchido quando o email for verificado
    created_at = models.DateTimeField(auto_now_add=True) #created_at é definido automaticamente quando o objeto é criado
    updated_at = models.DateTimeField(auto_now=True)  #update_at é atualizado automaticamente toda vez que o objeto é salvo  d

    USERNAME_FIELD = 'email'          # Define o email como o campo de login
    REQUIRED_FIELDS = ['username']    # Move o username para os campos obrigatórios no terminal

    objects: ClassVar[UserManager] = UserManager()  # pyright: ignore[reportIncompatibleVariableOverride] # Use o UserManager personalizado para criar usuários e superusuários

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower('username'), name='unique_lower_username'),
        ]
