from django.contrib import admin
from django.urls import path
from poppy import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('petsitters_nearby/<str:address>/<int:dist_or_fee>/', views.get_petsitters_nearby, name="petsitters_nearby"),
    path('petsitter_detail/<int:petsitter_pk>/', views.petsitter_detail, name="petsitter_detail"),
    path('apply/', views.ApplyView.as_view(), name="apply"),
    path('application/<str:target_petsitterID>', views.ApplicationView.as_view(), name="application"),
    path('authenticate/', views.is_authenticated, name="authentication"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('edit_profile/', views.EditProfileView.as_view(), name="edit_profile"),
]
