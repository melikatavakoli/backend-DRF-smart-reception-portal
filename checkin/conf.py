from django.conf import settings

DEFAULTS = {
    "GET_USER_BY_IDENTIFIER": None,
    "GENERATE_OTP": None,
    "STORE_OTP": None,
    "SEND_OTP": None,
    "VERIFY_OTP": None,
    "GENERATE_REGISTER_CODE": None,
    "REPRESENT_CHECKIN": None,
    "GET_TV_DASHBOARD": None,
}

USER_SETTINGS = getattr(settings, "CHECKIN", {})


def package_setting(name):
    return USER_SETTINGS.get(name, DEFAULTS.get(name))
