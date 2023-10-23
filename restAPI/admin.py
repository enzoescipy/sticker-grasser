from django.contrib import admin

from . import models


# User model
admin.site.register(model_or_iterable=models.User)

# Project models
admin.site.register(model_or_iterable=models.Project)
admin.site.register(model_or_iterable=models.Todo)

# Stamp models
admin.site.register(model_or_iterable=models.Stamp)
admin.site.register(model_or_iterable=models.DefFunc)
admin.site.register(model_or_iterable=models.FuncArg)

# History models
admin.site.register(model_or_iterable=models.UserTodoStampOwnedHistory)
admin.site.register(model_or_iterable=models.History)
admin.site.register(model_or_iterable=models.HistoryArg)