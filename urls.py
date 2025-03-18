
from django.urls import path
from . import views

urlpatterns = [
    # Navigation and index pages
    path('nav/', views.nav, name='nav'),
    path('home/', views.index, name='index'),

    # Registration and authentication
    path('register/', views.customer_reg, name='customer_reg'),
    path('', views.login_page, name='login_page'),
    path('logout/', views.logout, name='logout'),

    # Product views
    path('pro/<id>',views.pro,name='pro'),
    path('products/men/', views.products_men, name='products_men'),
    path('products/women/', views.products_women, name='products_women'),
    path('products/kids/', views.products_kids, name='products_kids'),
    path('products/accessories/', views.products_access, name='products_access'),
    path('product/<int:id>', views.single_product, name='single_product'),
     path('api/get_product_details/',views.get_product_details, name='get_product_details'),

    # Cart views
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/delete/<int:id>', views.cart_delete, name='cart_delete'),
    path('cart/buy_all/', views.buy_all, name='buy_all'),
    path('cart/buy_single/<int:cart_item_id>/', views.buy_single, name='buy_single'),


    # Order views
   #
    # path('orders/create/', views.create_order, name='create_order'),
    path('orders/status/<int:id>/', views.order_status, name='order_status'),
    path('confirm/order/', views.confirm_order, name='confirm_order'),
    path('invoice/<int:order_id>/', views.invoice_view, name='invoice_view'),
    path('order_details/<int:id>/',views.order_details,name='order_details'),
    path('order_history',views.order_history,name='order_history'),
    #payment
    path('payment_page/<order_id>',views.payment_page,name='payment_page'),
    # Admin views
    path('admin1/', views.admin1, name='admin1'),
    path('admin1/products/', views.view_products, name='view_products'),
    path('admin1/products/update/<int:id>/', views.update_product, name='update_product'),
    path('admin1/products/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('admin1/customers/', views.view_customers, name='view_customers'),
    path('admin1/customer/<int:id>/', views.view_customer, name='view_customer'),

    # Complaint and reply views
    path('contact/', views.contact, name='contact'),
    path('complaints/', views.view_complaints, name='view_complaints'),
    path('complaints/reply/<int:id>/', views.reply, name='reply'),
    path('complaints/replies/', views.view_reply, name='view_reply'),
    path('complaints/reply_id/<int:id>/', views.reply_id, name='reply_id'),

    # User profile
    path('profile/update/', views.update_profile, name='update_profile'),

    # Static pages
    path('about/', views.about, name='about'),
]
