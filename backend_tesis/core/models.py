# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone

class Getatributos(models.Model):
    id = models.IntegerField(primary_key=True) 
    nombre = models.CharField(max_length=128)
    nivel = models.CharField(max_length=25)
    tipo = models.CharField(max_length=128)
    atributos = models.CharField(max_length=128) 

    class Meta:
        managed = False  
        db_table = 'getatributos' 


class Getfunciones(models.Model):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=128)
    nivel = models.CharField(max_length=25)
    tipo = models.CharField(max_length=128)
    funciones = models.CharField(max_length=128) 

    class Meta:
        managed = False
        db_table = 'getfunciones'


class Herenciaf(models.Model):
    # En las vistas de herencia a veces no hay ID único. 
    # Django te obligará a poner uno como primary_key. 
    # Si la vista no tiene ID, engañamos a Django poniendo primary_key=True en 'Hijo' o 'Padre'
    # (Solo para lectura funcionará bien).
    
    # Basado en tu diagrama, parece que no tiene ID propio, así que usaremos el Hijo como PK falsa
    hijo = models.CharField(db_column='Hijo', max_length=128, primary_key=True) 
    padre = models.CharField(db_column='Padre', max_length=128)
    id_proyecto = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'herenciaf'

class Atributos(models.Model):
    nivel = models.CharField(max_length=25)
    nombre = models.CharField(max_length=128, blank=True, null=True)
    tipo = models.CharField(max_length=128, blank=True, null=True)
    id_clase = models.ForeignKey('Clase', models.DO_NOTHING, db_column='id_clase', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'atributos'


class Clase(models.Model):
    nivel = models.CharField(max_length=20)
    nombre = models.CharField(max_length=128)
    id_proyecto = models.ForeignKey('Proyecto', models.DO_NOTHING, db_column='id_proyecto')
    imagen = models.CharField(max_length=50)
    path_archivo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clase'
        unique_together = (('nombre', 'id_proyecto'),)


class Funciones(models.Model):
    nivel = models.CharField(max_length=25)
    nombre = models.CharField(max_length=128, blank=True, null=True)
    tipo = models.CharField(max_length=128, blank=True, null=True)
    id_clase = models.ForeignKey(Clase, models.DO_NOTHING, db_column='id_clase', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'funciones'


class Herencia(models.Model):
    id_clasePadre = models.ForeignKey(
        Clase, 
        models.DO_NOTHING, 
        db_column='id_clasePadre', 
        related_name='hijos_set' 
    )

    id_claseHijo = models.OneToOneField(
        Clase, 
        models.DO_NOTHING, 
        db_column='id_claseHijo', 
        related_name='herencia_info'
    )

    class Meta:
        managed = False
        db_table = 'herencia'

class Proyecto(models.Model):
    nombre = models.CharField(max_length=60)
    id_usr = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usr')

    class Meta:
        managed = False
        db_table = 'proyecto'


class Usuario(models.Model):
    name = models.CharField(max_length=40)
    email = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'usuario'


class LogActividad(models.Model):
    usuario = models.CharField(max_length=100) 
    accion = models.CharField(max_length=50)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True 
        db_table = 'log_actividad'

    def __str__(self):
        return f"{self.fecha} - {self.usuario} - {self.accion}"