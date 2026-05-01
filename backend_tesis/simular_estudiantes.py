"""
Script de simulación: 35 estudiantes usando POOGraph durante 2 semanas.
Ejecutar con: python manage.py shell < simular_estudiantes.py
O directamente configurando Django settings.
"""
import os
import sys
import shutil
import random
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_tesis.settings')
import django
django.setup()

from django.utils import timezone
from core.models import (
    Usuario, Proyecto, Clase, Atributos, Funciones, 
    Herencia, LogActividad, Examen, Pregunta, Opcion, IntentoExamen
)
from rest_framework.authtoken.models import Token
from django.conf import settings

# ============================================================
# FASE 1: LIMPIAR TODO (excepto admin_test)
# ============================================================
print("=" * 60)
print("FASE 1: Limpiando base de datos y archivos...")
print("=" * 60)

# Obtener admin_test para preservarlo
try:
    admin_user = Usuario.objects.get(username='admin_test')
    admin_id = admin_user.id
    print(f"  [OK] admin_test encontrado (id={admin_id})")
except Usuario.DoesNotExist:
    admin_user = None
    admin_id = None
    print("  [!] admin_test no encontrado, se limpiará todo")

# Limpiar tablas en orden (por dependencias FK)
# Usar raw SQL para tablas con managed=False
from django.db import connection

with connection.cursor() as cursor:
    # Desactivar FK checks temporalmente
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    # Limpiar intentos de examen
    IntentoExamen.objects.all().delete()
    print("  [OK] IntentoExamen limpiado")
    
    # Limpiar opciones y preguntas
    Opcion.objects.all().delete()
    Pregunta.objects.all().delete()
    Examen.objects.all().delete()
    print("  [OK] Exámenes limpiados")
    
    # Limpiar log
    LogActividad.objects.all().delete()
    print("  [OK] LogActividad limpiado")
    
    # Limpiar herencia (managed=False, usar raw)
    cursor.execute("DELETE FROM herencia;")
    print("  [OK] Herencia limpiado")
    
    # Limpiar funciones y atributos (managed=False)
    cursor.execute("DELETE FROM funciones;")
    cursor.execute("DELETE FROM atributos;")
    print("  [OK] Funciones y Atributos limpiados")
    
    # Limpiar clases (managed=False)
    cursor.execute("DELETE FROM clase;")
    print("  [OK] Clases limpiado")
    
    # Limpiar proyectos
    Proyecto.objects.all().delete()
    print("  [OK] Proyectos limpiado")
    
    # Limpiar tokens (excepto admin)
    if admin_user:
        Token.objects.exclude(user=admin_user).delete()
    else:
        Token.objects.all().delete()
    print("  [OK] Tokens limpiados")
    
    # Limpiar usuarios (excepto admin_test)
    if admin_user:
        Usuario.objects.exclude(id=admin_id).delete()
    else:
        Usuario.objects.all().delete()
    print("  [OK] Usuarios limpiados (admin_test preservado)")
    
    # Reactivar FK checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

# Limpiar carpeta codigos_fuente
codigos_path = os.path.join(settings.BASE_DIR, 'codigos_fuente')
if os.path.exists(codigos_path):
    shutil.rmtree(codigos_path)
os.makedirs(codigos_path)
print("  [OK] Carpeta codigos_fuente limpiada y recreada")

print("\n")

# ============================================================
# FASE 2: REGISTRAR 35 ESTUDIANTES
# ============================================================
print("=" * 60)
print("FASE 2: Registrando 35 estudiantes...")
print("=" * 60)

nombres_hombres = [
    "Carlos", "Miguel", "Andrés", "José", "Luis", "Daniel", "Fernando",
    "Ricardo", "Alejandro", "David", "Eduardo", "Gabriel", "Javier",
    "Roberto", "Diego", "Sergio", "Manuel", "Raúl", "Pablo", "Héctor"
]
nombres_mujeres = [
    "María", "Ana", "Laura", "Sofía", "Valentina", "Camila", "Isabella",
    "Daniela", "Fernanda", "Gabriela", "Mariana", "Paola", "Andrea",
    "Lucía", "Carolina"
]
apellidos = [
    "García", "Rodríguez", "Martínez", "López", "Hernández", "González",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera",
    "Gómez", "Díaz", "Morales", "Reyes", "Cruz", "Ortiz", "Gutiérrez",
    "Chávez", "Ramos", "Vargas", "Castillo", "Jiménez", "Moreno",
    "Romero", "Herrera", "Medina", "Aguilar", "Vega", "Castro",
    "Mendoza", "Guerrero", "Delgado", "Ríos"
]

