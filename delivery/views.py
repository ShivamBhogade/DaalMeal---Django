from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Restaurant

def index(request):
    return render(request, 'index.html')


# ================= SIGN UP =================
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')

        if not username or not password or not email:
            return HttpResponse("All fields are required")

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists")

        user = User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            phone_number=phone_number,
            address=address
        )

        request.session["customer_id"] = user.id
        return redirect("customer_home")

    return render(request, "signup.html")


# ================= SIGN IN =================
def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Admin login (Django auth)
        auth_user = authenticate(request, username=username, password=password)
        if auth_user:
            login(request, auth_user)
            return redirect("admin_home")

        # Customer login (custom model)
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                request.session["customer_id"] = user.id
                return redirect("customer_home")
        except User.DoesNotExist:
            pass

        return HttpResponse("Invalid username or password")

    return render(request, "signin.html")


# ================= CUSTOMER =================
def customer_home(request):
    if not request.session.get("customer_id"):
        return redirect("signin")

    restaurants = Restaurant.objects.all()
    return render(request, "customer.html", {"restaurantList": restaurants})


# ================= ADMIN =================
def admin_home(request):
    return render(request, "admin_home.html")


# ================= RESTAURANT =================
def open_add_restaurant(request):
    return render(request, "add_restaurant.html")

def add_restaurant(request):
    if request.method == "POST":
        restaurant_name = request.POST.get("restaurant_name")

        if Restaurant.objects.filter(name=restaurant_name).exists():
            return HttpResponse("Duplicate restaurant name not allowed")

        Restaurant.objects.create(
            name=restaurant_name,
            cuisine_type=request.POST.get("cuisine_type"),
            address=request.POST.get("address"),
            phone_number=request.POST.get("phone_number"),
            picture_url=request.POST.get("picture_url"),
            rating=request.POST.get("rating"),
        )

        return redirect("view_restaurant")

    return render(request, "add_restaurant.html")

def view_restaurant(request):
    restaurants = Restaurant.objects.all()
    return render(request, "view_restaurant.html", {"restaurants": restaurants})

def update_restaurant(request, id):
    restaurant = Restaurant.objects.get(id=id)

    if request.method == "POST":
        restaurant.name = request.POST.get("restaurant_name")
        restaurant.address = request.POST.get("address")
        restaurant.phone_number = request.POST.get("phone_number")
        restaurant.cuisine_type = request.POST.get("cuisine_type")
        restaurant.picture_url = request.POST.get("picture_url")
        restaurant.rating = request.POST.get("rating")

        restaurant.save()
        return redirect("view_restaurant")

    return render(request, "update_restaurant.html", {"restaurant": restaurant})

def delete_restaurant(request, id):
    restaurant = Restaurant.objects.get(id=id)

    if request.method == "POST":
        restaurant.delete()
        return redirect("view_restaurant")

    return render(request, "delete_restaurant.html", {"restaurant": restaurant})

from .models import MenuItem

def view_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    menu_items = MenuItem.objects.filter(restaurant=restaurant)
    return render(request, "view_menu.html", {
        "restaurant": restaurant,
        "menu_items": menu_items
    })


def add_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == "POST":
        MenuItem.objects.create(
            restaurant=restaurant,
            name=request.POST.get("name"),
            price=request.POST.get("price"),
            description=request.POST.get("description")
        )
        return redirect("view_menu", restaurant_id=restaurant.id)

    return render(request, "add_menu.html", {"restaurant": restaurant})

def customer_restaurants(request):
    restaurants = Restaurant.objects.all()
    return render(request, "customer_restaurants.html", {
        "restaurants": restaurants
    })

def customer_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)
    menu_items = restaurant.menu_items.all()

    return render(request, "customer_menu.html", {
        "restaurant": restaurant,
        "menu_items": menu_items
    })


def add_to_cart(request, menu_id):
    # 🔒 Login required
    if not request.session.get("customer_id"):
        return redirect("signin")

    cart = request.session.get("cart", {})

    if str(menu_id) in cart:
        cart[str(menu_id)]["qty"] += 1
    else:
        item = MenuItem.objects.get(id=menu_id)
        cart[str(menu_id)] = {
            "name": item.name,
            "price": item.price,
            "qty": 1
        }

    request.session["cart"] = cart
    return redirect("view_cart")


def view_cart(request):
    if not request.session.get("customer_id"):
        return redirect("signin")

    cart = request.session.get("cart", {})
    total = sum(item["price"] * item["qty"] for item in cart.values())

    return render(request, "cart.html", {
        "cart": cart,
        "total": total
    })


from .models import Order, OrderItem

def place_order(request):
    if not request.session.get("customer_id"):
        return redirect("signin")

    cart = request.session.get("cart", {})
    if not cart:
        return HttpResponse("Cart is empty")

    total = sum(item["price"] * item["qty"] for item in cart.values())

    # ✅ Create order
    order = Order.objects.create(
        customer_id=request.session["customer_id"],
        total_amount=total
    )

    # ✅ Save order items
    for item_id, item in cart.items():
        OrderItem.objects.create(
            order=order,
            menu_item_id=item_id,
            quantity=item["qty"],
            price=item["price"]
        )

    # ✅ Clear cart
    request.session["cart"] = {}

    return render(request, "order_success.html", {
        "order": order
    })

def customer_orders(request):
    if not request.session.get("customer_id"):
        return redirect("signin")

    orders = Order.objects.filter(
        customer_id=request.session["customer_id"]
    ).order_by("-created_at")

    return render(request, "customer_orders.html", {"orders": orders})

def order_detail(request, order_id):
    if not request.session.get("customer_id"):
        return redirect("signin")

    order = Order.objects.get(
        id=order_id,
        customer_id=request.session["customer_id"]
    )

    items = OrderItem.objects.filter(order=order)

    return render(request, "order_detail.html", {
        "order": order,
        "items": items
    })

def admin_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin_orders.html", {"orders": orders})

def admin_order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)

    if request.method == "POST":
        order.status = request.POST.get("status")
        order.save()

        # 🔥 redirect back to same page
        return redirect("admin_order_detail", order_id=order.id)

    return render(request, "admin_order_detail.html", {
        "order": order,
        "items": items
    })


def customer_order_detail(request, order_id):
    if not request.session.get("customer_id"):
        return redirect("signin")

    order = Order.objects.get(
        id=order_id,
        customer_id=request.session["customer_id"]
    )

    items = OrderItem.objects.filter(order=order)

    return render(request, "customer_order_detail.html", {
        "order": order,
        "items": items
    })

from django.contrib.auth import logout as django_logout

def logout_view(request):
    request.session.flush()  # 🔥 clears cart + customer_id
    return redirect("/")


