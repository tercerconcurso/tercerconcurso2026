from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Plan
from .pdf_utils import generar_pdf_constancia


def home(request):
    return render(request, 'home.html')


def ver_constancia_pdf(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)

    from datetime import datetime

    fecha = plan.fecha_ingreso.date()

    planes = Plan.objects.filter(
        rut_operador=plan.rut_operador.strip(),
        fecha_ingreso__date=fecha
    ).order_by('numero')

    return generar_pdf_constancia(list(planes))

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.db import connection

@login_required
def reset_secuencia(request):

    if not request.user.is_superuser:
        return HttpResponseForbidden("No autorizado")

    try:
        with connection.cursor() as cursor:
            cursor.execute("ALTER SEQUENCE planes_plan_numero_seq RESTART WITH 1;")

        return HttpResponse("✔️ Secuencia reiniciada correctamente")

    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")