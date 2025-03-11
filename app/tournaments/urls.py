from django.urls import (
    path,
    include
    )

from rest_framework.routers import DefaultRouter

from tournaments import views

router = DefaultRouter()
router.register('tournaments', views.TournamentsViewset)
router.register('tevent')

app_name = 'tournament'

urlpatterns = [
    path('', include(router.urls))
]
