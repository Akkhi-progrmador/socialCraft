from rest_framework import serializers
from .models import Profile

#serializer que vai expor os campos do modelo Profile para a API, permitindo que os dados do perfil sejam convertidos em formatos como JSON para serem enviados e recebidos através das requisições HTTP. mas só pra ler sem escrever, então não precisa de validação de campos, apenas leitura. O serializer é usado para transformar os dados do modelo em uma representação serializada que pode ser facilmente transmitida pela API.
#quem dita as funções é a view
class ProfileReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['birth_date'] #excluir o campo birth_date do serializer, garantindo que essa informação não seja exposta na API. Isso é útil para proteger a privacidade do usuário e evitar que informações sensíveis sejam compartilhadas inadvertidamente. sem fields='__all__' porque não funciona junto do exclude e já envia tudo automaticamente, então não precisa definir todos os campos manualmente.
class ProfileWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        read_only_fields = ['user']
        fields = '__all__' #incluir todos os campos do modelo Profile no serializer, permitindo que os dados do perfil sejam enviados através da API. Isso é útil para criar ou atualizar perfis de usuário, garantindo que todas as informações relevantes sejam incluídas nas requisições HTTP.
        