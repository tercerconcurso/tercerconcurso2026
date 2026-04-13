from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
import os
from django.conf import settings
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def generar_pdf_constancia(planes):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="constancia.pdf"'

    p = canvas.Canvas(response, pagesize=letter)

    y = 750

    # Rutas de los logos
    logo_seremi = os.path.join(settings.BASE_DIR, 'planes', 'static', 'images', 'seremi.png')
    logo_gore = os.path.join(settings.BASE_DIR, 'planes', 'static', 'images', 'gore.png')

    # Logo izquierda
    p.drawImage(logo_seremi, 50, 700, width=110, height=55, preserveAspectRatio=True)

    # Logo derecha
    p.drawImage(logo_gore, 440, 700, width=110, height=55, preserveAspectRatio=True)

    y -= 80

    # Título
    p.setFont("Helvetica-Bold", 12)
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(300, y, "CONSTANCIA DE RECEPCIÓN DE PLANES DE MANEJO")
    y -= 20

    p.setFont("Helvetica", 10)
    p.drawCentredString(300, y, "Apoyo al Mejoramiento de la Fertilidad en Sistemas Agropecuarios Productivos")
    y -= 15
    p.drawCentredString(300, y, "Región de Los Ríos – Código BIP 40013271-0 – Tercer Concurso 2026")
    y -= 30

    from datetime import datetime

    # Número de recepción (usamos el primero como referencia)
    numero_recepcion = planes[0].numero if planes else ""

    # Fecha y hora actual
    fecha_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    p.drawString(50, y, f"N° Recepción: {numero_recepcion}")
    y -= 15
    p.drawString(50, y, f"Fecha y hora: {fecha_hora}")
    y -= 20

    # Datos del operador
    if planes:
        operador = planes[0]

        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, "Profesional que entrega:")
        y -= 15

        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Nombre: {operador.nombre_operador}")
        y -= 15
        p.drawString(50, y, f"RUT: {operador.rut_operador}")
        y -= 15
        p.drawString(50, y, f"Correo: {operador.correo_operador}")
        y -= 25

    # Funcionario receptor
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Funcionario receptor:")
    y -= 15

    p.setFont("Helvetica", 10)
    usuario = planes[0].usuario if planes else None

    if usuario:
        nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
        
        if nombre_completo:
            p.drawString(50, y, nombre_completo)
        else:
            p.drawString(50, y, usuario.username)
    else:
        p.drawString(50, y, "-")
    y -= 15

    # Cantidad de planes
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, f"Cantidad de planes: {len(planes)}")
    y -= 30

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]

    # Tabla profesional
    data = [
        ["N°", "Agricultor", "RUT", "Comuna", "Sector", "Concurso"]
    ]

    for plan in planes:
        data.append([
            str(plan.numero),
            Paragraph(plan.nombre_agricultor, styleN),
            plan.rut_agricultor,
            Paragraph(plan.comuna, styleN),
            Paragraph(plan.sector, styleN),
            Paragraph(plan.concurso, styleN),
        ])

    tabla = Table(data, colWidths=[40, 150, 90, 80, 100, 80])

    tabla.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    # Dibujar tabla
    tabla.wrapOn(p, 50, y)
    tabla.drawOn(p, 50, y - (20 * len(data)))
    # Firmas
    y = 150

    # Línea izquierda
    p.line(100, y, 250, y)
    p.drawString(110, y - 15, "Firma Profesional que Entrega")

    # Línea derecha
    p.line(350, y, 500, y)
    p.drawString(360, y - 15, "Firma Funcionario Receptor")

    # Pie de página
    p.setFont("Helvetica", 8)

    y_footer = 30

    p.drawString(50, y_footer, "Programa de Fertilidad de Suelos – SEREMI Agricultura Región de Los Ríos")
    p.drawRightString(550, y_footer, "Página 1")

    p.showPage()
    p.save()

    return response