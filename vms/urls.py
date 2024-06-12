from django.urls import path
from .views import *


urlpatterns = [
    path('api/login', LoginView.as_view(), name='login'),
    path('api/logout', LogoutView.as_view(), name='logout'),
    path('api/registerVisitor', RegisterVisitorView.as_view(),
         name='registerVisitor'),
    path('api/visitorList', ListVisitorView.as_view(), name='visitor'),
    path('api/visitRequest/<int:pk>/accept',
         AcceptVisitRequest.as_view(), name='acceptVisitorReq'),
    path('api/visitRequest/<int:pk>/decline',
         DeclineVisitRequest.as_view(), name='declineVisitorReq'),
    path('api/checkout/<int:pk>',
         CheckoutVisitorView.as_view(), name='visitorCheckout'),
    path('api/checkin/<int:pk>', CheckInVisitorView.as_view(), name='visitorCheckin'),
    path('api/staffVisitRegister', StaffVisitRegisterView.as_view(),
         name='staffVisitRegister'),
    path('api/staffVisit', StaffScheduleListView.as_view(), name='StaffVisitList')
]
