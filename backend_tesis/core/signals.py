from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .utils import registrar_xapi 

@receiver(user_logged_in)
def log_login(sender, user, request, **kwargs):
    if user and getattr(user, 'is_admin', False):
        return
    registrar_xapi(user.id, "inició_sesión", "Plataforma Web")

@receiver(user_logged_out)
def log_logout(sender, user, request, **kwargs):
    # Ojo: A veces user puede ser Anonymous si la sesión ya murió, validamos:
    if user and user.username:
        if getattr(user, 'is_admin', False):
            return
        registrar_xapi(user.id, "cerró_sesión", "Plataforma Web")