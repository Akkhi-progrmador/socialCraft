from django.db import models
from uuid import uuid4 #pra gerar o uuid4 do perfil do usário o pk

# My models in profiles

class Profile(models.Model):

    #classe que disponibliza choices em dicionário pra facilitar o django de interpretar
    class CountryChoices(models.TextChoices):
        franca = 'FR', 'frança' 
        united_stade = 'US', 'estados unidos'
        angola = 'AO', 'angola'
        espanha = 'ES', 'espanha'

    class LanguageChoices(models.TextChoices): 
        frances = 'FR', 'françês'
        ingles = 'EN', 'inglês'
        portugues = 'PT', 'português'
        espanha = 'ES', 'espanhol'


    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE) #relação 1:1 com o user personalizado
    display_name = models.CharField(max_length=50) #nome que aparece no frontend
    bio = models.TextField(blank=True, max_length=500)
    avatar_url = models.URLField(blank=True) #caminho da url do arquivo de avatar do perfil

    #herdam as choices das classes acima
    country = models.CharField(max_length=2, choices=CountryChoices.choices)
    language = models.CharField(max_length=2, choices=LanguageChoices.choices)

    birth_date = models.DateField() #não visivel no frontend
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
