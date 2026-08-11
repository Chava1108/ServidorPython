from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome),

    # Subida de Archivos
    path('api/upload', views.upload_file),

    # --- CLASES ---
    path('api/clasesProyectId/<int:id>', views.get_clases_proyecto),
    path('api/clasesId', views.get_clase_id),
    path('api/clases', views.crear_clase), # POST
    path('api/clase/<int:id>', views.gestionar_clase_individual), # DELETE

    # --- ATRIBUTOS ---
    # POST: agregar (inyecta en archivo)
    path('api/atributos', views.gestionar_atributos),

    # --- FUNCIONES ---
    # POST: agregar (inyecta en archivo)
    path('api/funciones', views.gestionar_funciones),

    # --- HERENCIA ---
    # POST: agregar extends/herencia al archivo fuente
    path('api/herencia', views.agregar_herencia),

    # --- INFO COMPLETA DE CLASE (propios + heredados, desde archivos) ---
    path('api/clase-info/<int:id_clase>', views.obtener_info_completa_clase),
    path('api/clase-info/<int:id_clase>/codigo-funcion', views.obtener_codigo_funcion),

    # --- USUARIOS Y PROYECTOS ---
    # GET: lista, POST: crear
    path('api/usuario', views.gestionar_usuarios),
    
    path('api/proyecto/<int:id>', views.get_proyectos_usuario),
    path('api/proyectoIndividual', views.get_proyecto_individual),
    path('api/proyecto', views.crear_proyecto),

    path('api/clases/<int:id>/codigo', views.obtener_codigo_clase),
    path('api/archivos-proyecto/<int:proyecto_id>', views.listar_archivos_proyecto),
    path('api/leer-archivo', views.leer_archivo_fisico),
    path('api/compilar-proyecto', views.compilar_y_ejecutar_proyecto),
    path('api/guardar-archivo', views.guardar_archivo_cambios),
    
    # Estos ya lo tenían, se quedan igual
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/register/', views.register_view, name='register'),
    path('api/tooltip-log', views.registrar_tooltip),
    path('api/dashboard-analytics/', views.dashboard_analytics),

    # --- EXÁMENES ---
    path('api/examenes/crear', views.crear_examen),
    path('api/examenes', views.listar_examenes),
    path('api/examenes/disponibles/<int:id_estudiante>', views.listar_examenes_disponibles),
    path('api/examenes/<int:id_examen>/estudiante', views.obtener_examen_estudiante),
    path('api/examenes/iniciar', views.iniciar_intento_examen),
    path('api/examenes/enviar', views.enviar_respuestas_examen),
    path('api/examenes/resultados/<int:id_intento>', views.resultados_examen_estudiante),
]

# Servir archivos media (imágenes) - funciona en desarrollo y producción
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)