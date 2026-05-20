```
# Django Checkin

A reusable Django app for building OTP-based check-in and queue flows.

The app provides the API flow and structure.  
Your project provides the business logic through configurable hooks.

App name: `checkin`  
Default queue model name: `QueueEntry`

---

## Installation

Install the package:

```bash
pip install django-checkin
```

Add the app to your project:

```python
INSTALLED_APPS = [
    ...
    "checkin",
]
```

Run migrations (if the package ships models):

```bash
python manage.py migrate
```

---

## Include URLs

In your project `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path("checkin/", include("checkin.urls")),
]
```

---

## Configuration

The app reads its configuration from the `CHECKIN` setting.

In your project `settings.py`:

```python
CHECKIN = {
    "GET_USER_BY_IDENTIFIER": "project.hooks.get_user_by_identifier",
    "GENERATE_OTP": "project.hooks.generate_otp",
    "STORE_OTP": "project.hooks.store_otp",
    "SEND_OTP": "project.hooks.send_otp",
    "VERIFY_OTP": "project.hooks.verify_otp",
    "GENERATE_REGISTER_CODE": "project.hooks.generate_register_code",
    "REPRESENT_CHECKIN": "project.hooks.represent_checkin",
    "GET_TV_DASHBOARD": "project.hooks.get_tv_dashboard",
}
```

Internal package configuration (`checkin/conf.py`):

```python
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
```

---

## Required Hooks

Create a file in your project, for example:

```
project/hooks.py
```

Implement the required functions:

```python
import random
import uuid
from django.core.cache import cache


def get_user_by_identifier(identifier):
    """
    Return the user/client instance based on the provided identifier.
    Example: mobile number, national ID, or customer code.
    """
    from myapp.models import Client
    return Client.objects.filter(mobile=identifier).first()


def generate_otp():
    """Return a one-time password."""
    return str(random.randint(100000, 999999))


def store_otp(identifier, otp):
    """Store OTP temporarily (cache, DB, redis, etc.)."""
    cache.set(f"checkin:otp:{identifier}", otp, timeout=120)


def send_otp(identifier, otp):
    """Send OTP via SMS or other provider."""
    print(f"Send OTP {otp} to {identifier}")


def verify_otp(identifier, otp):
    """Validate the submitted OTP."""
    expected = cache.get(f"checkin:otp:{identifier}")
    return expected == otp


def generate_register_code():
    """Generate a unique check-in code."""
    return str(uuid.uuid4())[:8].upper()


def represent_checkin(queue_entry):
    """
    Convert a QueueEntry instance into a response dictionary.
    """
    return {
        "id": queue_entry.id,
        "code": queue_entry.code,
        "status": queue_entry.status,
        "created_at": queue_entry.created_at,
    }


def get_tv_dashboard():
    """
    Return dashboard data for TV/public display.
    """
    from checkin.models import QueueEntry

    return {
        "waiting": list(
            QueueEntry.objects.filter(status="waiting").values("code")
        ),
        "active": list(
            QueueEntry.objects.filter(status="active").values("code")
        ),
        "finished": list(
            QueueEntry.objects.filter(status="finished").values("code")
        ),
    }
```

---

## QueueEntry Model

Your project can use the provided `QueueEntry` model (if included), or integrate with it.

Example structure:

```python
class QueueEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="queue_entries",
    )
    code = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, default="waiting")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
```

---

## Typical Flow

1. Client submits an identifier  
2. `GET_USER_BY_IDENTIFIER` is called  
3. `GENERATE_OTP`, `STORE_OTP`, and `SEND_OTP` are called  
4. Client submits OTP  
5. `VERIFY_OTP` is called  
6. On success:
   - `GENERATE_REGISTER_CODE` is called
   - A `QueueEntry` is created
   - `REPRESENT_CHECKIN` formats the response  
7. Dashboard endpoints use `GET_TV_DASHBOARD`

---

## Example Requests

### Send Code

```
POST /checkin/send-code/
```

```json
{
  "identifier": "09120000000"
}
```

---

### Verify Code

```
POST /checkin/verify-code/
```

```json
{
  "identifier": "09120000000",
  "code": "123456"
}
```

---

### Example Success Response

```json
{
  "success": true,
  "queue_entry": {
    "id": 12,
    "code": "A1B2C3D4",
    "status": "waiting",
    "created_at": "2026-05-20T12:00:00Z"
  }
}
```

## Author

**Melika Tavakoli**  
Backend Developer specializing in real-time systems, clean architecture, and scalable backend solutions.

