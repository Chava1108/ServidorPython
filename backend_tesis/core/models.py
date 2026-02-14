# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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
    OPCIONES_LENGUAJE = [
            ('java', 'Java'),
            ('cpp', 'C++ (G++)'),
        ]
    lenguaje = models.CharField(
        max_length=10, 
        choices=OPCIONES_LENGUAJE, 
        default='java' 
    )
    class Meta:
        managed = True
        db_table = 'proyecto'

    
class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError('El usuario debe tener un username')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password) # Encripta la contraseña
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    # --- TUS CAMPOS EXISTENTES (Déjalos tal cual) ---
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=100, unique=True)
    
    # El campo 'password' YA EXISTE en AbstractBaseUser, 
    # así que puedes borrar tu definición de password si la tenías,
    # o dejarla si quieres configurar max_length específico.
    
    # --- CAMPOS NUEVOS REQUERIDOS POR DJANGO ---
    # Django necesita estos flags para saber si el usuario puede entrar
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UsuarioManager()

    # Configuración clave
    USERNAME_FIELD = 'username' # Campo para loguearse
    REQUIRED_FIELDS = ['email'] # Campos obligatorios al crear superuser

    class Meta:
        # IMPORTANTE: Asegúrate que esto coincida con el nombre real de tu tabla
        # para que no cree una nueva.
        db_table = 'usuario' 
        managed = True

    def __str__(self):
        return self.username

    # Métodos requeridos para que funcione el Admin de Django
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


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
