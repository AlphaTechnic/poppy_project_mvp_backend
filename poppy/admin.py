from django.contrib import admin
from .models import PetOwner, Post, Fee, Pet, Comment, Application, test
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin


class DynamicAdmin(admin.ModelAdmin, DynamicArrayMixin):
    pass


admin.site.register(Fee, DynamicAdmin)
admin.site.register(PetOwner)
admin.site.register(Post, DynamicAdmin)
admin.site.register(Pet)
admin.site.register(Comment)
admin.site.register(Application)

admin.site.register(test)

