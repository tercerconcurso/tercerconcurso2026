from django.urls import path
from .views import ver_constancia_pdf
from .views import agenda_view

urlpatterns = [
    path('constancia/<int:plan_id>/', ver_constancia_pdf, name='ver_constancia_pdf'),
    path('agenda/', agenda_view, name='agenda'),
    path('agenda/comprobante/', views.comprobante_view, name='comprobante'),
]