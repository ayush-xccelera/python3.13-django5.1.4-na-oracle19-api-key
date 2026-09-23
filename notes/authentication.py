from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import ApiKey


class ApiKeyUser:
    """A minimal authenticated-user stand-in so DRF's IsAuthenticated passes."""

    is_authenticated = True
    is_anonymous = False

    def __str__(self):
        return 'ApiKeyUser'


class ApiKeyAuthentication(BaseAuthentication):
    """Authenticates requests using the 'X-API-Key' header against the ApiKey table."""

    def authenticate(self, request):
        raw_key = request.META.get('HTTP_X_API_KEY')
        if not raw_key:
            return None

        key_hash = ApiKey.hash_key(raw_key)
        try:
            api_key = ApiKey.objects.get(key_hash=key_hash)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key.')

        if not api_key.is_active:
            raise AuthenticationFailed('API key is not active.')

        ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())

        return (ApiKeyUser(), api_key)

    def authenticate_header(self, request):
        return 'X-API-Key'
