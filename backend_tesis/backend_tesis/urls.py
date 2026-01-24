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

    # --- ATRIBUTOS (UNIFICADO) ---
    # GET: lista, POST: crear
    path('atributos', views.gestionar_atributos),
    # PUT: actualizar uno, DELETE: borrar todos de una clase
    path('atributos/<int:id>', views.gestionar_atributo_individual),
    # STORED PROCEDURE
    path('atributosHeredados/<int:id>', views.get_atributos_heredados),
    path('atributosClases/<int:id>', views.obtenerAtributosClase),

    # --- FUNCIONES (UNIFICADO) ---
    # GET: lista, POST: crear
    path('funciones', views.gestionar_funciones),
    # PUT: actualizar uno, DELETE: borrar todos de una clase
    path('funciones/<int:id>', views.gestionar_funcion_individual),
    path('funcionesClases/<int:id>', views.obtenerFuncionesClase),
    # --- HERENCIA ---
    # GET: lista (por proyecto), DELETE: borrar hijo
    path('herencia/<int:id>', views.gestionar_herencia_hijo),
    # POST: crear
    path('herencia', views.crear_herencia),
    # DELETE: borrar padre
    path('herenciaP/<int:id>', views.eliminar_herencia_padre),

    # --- USUARIOS Y PROYECTOS ---
    # GET: lista, POST: crear
    path('usuario', views.gestionar_usuarios),
    
    path('proyecto/<int:id>', views.get_proyectos_usuario),
    path('proyectoIndividual', views.get_proyecto_individual),
    path('proyecto', views.crear_proyecto),

    # --- TESIS: PARSER Y LOGS ---
    path('parsear', views.parsear_codigo),
    path('logs', views.registrar_log),

    path('clases/<int:id>/codigo', views.obtener_codigo_clase),
    path('archivos-proyecto/<int:proyecto_id>', views.listar_archivos_proyecto),
    path('leer-archivo', views.leer_archivo_fisico),
    path('compilar-proyecto', views.compilar_y_ejecutar_proyecto),
    path('guardar-archivo', views.guardar_archivo_cambios) 
]

# Configuración para servir imágenes en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
