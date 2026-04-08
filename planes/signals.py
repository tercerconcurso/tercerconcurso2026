# @receiver(post_save, sender=Plan)
# def crear_resumen(sender, instance, created, **kwargs):
#     if created and not ResumenPlan.objects.filter(plan=instance).exists():
#         ResumenPlan.objects.create(
#             plan=instance,
#             correo="",
#             telefono="",
#             rol_avaluo="",
#             tenencia="",
#             superficie_total=0,
#             coordenada_norte=0,
#             coordenada_este=0
#         )