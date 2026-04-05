from django.urls import path
from .views import ver_constancia_pdf

urlpatterns = [
    path('constancia/<int:plan_id>/', ver_constancia_pdf, name='ver_constancia_pdf'),
]