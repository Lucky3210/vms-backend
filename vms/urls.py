from django.urls import path
from .views import LoginView, LogoutView, RegisterVisitorView, ListVisitorView


urlpatterns = [
    path('api/login', LoginView.as_view(), name='login'),
    path('api/logout', LogoutView.as_view(), name='logout'),
    path('api/registerVisitor', RegisterVisitorView.as_view(), name='registerVisitor'),
    path('api/visitorList', ListVisitorView.as_view(), name='visitor'),
]