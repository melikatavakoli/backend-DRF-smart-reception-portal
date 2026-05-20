from django.db import models

class KioskStatus(models.TextChoices):
    waiting = "waiting", "در انتظار" 
    ready = "ready", "آماده است" 
    enter = "enter", "ورود"  