generos = ['M', 'F', 'O']
niveles_socio = ['bajo', 'medio_bajo', 'medio', 'medio_alto', 'alto']
semestres = [3, 4, 5, 6, 7, 8]

estudiantes = []

for i in range(35):
    # Generar datos realistas
    if i < 20:
        nombre = nombres_hombres[i]
        genero = 'M'
    elif i < 35:
        nombre = nombres_mujeres[i - 20]
        genero = 'F'
    
    apellido = apellidos[i]
    matricula = f"{320000 + i:06d}"
    username = f"al{matricula}"
    email = f"al{matricula}@edu.uaa.mx"
    password = "Test1234!"
    edad = random.randint(19, 25)
    nivel_socio = random.choice(niveles_socio)
    semestre = random.choice(semestres)
    
    user = Usuario.objects.create_user(
        username=username,
        email=email,
        password=password,
        name=f"{nombre} {apellido}",
        genero=genero,
        edad=edad,
        nivel_socioeconomico=nivel_socio,
        semestre=semestre,
    )
    estudiantes.append(user)
    print(f"  [{i+1:02d}/35] {username} - {nombre} {apellido} (Semestre {semestre})")

print(f"\n  [OK] {len(estudiantes)} estudiantes registrados\n")

# ============================================================
# FASE 3: CREAR PROYECTOS CON EJERCICIOS
# ============================================================
print("=" * 60)
print("FASE 3: Creando proyectos con ejercicios de POO...")
print("=" * 60)

