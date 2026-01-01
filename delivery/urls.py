from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    # Auth
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),

    # Dashboards
    path('customer/', views.customer_home, name='customer_home'),
    path('admin_home/', views.admin_home, name='admin_home'),

    # Restaurant
    path('add_restaurant/', views.add_restaurant, name='add_restaurant'),
    path('view_restaurant/', views.view_restaurant, name='view_restaurant'),

    # Update Restaurant
    path('update_restaurant/<int:id>/', views.update_restaurant, name='update_restaurant'),
    # Delete Restaurant
    path('delete_restaurant/<int:id>/', views.delete_restaurant, name='delete_restaurant'),

    path('menu/<int:restaurant_id>/', views.view_menu, name='view_menu'),
    path('add_menu/<int:restaurant_id>/', views.add_menu, name='add_menu'),

    path('customer/restaurants/', views.customer_restaurants, name='customer_restaurants'),
    
    path('customer/menu/<int:restaurant_id>/', views.customer_menu, name='customer_menu'),

    #cart
    path("cart/add/<int:menu_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),

    path("order/place/", views.place_order, name="place_order"),

    path("customer/orders/", views.customer_orders, name="customer_orders"),
    path("customer/orders/<int:order_id>/",views.order_detail,name="order_detail"),
    
    path("admin/orders/", views.admin_orders, name="admin_orders"), 

    # Admin dashboard (custom)
    path("dashboard/orders/", views.admin_orders, name="admin_orders"),
    path("dashboard/orders/<int:order_id>/",views.admin_order_detail,name="admin_order_detail"),

    path("customer/orders/<int:order_id>/",views.customer_order_detail,name="customer_order_detail"),

    path("logout/", views.logout_view, name="logout"),


]
