from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from datetime import datetime
import threading

from .models import Plan, Agenda
from .pdf_utils import generar_pdf_constancia


def home(request):
    return render(request, 'home.html')


def ver_constancia_pdf(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)

    fecha = plan.fecha_ingreso.date()

    planes = Plan.objects.filter(
        rut_operador=plan.rut_operador.strip(),
        fecha_ingreso__date=fecha
    ).order_by('numero')

    return generar_pdf_constancia(list(planes))


# ======================
# ENVÍO DE CORREO ASYNC
# ======================
def enviar_correo_async(nombre, correo, fecha, hora):
    def tarea():
        try:
            fecha_formateada = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d-%m-%Y")

            send_mail(
                'Confirmación de reserva',
                f'''Hola {nombre},

Tu hora ha sido agendada correctamente.

📅 Fecha: {fecha_formateada}
⏰ Hora: {hora}

Si necesitas modificar o cancelar tu hora, por favor contáctanos.

Saludos,
Equipo Programa Fertilidad Los Ríos
''',
                None,
                [correo],
                fail_silently=True,
            )
        except Exception as e:
            print("Error correo:", e)

    threading.Thread(target=tarea).start()


# ======================
# AGENDA
# ======================
def agenda_view(request):

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')

        # validar campos
        if not nombre or not correo or not fecha or not hora:
            return redirect('/agenda/?error=campos')

        # bloquear fines de semana
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        if fecha_obj.weekday() >= 5:
            return redirect(f'/agenda/?error=findesemana&fecha={fecha}')

        # validar horario
        horas_permitidas = [
            "09:00", "09:30",
            "10:00", "10:30",
            "11:00", "11:30",
            "12:00", "12:30",
            "15:00", "15:30",
            "16:00", "16:30"
        ]

        if hora not in horas_permitidas:
            return redirect(f'/agenda/?error=horario&fecha={fecha}')

        # validar duplicado
        existe = Agenda.objects.filter(fecha=fecha, hora=hora).exists()
        if existe:
            return redirect(f'/agenda/?error=ocupado&fecha={fecha}')

        # guardar
        Agenda.objects.create(
            nombre=nombre,
            correo=correo,
            fecha=fecha,
            hora=hora
        )

        # enviar correo en segundo plano
        enviar_correo_async(nombre, correo, fecha, hora)

        # 🔴 ESTE ERA EL PROBLEMA (faltaba)
        return redirect(f'/agenda/?success=1&fecha={fecha}')

    # ======================
    # GET
    # ======================
    error = request.GET.get('error')
    success = request.GET.get('success')
    fecha_filtro = request.GET.get('fecha')

    mensaje_error = None
    mensaje_success = None

    if error == 'campos':
        mensaje_error = 'Debe completar todos los campos'
    elif error == 'ocupado':
        mensaje_error = 'Ese horario ya está reservado'
    elif error == 'horario':
        mensaje_error = 'Horario no permitido (solo entre 09:00 y 16:30)'
    elif error == 'findesemana':
        mensaje_error = 'No se permiten reservas en fines de semana'

    if success:
        mensaje_success = 'Reserva realizada correctamente'

    # horas ocupadas
    if fecha_filtro:
        ocupadas = list(
            Agenda.objects.filter(fecha=fecha_filtro)
            .values_list('hora', flat=True)
        )
    else:
        ocupadas = []

    # bloques
    horas = [
        "09:00", "09:30",
        "10:00", "10:30",
        "11:00", "11:30",
        "12:00", "12:30",
        "15:00", "15:30",
        "16:00", "16:30"
    ]

    return render(request, 'agenda.html', {
        'error': mensaje_error,
        'success': mensaje_success,
        'ocupadas': ocupadas,
        'horas': horas,
        'fecha_filtro': fecha_filtro,
    })