# Definición de los 4 ejercicios (basados en ejercicios.txt)
ejercicios = [
    {
        "nombre": "Sobrecarga de Metodos",
        "clases": {
            "Pedido": {
                "codigo": '''public class Pedido {
    private String producto;
    private int cantidad;
    private double precioUnitario;
    private String destino;

    public Pedido(String producto, int cantidad, double precioUnitario) {
        this.producto = producto;
        this.cantidad = cantidad;
        this.precioUnitario = precioUnitario;
        this.destino = "Local";
    }

    public double calcularTotal() {
        return cantidad * precioUnitario;
    }

    public double calcularTotal(double descuento) {
        double subtotal = cantidad * precioUnitario;
        return subtotal - (subtotal * descuento / 100);
    }

    public double calcularTotal(double descuento, double envio) {
        double subtotal = cantidad * precioUnitario;
        return subtotal - (subtotal * descuento / 100) + envio;
    }

    public String mostrarResumen() {
        return "Pedido: " + producto + " x" + cantidad + " - Total: $" + calcularTotal();
    }
}''',
                "atributos": [
                    ("producto", "String", "private"),
                    ("cantidad", "int", "private"),
                    ("precioUnitario", "double", "private"),
                    ("destino", "String", "private"),
                ],
                "funciones": [
                    ("calcularTotal", "double", "public"),
                    ("calcularTotal", "double", "public"),
                    ("calcularTotal", "double", "public"),
                    ("mostrarResumen", "String", "public"),
                ],
                "padre": None,
            },
            "Main": {
                "codigo": '''public class Main {
    public static void main(String[] args) {
        Pedido p = new Pedido("Laptop", 2, 15000.0);
        System.out.println(p.mostrarResumen());
        System.out.println("Con descuento: $" + p.calcularTotal(10));
        System.out.println("Con descuento y envio: $" + p.calcularTotal(10, 250));
    }
}''',
                "atributos": [],
                "funciones": [("main", "void", "public")],
                "padre": None,
            },
        },
    },
    {
        "nombre": "Sobrecarga de Constructores",
        "clases": {
            "ArticuloCientifico": {
                "codigo": '''public class ArticuloCientifico {
    private String titulo;
    private String autor;
    private int anioPublicacion;
    private String revista;
    private String doi;

    public ArticuloCientifico(String titulo, String autor) {
        this.titulo = titulo;
        this.autor = autor;
        this.anioPublicacion = 2024;
        this.revista = "Sin asignar";
        this.doi = "";
    }

    public ArticuloCientifico(String titulo, String autor, int anio) {
        this.titulo = titulo;
        this.autor = autor;
        this.anioPublicacion = anio;
        this.revista = "Sin asignar";
        this.doi = "";
    }

    public ArticuloCientifico(String titulo, String autor, int anio, String revista, String doi) {
        this.titulo = titulo;
        this.autor = autor;
        this.anioPublicacion = anio;
        this.revista = revista;
        this.doi = doi;
    }

    public String getCita() {
        return autor + " (" + anioPublicacion + "). " + titulo + ". " + revista;
    }

    public String getInfo() {
        return "Titulo: " + titulo + "\\nAutor: " + autor + "\\nAnio: " + anioPublicacion;
    }
}''',
                "atributos": [
                    ("titulo", "String", "private"),
                    ("autor", "String", "private"),
                    ("anioPublicacion", "int", "private"),
                    ("revista", "String", "private"),
                    ("doi", "String", "private"),
                ],
                "funciones": [
                    ("getCita", "String", "public"),
                    ("getInfo", "String", "public"),
                ],
                "padre": None,
            },
            "Main": {
                "codigo": '''public class Main {
    public static void main(String[] args) {
        ArticuloCientifico a1 = new ArticuloCientifico("IA en Educacion", "Dr. Lopez");
        ArticuloCientifico a2 = new ArticuloCientifico("Redes Neuronales", "Dra. Garcia", 2023);
        ArticuloCientifico a3 = new ArticuloCientifico("Deep Learning", "Dr. Martinez", 2022, "IEEE", "10.1109/xyz");
        System.out.println(a1.getCita());
        System.out.println(a2.getCita());
        System.out.println(a3.getInfo());
    }
}''',
                "atributos": [],
                "funciones": [("main", "void", "public")],
                "padre": None,
            },
        },
    },
    {
        "nombre": "Herencia Bancaria",
        "clases": {
            "Cuenta": {
                "codigo": '''public class Cuenta {
    protected String titular;
    protected double saldo;
    protected String numeroCuenta;

    public Cuenta(String titular, double saldo, String numeroCuenta) {
        this.titular = titular;
        this.saldo = saldo;
        this.numeroCuenta = numeroCuenta;
    }

    public void depositar(double monto) {
        if (monto > 0) {
            saldo += monto;
        }
    }

    public boolean retirar(double monto) {
        if (monto > 0 && monto <= saldo) {
            saldo -= monto;
            return true;
        }
        return false;
    }

    public String getInfo() {
        return "Cuenta: " + numeroCuenta + " | Titular: " + titular + " | Saldo: $" + saldo;
    }
}''',
                "atributos": [
                    ("titular", "String", "protected"),
                    ("saldo", "double", "protected"),
                    ("numeroCuenta", "String", "protected"),
                ],
                "funciones": [
                    ("depositar", "void", "public"),
                    ("retirar", "boolean", "public"),
                    ("getInfo", "String", "public"),
                ],
                "padre": None,
            },
            "CuentaAhorros": {
                "codigo": '''public class CuentaAhorros extends Cuenta {
    private double tasaInteres;

    public CuentaAhorros(String titular, double saldo, String numeroCuenta, double tasaInteres) {
        super(titular, saldo, numeroCuenta);
        this.tasaInteres = tasaInteres;
    }

    public void aplicarInteres() {
        double interes = saldo * tasaInteres / 100;
        saldo += interes;
    }

    public String getInfo() {
        return super.getInfo() + " | Tasa: " + tasaInteres + "%";
    }
}''',
                "atributos": [
                    ("tasaInteres", "double", "private"),
                ],
                "funciones": [
                    ("aplicarInteres", "void", "public"),
                    ("getInfo", "String", "public"),
                ],
                "padre": "Cuenta",
            },
            "CuentaCorriente": {
                "codigo": '''public class CuentaCorriente extends Cuenta {
    private double limiteCredito;

    public CuentaCorriente(String titular, double saldo, String numeroCuenta, double limiteCredito) {
        super(titular, saldo, numeroCuenta);
        this.limiteCredito = limiteCredito;
    }

    public boolean retirar(double monto) {
        if (monto > 0 && monto <= (saldo + limiteCredito)) {
            saldo -= monto;
            return true;
        }
        return false;
    }

    public String getInfo() {
        return super.getInfo() + " | Limite credito: $" + limiteCredito;
    }
}''',
                "atributos": [
                    ("limiteCredito", "double", "private"),
                ],
                "funciones": [
                    ("retirar", "boolean", "public"),
                    ("getInfo", "String", "public"),
                ],
                "padre": "Cuenta",
            },
            "Main": {
                "codigo": '''public class Main {
    public static void main(String[] args) {
        CuentaAhorros ahorro = new CuentaAhorros("Juan Perez", 10000, "AH-001", 5.0);
        CuentaCorriente corriente = new CuentaCorriente("Maria Lopez", 5000, "CC-001", 3000);
        
        ahorro.depositar(2000);
        ahorro.aplicarInteres();
        System.out.println(ahorro.getInfo());
        
        corriente.retirar(7000);
        System.out.println(corriente.getInfo());
    }
}''',
                "atributos": [],
                "funciones": [("main", "void", "public")],
                "padre": None,
            },
        },
    },
    {
        "nombre": "Polimorfismo Docente",
        "clases": {
            "Profesor": {
                "codigo": '''public class Profesor {
    protected String nombre;
    protected String departamento;
    protected int horasClase;

    public Profesor(String nombre, String departamento, int horasClase) {
        this.nombre = nombre;
        this.departamento = departamento;
        this.horasClase = horasClase;
    }

    public double calcularSalario() {
        return horasClase * 250.0;
    }

    public String getInfo() {
        return "Profesor: " + nombre + " | Depto: " + departamento + " | Salario: $" + calcularSalario();
    }
}''',
                "atributos": [
                    ("nombre", "String", "protected"),
                    ("departamento", "String", "protected"),
                    ("horasClase", "int", "protected"),
                ],
                "funciones": [
                    ("calcularSalario", "double", "public"),
                    ("getInfo", "String", "public"),
                ],
                "padre": None,
            },
            "ProfesorTitular": {
                "codigo": '''public class ProfesorTitular extends Profesor {
    private double bonoInvestigacion;
    private int publicaciones;

    public ProfesorTitular(String nombre, String departamento, int horasClase, double bonoInvestigacion, int publicaciones) {
        super(nombre, departamento, horasClase);
        this.bonoInvestigacion = bonoInvestigacion;
        this.publicaciones = publicaciones;
    }

    public double calcularSalario() {
        return super.calcularSalario() + bonoInvestigacion + (publicaciones * 500);
    }

    public String getInfo() {
        return super.getInfo() + " | Publicaciones: " + publicaciones;
    }
}''',
                "atributos": [
                    ("bonoInvestigacion", "double", "private"),
                    ("publicaciones", "int", "private"),
                ],
                "funciones": [
                    ("calcularSalario", "double", "public"),
                    ("getInfo", "String", "public"),
                ],
                "padre": "Profesor",
            },
            "Main": {
                "codigo": '''public class Main {
    public static void main(String[] args) {
        Profesor p1 = new Profesor("Ana Torres", "Sistemas", 20);
        ProfesorTitular p2 = new ProfesorTitular("Dr. Carlos Vega", "Sistemas", 15, 8000, 12);
        
        Profesor[] profesores = {p1, p2};
        for (Profesor p : profesores) {
            System.out.println(p.getInfo());
        }
    }
}''',
                "atributos": [],
                "funciones": [("main", "void", "public")],
                "padre": None,
            },
        },
    },
]

