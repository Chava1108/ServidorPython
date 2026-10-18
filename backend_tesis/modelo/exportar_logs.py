"""
Exporta los datos REALES de la base de datos para el modelo y el análisis:
  datos/log_actividad_real.csv  -> eventos (con el grupo del alumno)
  datos/calificaciones.csv      -> pre-test, post-test y ganancia de Hake por alumno

Excluye a los administradores y al grupo 'sinteticos'. Las fechas se escriben en hora local.

Uso, desde la carpeta del backend (en el servidor: /var/www/backend):
    venv/bin/python manage.py shell < modelo/exportar_logs.py
"""
import csv
import os

from django.conf import settings
from django.utils import timezone

from core.models import IntentoExamen, LogActividad, Usuario

alumnos = Usuario.objects.filter(is_admin=False).exclude(grupo='sinteticos')
grupo_de = {str(u.id): u.grupo for u in alumnos}
logs = LogActividad.objects.filter(usuario__in=list(grupo_de)).order_by('fecha')

carpeta = os.path.join(settings.BASE_DIR, 'datos')
os.makedirs(carpeta, exist_ok=True)

ruta_logs = os.path.join(carpeta, 'log_actividad_real.csv')
with open(ruta_logs, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id', 'usuario', 'grupo', 'accion', 'detalle', 'fecha'])
    for log in logs.iterator():
        w.writerow([log.id, log.usuario, grupo_de.get(log.usuario, ''), log.accion, log.detalle or '',
                    timezone.localtime(log.fecha).strftime('%Y-%m-%d %H:%M:%S')])

# Último intento completado de cada tipo (pre / post) por alumno
notas = {}
for i in (IntentoExamen.objects.filter(completado=True, estudiante__in=alumnos, calificacion__isnull=False,
                                       examen__tipo__in=('pre', 'post'))
          .select_related('examen').order_by('fecha_fin')):
    notas.setdefault(i.estudiante_id, {})[i.examen.tipo] = float(i.calificacion)

ruta_notas = os.path.join(carpeta, 'calificaciones.csv')
completos = 0
with open(ruta_notas, 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['usuario', 'grupo', 'pre', 'post', 'ganancia'])
    for u in alumnos.order_by('grupo', 'id'):
        pre, post = notas.get(u.id, {}).get('pre'), notas.get(u.id, {}).get('post')
        g = round((post - pre) / (100 - pre), 4) if pre is not None and post is not None and pre < 100 else ''
        completos += pre is not None and post is not None
        w.writerow([u.id, u.grupo, '' if pre is None else pre, '' if post is None else post, g])

print(f"Exportados {logs.count()} eventos de {logs.values('usuario').distinct().count()} alumnos a {ruta_logs}")
print(f"Calificaciones de {alumnos.count()} alumnos ({completos} con pre y post) en {ruta_notas}")
print("Alumnos por grupo:", {g: list(grupo_de.values()).count(g) for g in sorted(set(grupo_de.values()))})
