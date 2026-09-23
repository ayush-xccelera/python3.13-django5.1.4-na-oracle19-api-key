from django.contrib import admin

from .models import ApiKey, Note

admin.site.register(ApiKey)
admin.site.register(Note)
