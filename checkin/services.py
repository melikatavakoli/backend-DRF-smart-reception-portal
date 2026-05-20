from django.conf import settings
from django.utils.module_loading import import_string

def get_hook(name, default=None):
    hooks = getattr(settings, "QueueEntry_HOOKS", {})
    path = hooks.get(name)
    if not path:
        return default
    return import_string(path)
