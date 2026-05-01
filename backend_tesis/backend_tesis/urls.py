from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome),

    # Subida de Archivos
    path('upload', views.upload_file),

    # --- CLASES ---
    path('clasesProyectId/<int:id>', views.get_clases_proyecto),
    path('clasesId', views.get_clase_id),
    path('clases', views.crear_clase), # POST
    path('clase/<int:id>', views.gestionar_clase_individual), # DELETE

    # --- ATRIBUTOS ---
    # POST: agregar (inyecta en archivo)
    path('atributos', views.gestionar_atributos),

    # --- FUNCIONES ---
    # POST: agregar (inyecta en archivo)
    path('funciones', views.gestionar_funciones),

    # --- HERENCIA ---
    # POST: agregar extends/herencia al archivo fuente
    path('herencia', views.agregar_herencia),

    # --- INFO COMPLETA DE CLASE (propios + heredados, desde archivos) ---
    path('clase-info/<int:id_clase>', views.obtener_info_completa_clase),
    path('clase-info/<int:id_clase>/codigo-funcion', views.obtener_codigo_funcion),

    # --- USUARIOS Y PROYECTOS ---
    # GET: lista, POST: crear
    path('usuario', views.gestionar_usuarios),
    
    path('proyecto/<int:id>', views.get_proyectos_usuario),
    path('proyectoIndividual', views.get_proyecto_individual),
    path('proyecto', views.crear_proyecto),

    path('clases/<int:id>/codigo', views.obtener_codigo_clase),
    path('archivos-proyecto/<int:proyecto_id>', views.listar_archivos_proyecto),
    path('leer-archivo', views.leer_archivo_fisico),
    path('compilar-proyecto', views.compilar_y_ejecutar_proyecto),
    path('guardar-archivo', views.guardar_archivo_cambios),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/register/', views.register_view, name='register'),
    path('api/tooltip-log', views.registrar_tooltip),
    path('api/dashboard-analytics', views.dashboard_analytics),

    # --- EXÁMENES ---
    path('examenes/crear', views.crear_examen),
    path('examenes', views.listar_examenes),
    path('examenes/disponibles/<int:id_estudiante>', views.listar_examenes_disponibles),
    path('examenes/<int:id_examen>/estudiante', views.obtener_examen_estudiante),
    path('examenes/iniciar', views.iniciar_intento_examen),
    path('examenes/enviar', views.enviar_respuestas_examen),
    path('examenes/resultados/<int:id_intento>', views.resultados_examen_estudiante),
]

# Configuración para servir imágenes en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
