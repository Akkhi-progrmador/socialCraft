from rest_framework import generics, mixins
from .models import Profile
from rest_framework.serializers import BaseSerializer
from .serializers import ProfileReadSerializer, ProfileWriteSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import Http404

# My views from profile

#herdar da generic view e das mixins
class ProfileDetailCreateView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):

    permission_classes = [IsAuthenticated] # Define a permissão para usuários autenticados

    def get_queryset(self): #pyright: ignore[reportIncompatibleMethodOverride]
        # Retorna apenas o perfil do usuário autenticado 
        return Profile.objects.filter(user=self.request.user) 

    def get_object(self): #pyright: ignore[reportIncompatibleMethodOverride]
        #busca do modelo com relação one-to-one com o usuário autenticado sem criar se não existir
        try:
            obj = Profile.objects.get(user=self.request.user)
            return obj
        except Profile.DoesNotExist:
            raise Http404("Profile does not exist for the authenticated user.")
    
    # Definimos um serializador padrão. Isso resolve o erro do Pylance!
    serializer_class = ProfileReadSerializer 

    #função que define qual serializador usar baseado nos verbos http
    def get_serializer_class(self)-> type[BaseSerializer]: #type:ignore
        if self.request.method == 'GET':
            return ProfileReadSerializer # Retorna imediatamente se for GET
        
        return ProfileWriteSerializer # Para POST, PUT, PATCH, retorna o de escrita

    #função usada pra criar um novo perfil de usuário, chamando o método create do mixin CreateModelMixin
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    #função usada pra atualizar um perfil de usuário, chamando o método update do mixin UpdateModelMixin
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    #função usada pra atualizar parcialmente um perfil de usuário, chamando o método partial_update do mixin UpdateModelMixin
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    #função usada pra recuperar um perfil de usuário, chamando o método retrieve do mixin RetrieveModelMixin
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Associa o perfil ao usuário autenticado ao criar
        serializer.save(user=self.request.user)

