from rest_framework.routers import DefaultRouter

from .views import ApiKeyViewSet, NoteViewSet

router = DefaultRouter()
router.register(r'api-keys', ApiKeyViewSet, basename='apikey')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = router.urls
