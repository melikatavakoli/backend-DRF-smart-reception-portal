import uuid
import logging
from django.db.models import Prefetch
from django.contrib.auth import get_user_model
from checkin.services import get_hook
from rest_framework import serializers

User = get_user_model()
logger = logging.getLogger(__name__)


class SendCodeSerializer(serializers.Serializer):
    mobile = serializers.CharField(required=False)
    national_id = serializers.CharField(required=False)
    file_id = serializers.CharField(required=False)
    mode = serializers.CharField(required=False, default="register")

    def validate(self, attrs):
        resolve_user = get_hook("resolve_user")
        if not resolve_user:
            raise serializers.ValidationError({"error": "System configuration error."})

        mobile = attrs.get("mobile")
        national_id = attrs.get("national_id")

        """
        Case 1:
        The client provides both national_id and mobile.
        This is used to identify the user and verify that the mobile number
        """
        if national_id and mobile:
            user = resolve_user(national_id=national_id, mobile=mobile)
            
            """
            Case 2:
            The client provides only the mobile number.
            The system resolves the user by mobile and sends an OTP to that number.
            """
        elif mobile:
            user = resolve_user(mobile=mobile)
        else:
            raise serializers.ValidationError(
                {"error": "Either 'mobile' or 'national_id + mobile' must be provided."}
            )
            
        if not user:
            raise serializers.ValidationError({"error": "User not found."})
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        generate_otp = get_hook("generate_otp")
        store_otp = get_hook("store_otp")
        send_otp = get_hook("send_otp")
        code = generate_otp(user)
        store_otp(user, code)
        send_otp(user, code)
        return {"status": "success", "message": "کد با موفقیت ارسال شد."}


class VerifyCodeSerializer(serializers.Serializer):
    national_id = serializers.CharField(required=False)
    mobile = serializers.CharField(required=False)
    file_id = serializers.CharField(required=False)
    code = serializers.CharField(required=False, max_length=10)

    default_error_messages = {
        "invalid_input": "ورودی معتبر نیست. یک ترکیب معتبر ارسال کنید.",
        "mobile_not_found": "شماره موبایل برای این کاربر ثبت نشده است.",
    }

    def validate(self, data):
        national_id = data.get("national_id")
        mobile = data.get("mobile")
        file_id = data.get("file_id")
        code = data.get("code")
        resolve_user = get_hook("resolve_user")
        validate_otp = get_hook("validate_otp")
        if not resolve_user:
            raise serializers.ValidationError({
                "error": "User resolver hook is not configured."
            })
        if not validate_otp:
            raise serializers.ValidationError({
                "error": "OTP validator hook is not configured."
            })

        """
        Case 1: national_id + mobile
        """
        if national_id and mobile and not code:
            user = resolve_user(
                national_id=national_id,
                mobile=mobile,
            )
            if not user:
                raise serializers.ValidationError({
                    "error": "کاربر با اطلاعات ارسال‌شده یافت نشد."
                })
            data["user"] = user
            data["auth_case"] = "national_id_mobile"
            return data

        """
        Case 2: national_id + file_id
        """
        if national_id and file_id and not code:
            user = resolve_user(
                national_id=national_id,
                file_id=file_id,
            )
            if not user:
                raise serializers.ValidationError({
                    "error": "کاربر با اطلاعات ارسال‌شده یافت نشد."
                })
            data["user"] = user
            data["auth_case"] = "national_id_file_id"
            return data

        """
        Case 3: mobile + code
        """
        if mobile and code:
            user = resolve_user(mobile=mobile)
            if not user:
                raise serializers.ValidationError({
                    "error": "کاربر با اطلاعات ارسال‌شده یافت نشد."
                })
            is_valid = validate_otp(user=user, mobile=mobile, code=code)
            if not is_valid:
                raise serializers.ValidationError({
                    "error": "کد تایید نامعتبر است یا منقضی شده است."
                })
            data["user"] = user
            data["auth_case"] = "mobile_code"
            return data

        """
        Case 4: file_id + code
        """
        if file_id and code:
            user = resolve_user(file_id=file_id)
            if not user:
                raise serializers.ValidationError({
                    "error": "کاربر با اطلاعات ارسال‌شده یافت نشد."
                })
            user_mobile = getattr(user, "mobile", None)
            if not user_mobile:
                raise serializers.ValidationError({
                    "error": self.error_messages["mobile_not_found"]
                })
            is_valid = validate_otp(user=user, mobile=user_mobile, code=code)
            if not is_valid:
                raise serializers.ValidationError({
                    "error": "کد تایید نامعتبر است یا منقضی شده است."
                })
            data["user"] = user
            data["auth_case"] = "file_id_code"
            return data

        raise serializers.ValidationError({
            "error": self.error_messages["invalid_input"]
        })


class QueueEntrySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.CharField()
    type = serializers.CharField()
    sub_status = serializers.CharField(allow_null=True)
    register_code = serializers.CharField()
    position = serializers.CharField()
    _created_at = serializers.DateTimeField()
    room_number = serializers.CharField(allow_null=True)

    def to_representation(self, obj):
        represent_registry = get_hook("represent_registry")
        if not represent_registry:
            raise serializers.ValidationError({
                "error": "Registry representation hook is not configured."
            })
        data = represent_registry(obj)
        if not isinstance(data, dict):
            raise serializers.ValidationError({
                "error": "Registry representation hook must return a dictionary."
            })
        return super().to_representation(data)


class TVDashboardSerializer(serializers.Serializer):
    tv = serializers.SerializerMethodField()

    def get_tv(self, obj):
        get_tv_dashboard = get_hook("get_tv_dashboard")
        if not get_tv_dashboard:
            raise serializers.ValidationError({
                "error": "TV dashboard hook is not configured."
            })
        section_id = self.context.get("section_id")
        data = get_tv_dashboard(
            obj=obj,
            section_id=section_id,
            context=self.context
        )
        return data
