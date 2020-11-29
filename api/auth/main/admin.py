from django.contrib import admin
from .models import Province, City, User, BlackList

admin.site.register(Province)
admin.site.register(City)
admin.site.register(User)
admin.site.register(BlackList)

