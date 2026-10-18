"""
Modelos de POOGRAPH.

Estándar de nombres en MySQL (octubre de 2026):
- tc_<plural>: tablas de catálogo        (tc_usuarios, tc_proyectos, tc_clases...)
- tr_<plural>: tablas de relación         (tr_herencias, tr_intentos_examen, tr_respuestas)
- tb_<nombre>: bitácoras                  (tb_log_actividad)
- La llave primaria es id_<entidad> y cada llave foránea se llama igual que la llave
  primaria a la que apunta (tc_proyectos.id_usuario -> tc_usuarios.id_usuario).

Los nombres de los ATRIBUTOS de Python no cambiaron (por ejemplo, Proyecto.id_usr): solo
cambiaron db_table y db_column, así que la API y el frontend siguen igual.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class Atributos(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_atributo')
    nivel = models.CharField(max_length=25)
    nombre = models.CharField(max_length=128, blank=True, null=True)
    tipo = models.CharField(max_length=128, blank=True, null=True)
    id_clase = models.ForeignKey('Clase', models.DO_NOTHING, db_column='id_clase', blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'tc_atributos'


class Clase(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_clase')
    nivel = models.CharField(max_length=20)
    nombre = models.CharField(max_length=128)
    id_proyecto = models.ForeignKey('Proyecto', models.DO_NOTHING, db_column='id_proyecto')
    imagen = models.CharField(max_length=50)
    path_archivo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_clases'
        unique_together = (('nombre', 'id_proyecto'),)


class Funciones(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_funcion')
    nivel = models.CharField(max_length=25)
    nombre = models.CharField(max_length=128, blank=True, null=True)
    tipo = models.CharField(max_length=128, blank=True, null=True)
    id_clase = models.ForeignKey(Clase, models.DO_NOTHING, db_column='id_clase', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_funciones'


class Herencia(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_herencia')
    id_clasePadre = models.ForeignKey(
        Clase, 
        models.DO_NOTHING, 
        db_column='id_clase_padre',
        related_name='hijos_set' 
    )

    id_claseHijo = models.OneToOneField(
        Clase, 
        models.DO_NOTHING, 
        db_column='id_clase_hija',
        related_name='herencia_info'
    )

    class Meta:
        managed = False
        db_table = 'tr_herencias'

class Proyecto(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_proyecto')
    nombre = models.CharField(max_length=60)
    id_usr = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='id_usuario')
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
        db_table = 'tc_proyectos'

    
class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('El usuario debe tener un username')
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields,
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
    id = models.BigAutoField(primary_key=True, db_column='id_usuario')
    # --- TUS CAMPOS EXISTENTES (Déjalos tal cual) ---
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=100, unique=True)
    
    # El campo 'password' YA EXISTE en AbstractBaseUser, 
    # así que puedes borrar tu definición de password si la tenías,
    # o dejarla si quieres configurar max_length específico.
    
    # --- CAMPOS DE LEARNING ANALYTICS ---
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    NIVEL_SOCIOECONOMICO_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio_bajo', 'Medio-Bajo'),
        ('medio', 'Medio'),
        ('medio_alto', 'Medio-Alto'),
        ('alto', 'Alto'),
    ]
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True, default='')
    edad = models.PositiveIntegerField(null=True, blank=True)
    nivel_socioeconomico = models.CharField(max_length=20, choices=NIVEL_SOCIOECONOMICO_CHOICES, blank=True, default='')
    semestre = models.PositiveIntegerField(null=True, blank=True)

    # --- GRUPO DEL ESTUDIO (lo asigna el administrador) ---
    # experimental: usa la plataforma completa · control: solo presenta exámenes
    # pruebas: alumnos que probaron la plataforma antes del estudio · sinteticos: simulador
    GRUPO_SIN_ASIGNAR = 'sin_asignar'
    GRUPO_CHOICES = [
        ('sin_asignar', 'Sin asignar'),
        ('experimental', 'Experimental'),
        ('control', 'Control'),
        ('pruebas', 'Pruebas'),
        ('sinteticos', 'Sintéticos'),
    ]
    GRUPOS_ESTUDIO = ('experimental', 'control')
    grupo = models.CharField(max_length=15, choices=GRUPO_CHOICES, default=GRUPO_SIN_ASIGNAR)
    
    # --- CAMPOS NUEVOS REQUERIDOS POR DJANGO ---
    # Django necesita estos flags para saber si el usuario puede entrar
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UsuarioManager()

    # Configuración clave
    USERNAME_FIELD = 'username' # Campo para loguearse
    REQUIRED_FIELDS = ['email'] # Campos obligatorios al crear superuser

    class Meta:
        db_table = 'tc_usuarios'
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
    id = models.BigAutoField(primary_key=True, db_column='id_log')
    # id del usuario guardado como texto (no es llave foránea: también registra eventos sin sesión)
    usuario = models.CharField(max_length=100, db_column='id_usuario')
    accion = models.CharField(max_length=50)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True 
        db_table = 'tb_log_actividad'

    def __str__(self):
        return f"{self.fecha} - {self.usuario} - {self.accion}"


# --- MODELOS PARA EXÁMENES ---

class Examen(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_examen')
    titulo = models.CharField(max_length=255)
    creado_por = models.ForeignKey(Usuario, models.CASCADE, db_column='id_usuario', related_name='examenes_creados')
    fecha_disponible = models.DateTimeField()
    duracion_minutos = models.IntegerField(default=30)
    activo = models.BooleanField(default=True)
    # pre / post: instrumentos de la tesis (ganancia de Hake) · practica: cualquier otro examen
    TIPO_CHOICES = [('pre', 'Pre-test'), ('post', 'Post-test'), ('practica', 'Práctica')]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='practica')
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = True
        db_table = 'tc_examenes'

    def __str__(self):
        return f"{self.titulo} - {self.fecha_disponible}"


class Pregunta(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_pregunta')
    examen = models.ForeignKey(Examen, models.CASCADE, db_column='id_examen', related_name='preguntas')
    texto = models.TextField()
    orden = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'tc_preguntas'

    def __str__(self):
        return f"Pregunta {self.orden}: {self.texto[:50]}"


class Opcion(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_opcion')
    pregunta = models.ForeignKey(Pregunta, models.CASCADE, db_column='id_pregunta', related_name='opciones')
    texto = models.CharField(max_length=500)
    es_correcta = models.BooleanField(default=False)
    letra = models.CharField(max_length=1)  # A, B, C, D

    class Meta:
        managed = True
        db_table = 'tc_opciones'

    def __str__(self):
        return f"{self.letra}. {self.texto}"


class IntentoExamen(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_intento')
    examen = models.ForeignKey(Examen, models.CASCADE, db_column='id_examen', related_name='intentos')
    estudiante = models.ForeignKey(Usuario, models.CASCADE, db_column='id_usuario', related_name='intentos_examen')
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    completado = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'tr_intentos_examen'
        unique_together = (('examen', 'estudiante'),)

    def __str__(self):
        return f"{self.estudiante} - {self.examen} - {self.calificacion}"


class RespuestaEstudiante(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id_respuesta')
    intento = models.ForeignKey(IntentoExamen, models.CASCADE, db_column='id_intento', related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, models.CASCADE, db_column='id_pregunta')
    opcion_elegida = models.ForeignKey(Opcion, models.CASCADE, db_column='id_opcion', blank=True, null=True)
    es_correcta = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'tr_respuestas'
        unique_together = (('intento', 'pregunta'),)

    def __str__(self):
        return f"Resp: {self.pregunta} -> {self.opcion_elegida}"
