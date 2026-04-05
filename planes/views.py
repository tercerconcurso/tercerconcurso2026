from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Plan
from .pdf_utils import generar_pdf_constancia


def home(request):
    return render(request, 'home.html')


def ver_constancia_pdf(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)

    pdf = generar_pdf_constancia([plan])  # tu función recibe lista

    return HttpResponse(pdf, content_type='application/pdf')