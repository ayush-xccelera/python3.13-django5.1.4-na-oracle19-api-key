import hashlib
import secrets

from django.db import models


class ApiKey(models.Model):
    """A client identified by an API key. Each ApiKey row represents one client."""

    key_hash = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({"active" if self.is_active else "revoked"})'

    @staticmethod
    def hash_key(raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    @classmethod
    def generate(cls, name: str):
        """Create a new ApiKey row, returning (instance, raw_key)."""
        raw_key = secrets.token_urlsafe(32)
        instance = cls.objects.create(name=name, key_hash=cls.hash_key(raw_key))
        return instance, raw_key


class Note(models.Model):
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_ARCHIVED = 'ARCHIVED'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    owner = models.ForeignKey(ApiKey, on_delete=models.CASCADE, related_name='notes')
    shared_with = models.ManyToManyField(
        ApiKey, related_name='shared_notes', blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} [{self.status}]'
