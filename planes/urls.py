from django.urls import path
from .views import ver_constancia_pdf
from .views import agenda_view
from . import views

urlpatterns = [
    path('constancia/<int:plan_id>/', ver_constancia_pdf, name='ver_constancia_pdf'),
    path('agenda/', agenda_view, name='agenda'),
    path('comprobante/', views.comprobante_view, name='comprobante'),
]