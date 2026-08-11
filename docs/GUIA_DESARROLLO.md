# 👨‍💻 Guía de Desarrollo - POOGraph

## 📋 Tabla de Contenidos

1. [Convenciones de Código](#convenciones-de-código)
2. [Estructura de Componentes](#estructura-de-componentes)
3. [Gestión de Estado](#gestión-de-estado)
4. [API y Servicios](#api-y-servicios)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Performance](#performance)
8. [Deployment](#deployment)

---

## 🎨 Convenciones de Código

### Frontend (TypeScript/Angular)

#### Nombres
```typescript
// Componentes: PascalCase
export class AreaDeTrabajoComponent { }

// Servicios: PascalCase + Service
export class CodeService { }

// Interfaces: PascalCase
export interface Proyecto { }

// Variables: camelCase
let archivoActivo: any;

// Constantes: UPPER_SNAKE_CASE
const API_URL = 'http://localhost:8000';

// Archivos: kebab-case
area-de-trabajo.component.ts
```

#### Estructura de Componente
```typescript
@Component({
  selector: 'app-nombre',
  templateUrl: './nombre.component.html',
  styleUrls: ['./nombre.component.scss']
})
export class NombreComponent implements OnInit {
  // 1. Propiedades públicas
  mostrarEditor: boolean = false;
  
  // 2. ViewChild
  @ViewChild('codeContent') codeContent!: ElementRef;
  
  // 3. Constructor (inyección de dependencias)
  constructor(
    private service: MiServicio,
    private router: Router
  ) {}
  
  // 4. Lifecycle hooks
  ngOnInit(): void {
    this.inicializar();
  }
  
  ngOnDestroy(): void {
    this.limpiar();
  }
  
  // 5. Métodos públicos
  public abrirArchivo(): void { }
  
  // 6. Métodos privados
  private inicializar(): void { }
}
```

#### Observables
```typescript
// Usar async pipe cuando sea posible
<div *ngIf="proyectos$ | async as proyectos">

// Unsubscribe en ngOnDestroy
ngOnDestroy() {
  this.subscription?.unsubscribe();
}

// Usar takeUntil para múltiples subscriptions
private destroy$ = new Subject<void>();

ngOnDestroy() {
  this.destroy$.next();
  this.destroy$.complete();
}

this.service.getData()
  .pipe(takeUntil(this.destroy$))
  .subscribe(data => { });
```

---

### Backend (Python/Django)

#### Nombres
```python
# Clases: PascalCase
class Usuario(AbstractBaseUser):
    pass

# Funciones/métodos: snake_case
def obtener_codigo_clase(id_clase):
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_FILE_SIZE = 1024 * 1024

# Variables: snake_case
codigo_fuente = "..."
```

#### Estructura de View
```python
@api_view(['GET', 'POST'])
def gestionar_proyectos(request):
    """
    Docstring explicando la función
    
    GET: Lista proyectos del usuario
    POST: Crea nuevo proyecto
    """
    
    # 1. Validación de entrada
    if request.method == 'POST':
        if not request.data.get('nombre'):
            return Response(
                {'error': 'Nombre requerido'},
                status=400
            )
    
    # 2. Lógica de negocio
    try:
        proyectos = Proyecto.objects.filter(...)
    except Exception as e:
        # 3. Manejo de errores
        return Response(
            {'error': str(e)},
            status=500
        )
    
    # 4. Respuesta
    return Response({
        'proyectos': proyectos
    }, status=200)
```

#### Queries Eficientes
```python
# ❌ Mal: N+1 queries
proyectos = Proyecto.objects.all()
for p in proyectos:
    clases = p.clase_set.all()  # Query por cada proyecto

# ✅ Bien: Prefetch
proyectos = Proyecto.objects.prefetch_related('clase_set').all()

# ✅ Bien: Select related (FK)
clases = Clase.objects.select_related('id_proyecto', 'id_proyecto__id_usr')
```

---

## 📦 Estructura de Componentes

### Árbol de Componentes

```
AppComponent
│
├── NavbarComponent
│   └── [Router Outlet]
│
├── LoginComponent
├── RegisterComponent
│
├── HomeComponent
│   └── FormProyectComponent (Dialog)
│
├── AreaDeTrabajoComponent
│   ├── Monaco Editor
│   ├── ngx-graph (Diagrama)
│   │   └── ShowclassComponent (Dialog)
│   │       ├── EditarFormularioComponent (Dialog)
│   │       └── FormularioComponent (Dialog)
│   └── Terminal
│
├── DashboardComponent
│   └── ng2-charts
│
└── HacerExamenComponent
    └── RealizarTestComponent
```

### Comunicación entre Componentes

#### 1. Parent → Child (Input)
```typescript
// Parent
<app-child [dato]="miDato"></app-child>

// Child
@Input() dato: string;
```

#### 2. Child → Parent (Output)
```typescript
// Child
@Output() eventoGuardar = new EventEmitter<string>();

guardar() {
  this.eventoGuardar.emit(this.valor);
}

// Parent
<app-child (eventoGuardar)="onGuardar($event)"></app-child>

onGuardar(valor: string) {
  console.log(valor);
}
```

#### 3. Service (Estado Compartido)
```typescript
// Servicio
@Injectable()
export class ProyectoCompartidoService {
  private proyectoActual = new BehaviorSubject<Proyecto | null>(null);
  proyectoActual$ = this.proyectoActual.asObservable();
  
  setProyecto(p: Proyecto) {
    this.proyectoActual.next(p);
  }
}

// Componente A (setter)
constructor(private shared: ProyectoCompartidoService) {}
seleccionar(p: Proyecto) {
  this.shared.setProyecto(p);
}

// Componente B (getter)
ngOnInit() {
  this.shared.proyectoActual$.subscribe(p => {
    this.proyecto = p;
  });
}
```

---

## 🔄 Gestión de Estado

### LocalStorage Encriptado

```typescript
// SecureStorageService
export class SecureStorageService {
  private secretKey = 'mi-clave-secreta'; // Mover a environment
  
  setItem(key: string, value: string): void {
    const encrypted = CryptoJS.AES.encrypt(
      value, 
      this.secretKey
    ).toString();
    localStorage.setItem(key, encrypted);
  }
  
  getItem(key: string): string {
    const encrypted = localStorage.getItem(key);
    if (!encrypted) return '';
    
    const decrypted = CryptoJS.AES.decrypt(
      encrypted, 
      this.secretKey
    );
    return decrypted.toString(CryptoJS.enc.Utf8);
  }
}

// Uso
this.storage.setItem('Usrid', usuario.id.toString());
const userId = this.storage.getItem('Usrid');
```

### State Management Pattern

```typescript
// Estado global simulado con BehaviorSubject
export class AppStateService {
  private state = new BehaviorSubject<AppState>({
    usuario: null,
    proyectoActual: null,
    archivoActivo: null
  });
  
  state$ = this.state.asObservable();
  
  get snapshot() {
    return this.state.value;
  }
  
  setUsuario(usuario: Usuario) {
    this.state.next({
      ...this.state.value,
      usuario
    });
  }
}
```

---

## 🌐 API y Servicios

### Estructura de Servicio

```typescript
@Injectable({
  providedIn: 'root'
})
export class CodeService {
  private apiUrl = environment.apiUrl;
  
  constructor(private http: HttpClient) {}
  
  // Métodos con tipado fuerte
  listarArchivos(idProyecto: number): Observable<Archivo[]> {
    return this.http.get<Archivo[]>(
      `${this.apiUrl}/archivos-proyecto/${idProyecto}`
    );
  }
  
  // Manejo de errores
  guardarArchivo(ruta: string, codigo: string): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/guardar-archivo`,
      { ruta, codigo }
    ).pipe(
      catchError(this.handleError)
    );
  }
  
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Error desconocido';
    
    if (error.error instanceof ErrorEvent) {
      // Error del cliente
      errorMessage = error.error.message;
    } else {
      // Error del servidor
      errorMessage = `Error ${error.status}: ${error.message}`;
    }
    
    return throwError(() => new Error(errorMessage));
  }
}
```

### Interceptors

```typescript
// auth.interceptor.ts
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler) {
    const token = localStorage.getItem('token');
    
    if (token) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      return next.handle(cloned);
    }
    
    return next.handle(req);
  }
}

