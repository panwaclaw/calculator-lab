from django.urls import path

from .views import IndexView, CalcView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('calc/', CalcView.as_view(), name='calc'),
]