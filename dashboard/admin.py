from django.contrib import admin

from .models import Sample, Algo, Hash

admin.site.register(Algo)
admin.site.register(Hash)
admin.site.register(Sample)
