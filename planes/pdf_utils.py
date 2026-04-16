from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.conf import settings
import os
from datetime import datetime
from reportlab.platypus import Table, Paragraph, TableStyle


def generar_pdf_constancia(planes):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="constancia.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    styleN = styles["Normal"]

    # Logos
    logo_seremi = os.path.join(settings.BASE_DIR, 'planes', 'static', 'images', 'seremi.png')
    logo_gore = os.path.join(settings.BASE_DIR, 'planes', 'static', 'images', 'gore.png')

    from reportlab.platypus import Table

    logos = []

    if os.path.exists(logo_seremi):
        img1 = Image(logo_seremi, width=100, height=50, kind='proportional')
    else:
        img1 = ""

    if os.path.exists(logo_gore):
        img2 = Image(logo_gore, width=110, height=55, kind='proportional')
    else:
        img2 = ""

    logos.append([img1, "", img2])

    tabla_logos = Table(logos, colWidths=[200, 100, 200])
    tabla_logos.setStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ])

    elements.append(tabla_logos)
    elements.append(Spacer(1, 8))

    

    # Título
    from reportlab.lib.styles import ParagraphStyle

    titulo_style = ParagraphStyle(
        'TituloCustom',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=1,  # centrado
        spaceAfter=6,
    )

    elements.append(Paragraph("CONSTANCIA DE RECEPCIÓN DE PLANES DE MANEJO", titulo_style))
    elements.append(Paragraph("Apoyo al Mejoramiento de la Fertilidad en Sistemas Agropecuarios Productivos", styleN))
    elements.append(Paragraph("Región de Los Ríos - Código BIP 40013271-0 - Tercer Concurso 2026", styleN))

    elements.append(Spacer(1, 15))

    numero_recepcion = planes[0].numero if planes else ""
    fecha_hora = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    elements.append(Paragraph(f"N° Recepción: {numero_recepcion}", styleN))
    elements.append(Paragraph(f"Fecha y hora: {fecha_hora}", styleN))

    elements.append(Spacer(1, 10))

    # Operador
    if planes:
        operador = planes[0]

        elements.append(Paragraph("<b>Profesional que entrega:</b>", styleN))
        elements.append(Paragraph(f"Nombre: {operador.nombre_operador}", styleN))
        elements.append(Paragraph(f"RUT: {operador.rut_operador}", styleN))
        elements.append(Paragraph(f"Correo: {operador.correo_operador}", styleN))

    elements.append(Spacer(1, 10))

    # Usuario
    usuario = planes[0].usuario if planes else None
    if usuario:
        nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
        elements.append(Paragraph(f"Funcionario receptor: {nombre_completo or usuario.username}", styleN))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Cantidad de planes: {len(planes)}</b>", styleN))

    elements.append(Spacer(1, 15))

    # TABLA (CORREGIDA)
    data = [["N°", "Agricultor", "RUT", "Comuna", "Sector", "Concurso"]]

    for plan in planes:
        data.append([
            str(plan.numero),
            Paragraph(plan.nombre_agricultor, styleN),
            plan.rut_agricultor,
            Paragraph(plan.comuna, styleN),
            Paragraph(plan.sector, styleN),
            Paragraph(plan.concurso, styleN),
        ])

    tabla = Table(data, colWidths=[30, 140, 80, 80, 90, 70])

    tabla.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    elements.append(tabla)

    elements.append(Spacer(1, 40))

    # Firmas
    firma_tabla = Table([
    ["_______________________________", "_______________________________"]
    ["Firma Profesional que Entrega", "Firma Funcionario Receptor"]
    ], colWidths=[250, 250])

    from reportlab.platypus import TableStyle

    firma_tabla.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))

    elements.append(Spacer(1, 40))
    elements.append(firma_tabla)

    return response