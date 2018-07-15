from django.urls import path
from . import views

app_name = "iplDataRepresentation"

urlpatterns = [
    path('', views.index, name='index'),
    path('matchesPerYear', views.matches_per_year, name='matchesPerYear'),
    path('matchesWonPerYear', views.matches_won_per_year, name='matchesWonPerYear'),
    path('economicalBowlerIn2015', views.economical_bowler_in_2015, name='economicalBowlerIn2015'),
    path('extraRunsIn2016', views.extra_runs_in_2016, name='extraRunsIn2016'),
    path('story', views.better_decision, name='story'),
]
