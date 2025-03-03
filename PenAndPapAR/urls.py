from django.urls import path
from PenAndPapAR.views import CharacterStatsView

urlpatterns = [
    path('stats/', CharacterStatsView.as_view(), name='char-stats'),
]
