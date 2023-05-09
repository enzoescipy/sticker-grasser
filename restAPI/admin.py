from django.contrib import admin

from . import models

admin.site.register(models.User)
admin.site.register(models.Project)
admin.site.register(models.Stamp)
admin.site.register(models.Main)