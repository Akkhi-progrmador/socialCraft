
from django.urls import path
from .views import ProfileDetailCreateView

urlpatterns = [
    path('me/', ProfileDetailCreateView.as_view(), name='profile'),
]