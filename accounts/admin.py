from django.contrib import admin

# Register your models here.
from accounts.models import Review
admin.site.register(Review)

from accounts.models import Notification
admin.site.register(Notification)

from accounts.models import Complaint
admin.site.register(Complaint)

from accounts.models import User
admin.site.register(User)