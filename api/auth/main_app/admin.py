from django.contrib import admin
from .models import User, SalesMan, City, Province, JobCategory

admin.site.register(User)
admin.site.register(SalesMan)
admin.site.register(Province)
admin.site.register(City)
admin.site.register(JobCategory)


