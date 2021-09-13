from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registration/', views.register, name='registration'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('', views.home, name='home'),
    path('new_order', views.create_order, name='new_order'),
    path('all-order', views.AllOrder.as_view(template_name='all_order.html'), name='all-order'),
    path('profit', views.profit, name='profit')
]
