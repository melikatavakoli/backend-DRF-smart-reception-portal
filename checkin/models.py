from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class QueueEntry(models.Model):
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
     register_code = models.CharField(max_length=300, null=True, blank=True)
     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="registry_item")
     object_id = models.PositiveIntegerField()
     content_object = GenericForeignKey('content_type', 'object_id')
     appointment_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, related_name="registry_appointment")
     appointment_id = models.PositiveIntegerField(null=True, blank=True)
     appointment = GenericForeignKey('appointment_type', 'appointment_id')
     status = models.CharField(max_length=100, null=True, blank=True)

     class Meta:
          db_table = 'queue_entry'
          ordering = ('-updated_at',)

     def __str__(self):
          return str(self.register_code or "No Code")

     @staticmethod
     def generate_register_code():
          today = timezone.now().date()
          last = QueueEntry.objects.filter(
               created_at__date=today
          ).aggregate(max_code=Max("register_code"))["max_code"]
          if not last:
               return "100"
          return str(int(last) + 1)