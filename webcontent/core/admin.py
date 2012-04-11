from django.contrib import admin
from webcontent.core import models

class GadgetAdmin(admin.ModelAdmin):
    model = models.Gadgets

class LibraryAdmin(admin.ModelAdmin):
    model = models.Library

admin.site.register(models.Gadgets, GadgetAdmin)
admin.site.register(models.Library, LibraryAdmin)