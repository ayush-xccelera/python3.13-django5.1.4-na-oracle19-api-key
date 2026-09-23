from django.urls import re_path
from rest_framework.routers import DefaultRouter

from .views import ApiKeyViewSet, NoteViewSet

router = DefaultRouter()
router.register(r'api-keys', ApiKeyViewSet, basename='apikey')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    # Explicit route (no trailing slash) matching the spec literally:
    # DELETE /api/v1/notes/{id}/share/{client_id}
    re_path(
        r'^notes/(?P<pk>[^/.]+)/share/(?P<client_id>[^/.]+)$',
        NoteViewSet.as_view({'delete': 'unshare'}),
        name='note-unshare-no-slash',
    ),
] + router.urls
