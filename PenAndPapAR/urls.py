from django.urls import path
from .views import CharacterStatsList, CharacterStatsDetail

urlpatterns = [
    path('character-stats/', CharacterStatsList.as_view(), name='character-stats-list'),
    path('character-stats/<int:pk>/', CharacterStatsDetail.as_view(), name='character-stats-detail'),
]