# Para cada estudiante, crear los 4 proyectos
for idx, estudiante in enumerate(estudiantes):
    uid = estudiante.id
    print(f"\n  Estudiante [{idx+1:02d}/35] {estudiante.username}:")
    
    for ej in ejercicios:
        # Crear proyecto
        proyecto = Proyecto.objects.create(
            nombre=ej["nombre"],
            id_usr=estudiante,
            lenguaje='java'
        )
        
        # Crear carpeta
        ruta_carpeta = os.path.join(
            settings.BASE_DIR, 'codigos_fuente', 
            f'usuario_{uid}', f'proyecto_{proyecto.id}'
        )
        os.makedirs(ruta_carpeta, exist_ok=True)
        
        # Mapeo de nombre_clase -> instancia Clase (para herencia)
        clases_map = {}
        
        for nombre_clase, datos_clase in ej["clases"].items():
            # Guardar archivo .java
            ruta_archivo = os.path.join(ruta_carpeta, f"{nombre_clase}.java")
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(datos_clase["codigo"])
            
            # Ruta relativa para la BD
            ruta_relativa = os.path.join(
                'codigos_fuente', f'usuario_{uid}', 
                f'proyecto_{proyecto.id}', f'{nombre_clase}.java'
            )
            
            # Crear clase en BD
            clase = Clase.objects.create(
                nombre=nombre_clase,
                id_proyecto=proyecto,
                nivel='public',
                imagen='',
                path_archivo=ruta_relativa,
            )
            clases_map[nombre_clase] = clase
            
            # Crear atributos
            for attr_nombre, attr_tipo, attr_nivel in datos_clase["atributos"]:
                Atributos.objects.create(
                    nombre=attr_nombre,
                    tipo=attr_tipo,
                    nivel=attr_nivel,
                    id_clase=clase,
                )
            
            # Crear funciones
            for func_nombre, func_tipo, func_nivel in datos_clase["funciones"]:
                Funciones.objects.create(
                    nombre=func_nombre,
                    tipo=func_tipo,
                    nivel=func_nivel,
                    id_clase=clase,
                )
        
        # Crear relaciones de herencia
        for nombre_clase, datos_clase in ej["clases"].items():
            if datos_clase["padre"] and datos_clase["padre"] in clases_map:
                from django.db import connection as conn2
                with conn2.cursor() as cur:
                    cur.execute(
                        "INSERT INTO herencia (id_clasePadre, id_claseHijo) VALUES (%s, %s)",
                        [clases_map[datos_clase["padre"]].id, clases_map[nombre_clase].id]
                    )
        
        print(f"    [OK] Proyecto '{ej['nombre']}' ({len(ej['clases'])} clases)")

