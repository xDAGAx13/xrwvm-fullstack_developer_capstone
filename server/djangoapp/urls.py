from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'

urlpatterns = [
    # path for registration (if needed later)

    # path for login
    path("login", views.login_user, name="login"),
    path('logout', views.logout_request, name='logout'),
    path('register/', views.registration, name='register'),


    # path for dealer reviews (to be added)

    # path for add a review (to be added)
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
