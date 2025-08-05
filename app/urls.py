from django.urls import path, include
from app.core import views 

urlpatterns = [
    path('api/', include('app.core.urls')),
    path('api/', views.api_view),
]
