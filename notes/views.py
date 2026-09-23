from django.db import transaction
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import ApiKey, Note
from .pagination import DefaultLimitOffsetPagination
from .permissions import IsAdminApiKey
from .serializers import (
    ApiKeyCreateSerializer,
    ApiKeyOut,
    ApiKeyUpdateSerializer,
    NoteSerializer,
)


class ApiKeyViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Administrative API key management. Gated by ADMIN_API_KEY, never by X-API-Key."""

    queryset = ApiKey.objects.all()
    authentication_classes = []
    permission_classes = [IsAdminApiKey]
    pagination_class = DefaultLimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return ApiKeyCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ApiKeyUpdateSerializer
        return ApiKeyOut

    def create(self, request, *args, **kwargs):
        name = (request.data.get('name') or '').strip()
        if not name:
            raise ValidationError({'name': 'This field is required.'})
        instance, raw_key = ApiKey.generate(name=name)
        data = ApiKeyOut(instance).data
        data['key'] = raw_key
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response(ApiKeyOut(instance).data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'bootstrap':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='bootstrap')
    def bootstrap(self, request, *args, **kwargs):
        """One-time, unauthenticated endpoint to create the very first API key.

        Permanently disabled (always 403) once any ApiKey row exists.
        """
        if ApiKey.objects.exists():
            raise PermissionDenied('Bootstrap is disabled: an API key already exists.')

        name = (request.data.get('name') or '').strip() or 'bootstrap-client'
        instance, raw_key = ApiKey.generate(name=name)
        data = ApiKeyOut(instance).data
        data['raw_key'] = raw_key
        return Response(data, status=status.HTTP_201_CREATED)


class NoteViewSet(viewsets.ModelViewSet):
    """CRUD + archive/restore for notes, scoped to the authenticated client (API key)."""

    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    ORDERING_FIELDS = {'created_at', 'updated_at', 'title'}

    def get_queryset(self):
        owner = self.request.auth
        qs = Note.objects.filter(owner=owner)

        if self.action == 'list':
            qs = qs.filter(status=Note.STATUS_ACTIVE)

        ordering = self.request.query_params.get('ordering')
        if ordering:
            field = ordering.lstrip('-')
            if field in self.ORDERING_FIELDS:
                qs = qs.order_by(ordering)

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.auth, status=Note.STATUS_ACTIVE)

    def get_object(self):
        owner = self.request.auth
        obj = Note.objects.filter(pk=self.kwargs['pk'], owner=owner).first()
        if obj is None:
            raise NotFound('Note not found.')
        return obj

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            serializer.save(owner=instance.owner)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='archive')
    def archive(self, request, pk=None):
        instance = self.get_object()
        if instance.status != Note.STATUS_ACTIVE:
            raise ValidationError('Only ACTIVE notes can be archived.')
        instance.status = Note.STATUS_ARCHIVED
        instance.save(update_fields=['status', 'updated_at'])
        return Response(NoteSerializer(instance).data)

    @action(detail=True, methods=['patch'], url_path='restore')
    def restore(self, request, pk=None):
        instance = self.get_object()
        if instance.status != Note.STATUS_ARCHIVED:
            raise ValidationError('Only ARCHIVED notes can be restored.')
        instance.status = Note.STATUS_ACTIVE
        instance.save(update_fields=['status', 'updated_at'])
        return Response(NoteSerializer(instance).data)
