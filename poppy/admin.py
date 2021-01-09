from django.contrib import admin
from .models import PetOwner, Post, Fee, Pet, Comment, Application

admin.site.register(Fee)
admin.site.register(PetOwner)
admin.site.register(Post)
admin.site.register(Pet)
admin.site.register(Comment)
admin.site.register(Application)

