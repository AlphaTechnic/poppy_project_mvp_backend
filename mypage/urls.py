from django.contrib import admin
from django.urls import path
from poppy import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('petsitters_nearby/<str:address>/<int:dist_or_fee>/', views.get_petsitters_nearby, name="petsitters_nearby"),
    path('petsitter_detail/<str:petsitterID>/', views.petsitter_detail, name="petsitter_detail"),
    path('apply/', views.apply, name="apply"),
    path('care_detail/<str:senderID>/<str:target_petsitterID>', views.care_detail, name="care_detail")
]
