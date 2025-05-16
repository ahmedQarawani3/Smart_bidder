from django.contrib import admin

# Register your models here.
from .models import Investor
admin.site.register(Investor)

from .models import InvestmentOffer
admin.site.register(InvestmentOffer)

from .models import Negotiation
admin.site.register(Negotiation)