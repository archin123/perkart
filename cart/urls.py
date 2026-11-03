from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail_view, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('update/<int:product_id>/', views.cart_update_view, name='cart_update'),
    path('remove/<int:product_id>/', views.cart_remove_view, name='cart_remove'),
    path('coupon/apply/', views.cart_apply_coupon_view, name='cart_apply_coupon'),
    path('coupon/remove/', views.cart_remove_coupon_view, name='cart_remove_coupon'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_list_view, name='order_list'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
]
