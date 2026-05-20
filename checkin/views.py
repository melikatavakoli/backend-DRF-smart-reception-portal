from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from calendar_app.models import AppointmentCalender
from client_registry.models import ClientRegistry
from client_registry.serializers import RegistrySendCodeSerializer, RegistryVerifyCodeSerializer, TVDashboardSerializer
from patient.models import Patient
from rest_framework.response import Response

# ==========================================================================================================================
# =========================== Registry-Send-Code View
# ==========================================================================================================================
class RegistrySendCodeView(APIView):
     authentication_classes = []
     permission_classes = []

     def post(self, request):
          serializer = RegistrySendCodeSerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          result = serializer.save()
          return Response(result, status=status.HTTP_200_OK)

# ==========================================================================================================================
# =========================== Registry-Appointments View
# ==========================================================================================================================
class RegistryAppointmentsView(APIView):
     authentication_classes = []
     permission_classes = []

     def post(self, request):
          serializer = RegistryVerifyCodeSerializer(data=request.data)
          serializer.is_valid(raise_exception=True)
          user = serializer.validated_data["user"]
          code = serializer.validated_data.get("code")

          patient = Patient.objects.filter(user=user).first()
          if not patient:
               return Response({"error": "No patient found for this user"}, status=400)

          registry_obj = ClientRegistry.objects.create(
               user=user,
               patient=patient
          )

          today = timezone.localdate()

          appointments = AppointmentCalender.objects.filter(
               patient=patient,
               appointment_date=today
          ).prefetch_related("medical_service") 

          appointments_data = []
          for app in appointments:
              medical_services = []
              if app.medical_service:
                  medical_services.append({
                      "id": str(app.medical_service.id),
                      "title": app.medical_service.title
                  })
              appointments_data.append({
                    "id": str(app.id),
                    "type": app.type,
                    "status": app.status,
                    "medical_service": medical_services,
                    "section": {
                         "id": app.section.id if app.section else None,
                         "title": app.section.title if app.section else None,
                         # "number": app.section.number if app.section and hasattr(app.section, "number") else None,
                         # "number": app.section.number if app.number else None,
                    },
               })

          return Response(
               {
                    "appointments": appointments_data,
                    "user": {
                         "id": str(user.id),
                         "first_name": str(user.first_name),
                         "last_name": str(user.last_name),
                         "full_name": f"{user.first_name} {user.last_name}",
                         "file_id": str(user.file_id),
                         "national_id": str(user.national_id)
                    },
                    "registry": {
                         "id": str(registry_obj.id),
                         "register_code": registry_obj.register_code
                    },
                    "today": today
               },
               status=status.HTTP_200_OK
          )

# ==========================================================================================================================
# =========================== TV-Dashboard APIView
# ==========================================================================================================================
class TVDashboardAPIView(APIView):
     authentication_classes = []
     permission_classes = []
     
     def get(self, request):
          section_id = request.query_params.get("section_id")
          serializer = TVDashboardSerializer(instance={})
          serializer.context["section_id"] = section_id
          data = serializer.data
          return Response(data)