// app.module.ts
providers: [
  {
    provide: HTTP_INTERCEPTORS,
    useClass: AuthInterceptor,
    multi: true
  }
]
```

### Retry Logic

```typescript
compilarProyecto(id: number): Observable<any> {
  return this.http.post(`${this.apiUrl}/compilar-proyecto`, { id }).pipe(
    retry(2), // Reintentar 2 veces
    timeout(30000), // Timeout de 30 segundos
    catchError(this.handleError)
  );
}
```

---

## 🧪 Testing

### Unit Tests (Frontend)

```typescript
// area-de-trabajo.component.spec.ts
describe('AreaDeTrabajoComponent', () => {
  let component: AreaDeTrabajoComponent;
  let fixture: ComponentFixture<AreaDeTrabajoComponent>;
  let codeService: jasmine.SpyObj<CodeService>;
  
  beforeEach(async () => {
    const codeServiceSpy = jasmine.createSpyObj('CodeService', [
      'listarArchivos',
      'guardarArchivo'
    ]);
    
    await TestBed.configureTestingModule({
      declarations: [ AreaDeTrabajoComponent ],
      providers: [
        { provide: CodeService, useValue: codeServiceSpy }
      ]
    }).compileComponents();
    
    codeService = TestBed.inject(CodeService) as jasmine.SpyObj<CodeService>;
  });
  
  beforeEach(() => {
    fixture = TestBed.createComponent(AreaDeTrabajoComponent);
    component = fixture.componentInstance;
  });
  
  it('should create', () => {
    expect(component).toBeTruthy();
  });
  
  it('should load files on init', () => {
    const mockFiles = [{ nombre: 'Main.java', ruta: '/Main.java' }];
    codeService.listarArchivos.and.returnValue(of(mockFiles));
    
    component.ngOnInit();
    
    expect(codeService.listarArchivos).toHaveBeenCalled();
    expect(component.listaArchivos).toEqual(mockFiles);
  });
  
  it('should save file before opening new one', () => {
    component.archivoActivo = { ruta: '/Persona.java' };
    component.code = 'public class Persona {}';
    codeService.guardarArchivo.and.returnValue(of({}));
    
    component.abrirArchivo({ ruta: '/Main.java' });
    
    expect(codeService.guardarArchivo).toHaveBeenCalledWith(
      '/Persona.java',
      'public class Persona {}'
    );
  });
});
```

### Unit Tests (Backend)

```python
# tests.py
from django.test import TestCase
from core.models import Usuario, Proyecto, Clase

