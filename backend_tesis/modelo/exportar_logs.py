"""
Exporta los logs REALES de la base de datos a datos/log_actividad_real.csv para el modelo.

Excluye a los administradores y a los usuarios generados por simular_estudiantes.py
(los identifica por los verbos que solo usó el simulador). Las fechas se escriben en hora local.

Uso, desde la carpeta del backend (en el servidor: /var/www/backend):
    venv/bin/python manage.py shell < modelo/exportar_logs.py
"""
import csv
import os

from django.conf import settings
from django.utils import timezone

from core import analitica
from core.models import LogActividad, Usuario

admins = {str(i) for i in Usuario.objects.filter(is_admin=True).values_list('id', flat=True)}
sinteticos = set(LogActividad.objects.filter(accion__in=analitica.VERBOS_SIMULADOR)
                 .values_list('usuario', flat=True).distinct())
logs = LogActividad.objects.exclude(usuario__in=admins | sinteticos).order_by('fecha')

ruta = os.path.join(settings.BASE_DIR, 'datos', 'log_actividad_real.csv')
os.makedirs(os.path.dirname(ruta), exist_ok=True)
with open(ruta, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id', 'usuario', 'accion', 'detalle', 'fecha'])
    for log in logs.iterator():
        w.writerow([log.id, log.usuario, log.accion, log.detalle or '',
                    timezone.localtime(log.fecha).strftime('%Y-%m-%d %H:%M:%S')])

print(f"Exportados {logs.count()} eventos de {logs.values('usuario').distinct().count()} usuarios a {ruta}")
print(f"Excluidos: {len(admins)} administradores y {len(sinteticos)} usuarios sintéticos")