print(f"\n  [OK] Proyectos creados para los 35 estudiantes\n")

# ============================================================
# FASE 4: GENERAR LOG DE ACTIVIDAD (2 semanas)
# ============================================================
print("=" * 60)
print("FASE 4: Generando log de actividad (2 semanas)...")
print("=" * 60)

# Definir rango de fechas: últimas 2 semanas
fecha_fin = timezone.now()
fecha_inicio = fecha_fin - timedelta(days=14)

# Acciones posibles con sus pesos de probabilidad
acciones = [
    ("consultó_tooltip", 35),
    ("intentó_pegar_código", 8),
    ("MOSTRAR_DIAGRAMA", 20),
    ("OCULTAR_DIAGRAMA", 15),
    ("creó_proyecto", 5),
    ("creó_clase", 10),
    ("inició_sesión", 15),
    ("cerró_sesión", 12),
    ("compiló_proyecto", 18),
    ("editó_código", 25),
]

# Palabras clave para tooltips
palabras_tooltip = [
    "class", "extends", "implements", "public", "private", "protected",
    "static", "void", "int", "double", "String", "boolean", "return",
    "new", "this", "super", "abstract", "interface", "override",
    "herencia", "polimorfismo", "encapsulamiento", "constructor",
    "método", "atributo", "objeto", "instancia"
]

# Detalles para cada acción
def generar_detalle(accion, estudiante):
    if accion == "consultó_tooltip":
        palabra = random.choice(palabras_tooltip)
        return f"Palabra: '{palabra}' (Lenguaje: java)"
    elif accion == "intentó_pegar_código":
        return "Intento de pegar código en editor (Lenguaje: java)"
    elif accion == "MOSTRAR_DIAGRAMA":
        ej = random.choice(ejercicios)
        return f"Diagrama mostrado para proyecto '{ej['nombre']}'"
    elif accion == "OCULTAR_DIAGRAMA":
        ej = random.choice(ejercicios)
        return f"Diagrama ocultado para proyecto '{ej['nombre']}'"
    elif accion == "creó_proyecto":
        ej = random.choice(ejercicios)
        return f"Proyecto '{ej['nombre']}'"
    elif accion == "creó_clase":
        clase = random.choice(["Pedido", "ArticuloCientifico", "Cuenta", "CuentaAhorros", "Profesor", "ProfesorTitular"])
        return f"Clase {clase}"
    elif accion == "inició_sesión":
        return "Login exitoso"
    elif accion == "cerró_sesión":
        return "Logout"
    elif accion == "compiló_proyecto":
        exito = random.choice([True, True, True, False])
        ej = random.choice(ejercicios)
        if exito:
            return f"Compilación exitosa - Proyecto '{ej['nombre']}'"
        else:
            return f"Error de compilación - Proyecto '{ej['nombre']}'"
    elif accion == "editó_código":
        clase = random.choice(["Pedido", "ArticuloCientifico", "Cuenta", "CuentaAhorros", "CuentaCorriente", "Profesor", "ProfesorTitular"])
        return f"Editó clase {clase}"
    return ""