class ProyectoTestCase(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            username='test',
            email='test@test.com'
        )
        
    def test_crear_proyecto(self):
        """Verifica que se pueda crear un proyecto"""
        proyecto = Proyecto.objects.create(
            nombre='MiProyecto',
            id_usr=self.usuario,
            lenguaje='java'
        )
        
        self.assertEqual(proyecto.nombre, 'MiProyecto')
        self.assertEqual(proyecto.lenguaje, 'java')
        
    def test_proyecto_debe_tener_clase_main(self):
        """Todo proyecto debe tener una clase Main"""
        proyecto = Proyecto.objects.create(
            nombre='MiProyecto',
            id_usr=self.usuario,
            lenguaje='java'
        )
        
        main = Clase.objects.create(
            nombre='Main',
            nivel='public',
            id_proyecto=proyecto
        )
        
        clases = Clase.objects.filter(id_proyecto=proyecto)
        self.assertEqual(clases.count(), 1)
        self.assertEqual(clases.first().nombre, 'Main')
```

### Integration Tests

```python
from rest_framework.test import APITestCase
from rest_framework import status

class APIIntegrationTest(APITestCase):
    def test_crear_y_listar_proyecto(self):
        # Crear usuario
        self.client.post('/api/register/', {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'password123'
        })
        
        # Login
        response = self.client.post('/api/login/', {
            'username': 'test',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Crear proyecto
        response = self.client.post('/proyecto', {
            'nombre': 'MiProyecto',
            'lenguaje': 'java'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Listar proyectos
        response = self.client.get('/proyecto/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
```

---

## 🐛 Debugging

### Frontend (Chrome DevTools)

#### Breakpoints en TypeScript
```typescript
// En el código
debugger; // Pausa ejecución

// En DevTools > Sources
// Clic en número de línea para breakpoint
```

#### Angular DevTools Extension

```bash
# Instalar extensión de Chrome
# Permite inspeccionar:
# - Component tree
# - Change detection
# - Dependency injection
```

#### Console Logging Efectivo

```typescript
// ❌ Mal
console.log(miObjeto);

// ✅ Bien: Etiqueta y expansión
console.log('Usuario cargado:', miObjeto);

// ✅ Mejor: Usar grupos
console.group('Carga de Proyecto');
console.log('ID:', id);
console.log('Nombre:', nombre);
console.log('Clases:', clases);
console.groupEnd();

// ✅ Warnings y Errors
console.warn('Advertencia: Archivo grande');
console.error('Error crítico:', error);

// ✅ Tablas
console.table(listaArchivos);
```

### Backend (Django Debug Toolbar)

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...
]

INTERNAL_IPS = ['127.0.0.1']
```

#### Logging en Django

```python
import logging
logger = logging.getLogger(__name__)

def compilar_proyecto(request):
    logger.info(f'Compilando proyecto {proyecto_id}')
    
    try:
        resultado = compilador.ejecutar()
        logger.debug(f'Output: {resultado}')
    except Exception as e:
        logger.error(f'Error en compilación: {e}', exc_info=True)
        
    return Response(...)
```

---

## ⚡ Performance

### Frontend Optimizations

#### Lazy Loading de Módulos

```typescript
// app-routing.module.ts
const routes: Routes = [
  {
    path: 'dashboard',
    loadChildren: () => import('./dashboard/dashboard.module')
      .then(m => m.DashboardModule)
  }
];
```

#### Change Detection Strategy

```typescript
@Component({
  selector: 'app-mi-componente',
  templateUrl: './mi-componente.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush // Solo detecta cambios con @Input o eventos
})
export class MiComponente { }
```

#### TrackBy en ngFor

```typescript
// Template
<div *ngFor="let archivo of archivos; trackBy: trackByRuta">
  {{ archivo.nombre }}
</div>

// Component
trackByRuta(index: number, archivo: Archivo): string {
  return archivo.ruta;
}
```

#### Debounce en Búsquedas

```typescript
searchControl = new FormControl('');

ngOnInit() {
  this.searchControl.valueChanges
    .pipe(
      debounceTime(300),
      distinctUntilChanged()
    )
    .subscribe(query => {
      this.buscar(query);
    });
}
```

### Backend Optimizations

#### Database Indexes

```python
class Clase(models.Model):
    nombre = models.CharField(max_length=128, db_index=True)
    id_proyecto = models.ForeignKey(
        'Proyecto', 
        models.DO_NOTHING, 
        db_index=True
    )
```

#### Pagination

```python
from rest_framework.pagination import PageNumberPagination

class ProyectoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@api_view(['GET'])
def listar_proyectos(request):
    proyectos = Proyecto.objects.all()
    paginator = ProyectoPagination()
    result_page = paginator.paginate_queryset(proyectos, request)
    serializer = ProyectoSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
```

#### Caching

```python
from django.core.cache import cache

def get_clases_proyecto(id_proyecto):
    cache_key = f'clases_proyecto_{id_proyecto}'
    clases = cache.get(cache_key)
    
    if not clases:
        clases = Clase.objects.filter(id_proyecto=id_proyecto)
        cache.set(cache_key, clases, timeout=300)  # 5 minutos
        
    return clases
```

---

## 🚀 Deployment

### Build de Producción

#### Frontend
```bash
cd frontend

# Build con optimizaciones
ng build --configuration production

# Output en dist/
# - Minificación
# - Tree shaking
# - AOT compilation
# - Lazy loading
```

#### Backend
```bash
cd backend_tesis

# Collectstatic (archivos estáticos)
python manage.py collectstatic --noinput

# Compilar requirements
pip freeze > requirements.txt
```

### Docker Production

```dockerfile
# frontend/Dockerfile.prod
FROM node:14 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build -- --configuration production

FROM nginx:alpine
COPY --from=build /app/dist/tesis /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```dockerfile
# backend/Dockerfile.prod
FROM python:3.9-slim
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    default-jdk \
    g++ \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt
RUN pip install gunicorn

COPY . .

EXPOSE 8000
CMD ["gunicorn", "backend_tesis.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Environment Variables

```typescript
// frontend/src/environments/environment.prod.ts
export const environment = {
  production: true,
  apiUrl: 'https://api.poograph.com'
};
```

```python
# backend/settings.py
import os
from pathlib import Path

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'clases'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'root'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}
```

### CI/CD con GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy POOGraph

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '14'
          
      - name: Test Frontend
        run: |
          cd frontend
          npm ci
          npm run test -- --watch=false --browsers=ChromeHeadless
          
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Test Backend
        run: |
          cd backend_tesis
          pip install -r requirements-docker.txt
          python manage.py test
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and Push Docker Images
        run: |
          docker-compose build
          docker-compose push
          
      - name: Deploy to Server
        run: |
          # SSH y comandos de deploy
```

---

## 📚 Recursos Adicionales

### Angular
- [Angular Docs](https://angular.io/docs)
- [RxJS Docs](https://rxjs.dev/)
- [Angular Material](https://material.angular.io/)

### Django
- [Django Docs](https://docs.djangoproject.com/)
- [DRF Docs](https://www.django-rest-framework.org/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)

### Testing
- [Jasmine Docs](https://jasmine.github.io/)
- [Karma Docs](https://karma-runner.github.io/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)

---

**¡Feliz Desarrollo! 🚀**

*Última actualización: Julio 2026*

