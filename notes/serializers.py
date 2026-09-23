from rest_framework import serializers

from .models import ApiKey, Note


class ApiKeyCreateSerializer(serializers.ModelSerializer):
    """Used only for the creation request body."""

    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'is_active', 'created_at', 'last_used_at']
        read_only_fields = ['id', 'is_active', 'created_at', 'last_used_at']


class ApiKeyOut(serializers.ModelSerializer):
    """Safe representation of an ApiKey. Never exposes key_hash or the raw key."""

    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'is_active', 'created_at', 'last_used_at']
        read_only_fields = fields


class ApiKeyUpdateSerializer(serializers.ModelSerializer):
    """Used for PUT edits: name and/or is_active."""

    class Meta:
        model = ApiKey
        fields = ['id', 'name', 'is_active', 'created_at', 'last_used_at']
        read_only_fields = ['id', 'created_at', 'last_used_at']


class NoteSerializer(serializers.ModelSerializer):
    shared_with = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'status', 'owner', 'shared_with', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'owner', 'shared_with', 'created_at', 'updated_at']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('title must not be empty.')
        return value

    def validate_content(self, value):
        if value is None or not str(value).strip():
            raise serializers.ValidationError('content must be provided.')
        return value
