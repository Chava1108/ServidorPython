from rest_framework import serializers
from .models import * 
from .utils import obtener_padre_desde_codigo
from django.conf import settings
import os

class ClaseSerializer(serializers.ModelSerializer):
    # ESTA ES LA LÍNEA QUE FALTA:
    # Le indica a Django que busque el método 'get_nombre_padre'
    nombre_padre = serializers.SerializerMethodField()

    class Meta:
        model = Clase
        fields = '__all__'

    def get_nombre_padre(self, obj):
        if not obj.path_archivo:
            return None
        # Usar settings.BASE_DIR para compatibilidad con cualquier servidor
        ruta = os.path.join(settings.BASE_DIR, obj.path_archivo)
        lenguaje = obj.id_proyecto.lenguaje 
        
        # Llamamos a tu función de extracción
        return obtener_padre_desde_codigo(ruta, lenguaje)


class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class HerenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Herencia
        fields = '__all__'

# Para las Vistas de MySQL (getatributos, getfunciones)
# Si inspectdb las detectó como modelos, úsalos así:
class VistaAtributosSerializer(serializers.ModelSerializer):
    class Meta:
        # Asegúrate que el nombre coincida con lo que hay en models.py (ej. Getatributos)
        model = Getatributos 
        fields = '__all__'

class VistaFuncionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Getfunciones
        fields = '__all__'

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogActividad
        fields = '__all__'


class AtributosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atributos # Asegúrate que tu modelo se llame así
        fields = '__all__'

class FuncionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funciones # Asegúrate que tu modelo se llame así
        fields = '__all__'


# Serializadores para Vistas SQL (Solo Lectura)
class GetFuncionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Getfunciones
        fields = '__all__'

class GetAtributosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Getatributos
        fields = '__all__'

class HerenciaFSerializer(serializers.ModelSerializer):
    Padre = serializers.CharField(source='padre')
    Hijo = serializers.CharField(source='hijo')

    class Meta:
        model = Herenciaf
        fields = ['Padre', 'Hijo', 'id_proyecto']


# --- SERIALIZADORES PARA EXÁMENES ---

class OpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcion
        fields = '__all__'


class PreguntaSerializer(serializers.ModelSerializer):
    opciones = OpcionSerializer(many=True, read_only=True)

    class Meta:
        model = Pregunta
        fields = '__all__'


class ExamenSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True)
    total_preguntas = serializers.SerializerMethodField()

    class Meta:
        model = Examen
        fields = '__all__'

    def get_total_preguntas(self, obj):
        return obj.preguntas.count()


class ExamenListSerializer(serializers.ModelSerializer):
    """Versión ligera para listar exámenes (sin preguntas completas)."""
    total_preguntas = serializers.SerializerMethodField()

    class Meta:
        model = Examen
        fields = ['id', 'titulo', 'fecha_disponible', 'duracion_minutos', 'activo', 'fecha_creacion', 'creado_por', 'total_preguntas']

    def get_total_preguntas(self, obj):
        return obj.preguntas.count()


class IntentoExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntentoExamen
        fields = '__all__'


class RespuestaEstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaEstudiante
        fields = '__all__'