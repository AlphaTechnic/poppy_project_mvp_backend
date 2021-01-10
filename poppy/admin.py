from django.contrib import admin
from .models import PetOwner, Post, Fee, Pet, Comment, Application
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin


class PostAdmin(admin.ModelAdmin, DynamicArrayMixin):
    pass

admin.site.register(Fee)
admin.site.register(PetOwner)
admin.site.register(Post, PostAdmin)
admin.site.register(Pet)
admin.site.register(Comment)
admin.site.register(Application)

