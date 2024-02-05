from django.contrib import admin
from django.urls import path

from account.views import (
    cart_summary_view,
    cart_add_view,
    cart_delete_view,
    cart_update_view
)



urlpatterns = [
    path('', cart_summary_view, name="cart_summary"),
    path('add/', cart_add_view, name="cart_add"),
    path('delete/', cart_delete_view, name="cart_delete"),
    path('update/', cart_update_view, name="cart_update"),
]