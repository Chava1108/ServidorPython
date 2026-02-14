from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario  # Importa tu modelo personalizado

class UsuarioAdmin(UserAdmin):
    # Configuración para que el Admin sepa qué columnas mostrar
    # ya que tu tabla no es la estándar.
    
    # Columnas que se ven en la lista de usuarios
    list_display = ('username', 'email', 'name', 'is_active', 'is_admin')
    
    # Filtros laterales
    list_filter = ('is_admin', 'is_active')
    
    # Campos por los que se puede buscar
    search_fields = ('username', 'email', 'name')
    
    # Ordenamiento
    ordering = ('username',)

    # Como usamos un modelo personalizado, debemos definir cómo se ven los formularios
    # fieldsets controla la vista de "Editar Usuario"
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_admin')}),
    )

    # add_fieldsets controla la vista de "Agregar Usuario"
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'name'),
        }),
    )

    filter_horizontal = ()

admin.site.register(Usuario, UsuarioAdmin)