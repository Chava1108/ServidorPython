from rest_framework import serializers
from .models import * 

class ClaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clase
        fields = '__all__' # Trae todos los campos

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