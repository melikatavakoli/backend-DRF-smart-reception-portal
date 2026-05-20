from django.contrib import admin

from import_export import fields

from common.export import BaseModelResource
from common.admin import BaseAuditAdmin, SoftDeleteListFilter
from client_registry.models import ClientRegistry


class ClientRegistryResource(BaseModelResource):
    id = fields.Field(attribute='id', column_name='id')
    patient = fields.Field(attribute='patient__id', column_name='patient_id')
    patient_name = fields.Field(attribute='patient__description', column_name='patient_description')
    user = fields.Field(attribute='user__full_name', column_name='user__full_name')
    appointment = fields.Field(attribute='appointment__id', column_name='appointment_id')
    status = fields.Field(attribute='status', column_name='status')
    register_code = fields.Field(attribute='register_code', column_name='register_code')

    class Meta:
        model = ClientRegistry
        fields = ('id', 'patient', 'patient_name', 'user', 'appointment', 'status', 'register_code')
        import_id_fields = ('register_code',)

@admin.register(ClientRegistry)
class ClientRegistryAdmin(BaseAuditAdmin):
    resource_class = ClientRegistryResource
    list_display = ('register_code', 'patient', 'appointment', 'status', '_is_deleted')
    search_fields = ('register_code', 'patient__description',)
    list_filter = (SoftDeleteListFilter, 'status',)
