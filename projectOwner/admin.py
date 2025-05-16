from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from projectOwner.models import ProjectOwner
admin.site.register(ProjectOwner)

from projectOwner.models import Project
admin.site.register(Project)