# Generar eventos
total_eventos = 0
logs_bulk = []

for estudiante in estudiantes:
    # Cada estudiante tiene entre 3-7 sesiones en 2 semanas
    num_sesiones = random.randint(3, 7)
    
    for sesion in range(num_sesiones):
        # Día aleatorio en las 2 semanas
        dia_offset = random.randint(0, 13)
        fecha_sesion = fecha_inicio + timedelta(days=dia_offset)
        
        # Hora de inicio entre 8am y 10pm
        hora_inicio = random.randint(8, 22)
        minuto_inicio = random.randint(0, 59)
        fecha_sesion = fecha_sesion.replace(
            hour=hora_inicio, minute=minuto_inicio, second=0, microsecond=0
        )
        
        # Login
        logs_bulk.append(LogActividad(
            usuario=str(estudiante.id),
            accion="inició_sesión",
            detalle="Login exitoso",
            fecha=fecha_sesion,
        ))
        
        # Actividades durante la sesión (5-25 acciones)
        num_acciones = random.randint(5, 25)
        tiempo_actual = fecha_sesion
        
        for _ in range(num_acciones):
            # Avanzar tiempo 30s-5min
            tiempo_actual += timedelta(seconds=random.randint(30, 300))
            
            # Elegir acción ponderada (excluir login/logout)
            acciones_sesion = [(a, p) for a, p in acciones if a not in ("inició_sesión", "cerró_sesión")]
            total_peso = sum(p for _, p in acciones_sesion)
            r = random.randint(1, total_peso)
            acum = 0
            accion_elegida = acciones_sesion[0][0]
            for a, p in acciones_sesion:
                acum += p
                if r <= acum:
                    accion_elegida = a
                    break
            
            detalle = generar_detalle(accion_elegida, estudiante)
            logs_bulk.append(LogActividad(
                usuario=str(estudiante.id),
                accion=accion_elegida,
                detalle=detalle,
                fecha=tiempo_actual,
            ))
        
        # Logout
        tiempo_actual += timedelta(seconds=random.randint(60, 300))
        logs_bulk.append(LogActividad(
            usuario=str(estudiante.id),
            accion="cerró_sesión",
            detalle="Logout",
            fecha=tiempo_actual,
        ))
    
    total_eventos += len([l for l in logs_bulk if l.usuario == str(estudiante.id)])

# Insertar en bulk
LogActividad.objects.bulk_create(logs_bulk, batch_size=500)
print(f"  [OK] {len(logs_bulk)} eventos de log generados para 35 estudiantes")
print(f"  [OK] Rango: {fecha_inicio.strftime('%Y-%m-%d')} a {fecha_fin.strftime('%Y-%m-%d')}")

# Estadísticas
from collections import Counter
conteo_acciones = Counter(l.accion for l in logs_bulk)
print("\n  Distribución de acciones:")
for accion, count in conteo_acciones.most_common():
    print(f"    {accion}: {count}")

print("\n")
print("=" * 60)
print("SIMULACIÓN COMPLETADA")
print("=" * 60)
print(f"  - Estudiantes: 35")
print(f"  - Proyectos por estudiante: 4")
print(f"  - Total proyectos: {Proyecto.objects.count()}")
print(f"  - Total clases: {Clase.objects.count()}")
print(f"  - Total eventos log: {LogActividad.objects.count()}")
print(f"  - Periodo: 2 semanas")
print(f"  - admin_test preservado: {'Sí' if admin_user else 'No'}")
print("=" * 60)
