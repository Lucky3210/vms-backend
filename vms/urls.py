from django.urls import path
from .views import LoginView, LogoutView, RegisterVisitorView, ListVisitorView, AcceptVisitRequest, DeclineVisitRequest, CheckoutVisitorView, CheckInVisitorView


urlpatterns = [
    path('api/login', LoginView.as_view(), name='login'),
    path('api/logout', LogoutView.as_view(), name='logout'),
    path('api/registerVisitor', RegisterVisitorView.as_view(), name='registerVisitor'),
    path('api/visitorList', ListVisitorView.as_view(), name='visitor'),
    path('api/visitRequest/<int:visitRequestId>/accept', AcceptVisitRequest.as_view(), name='acceptVisitorReq'),
    path('api/visitRequest/<int:visitRequestId>/decline', DeclineVisitRequest.as_view(), name='declineVisitorReq'),
    path('api/checkout/<int:pk>', CheckoutVisitorView.as_view(), name='visitorCheckout'),
    path('api/checkin/<int:pk>', CheckInVisitorView.as_view(), name='visitorCheckin'),
]