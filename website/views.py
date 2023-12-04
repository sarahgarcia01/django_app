from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from .models import Product, Order, User
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from decimal import Decimal
from django.contrib.auth import get_user
from django.shortcuts import get_object_or_404
from .forms import SearchForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import loader
from .forms import SearchForm
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models import Q



def index(request):
    products = Product.objects.all()
    return render(request, 'website/index.html', {'products': products})


def searchresults(request):
    search = request.GET.get('search') or request.POST.get('search')
    sort_option = request.GET.get('sort', 'name')

    results = Product.objects.filter(name__contains=search) if search else Product.objects.all()
    
    if sort_option == 'name':
        results = results.order_by('name')
    elif sort_option == '-name':
        results = results.order_by('-name')
    elif sort_option == 'price':
        results = results.order_by('price')
    elif sort_option == '-price':
        results = results.order_by('-price')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template = loader.get_template('website/sortedresults.html')
        return HttpResponse(template.render({'results': results}))

    # if request.is_ajax():
    #     html = render_to_string('website/sortedresults.html', {'results': results})
    #     return HttpResponse(html)

    return render(request, 'website/searchresult.html', {'search': search, 'results': results})

    
    
    #############################################
    
    # if request.method == "POST":
        
    #     search = request.POST['search']
        
    #     if search == "\0":
    #         results = Product.objects.all()
    #         return render(request, 'website/index.html',{'search':search, 'results':results})
        
    #     else:
    #         results = Product.objects.filter(name__contains=search)
    #         sort_option = request.GET.get('sort', 'name')
    #         # sort_option = request.GET.get('sort', 'relevance')
    #         if sort_option == 'name':
    #             results = results.order_by('name')
    #         elif sort_option == 'price':
    #             results = results.order_by('price')

    #         return render(request, 'website/searchresult.html',{'search':search, 'results':results})

    
def shopping_cart(request):
    """
    This function displays the shopping cart page.
    Args:
        request: the HTTP request object.
    Returns:
        the rendered shopping cart page.
    """

    # check if user is logged in
    if not request.user.is_authenticated:
        return redirect('register')
    
    # get the user's cart from session
    shopping_cart = request.session.get('shopping_cart', {})

    # create empty list for storing cart items
    cart_items = []

    # calculate the total cost of the order
    total_cost = 0

    for product_id, quantity in shopping_cart.items():
        # get product from database
        product = Product.objects.get(id=product_id)
        # calculate total cost for product
        subtotal = product.price * quantity
        # add subtotal to total cost
        total_cost += subtotal

        # add product to list
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal})

    # calculate tax
    tax = calculate_tax(total_cost)
    total_after_tax = total_cost + tax
    total_after_tax = round(total_after_tax, 2)

    context = {
    'cart_items': cart_items,
    'total_cost': total_cost,
    'tax': tax,
    'total_after_tax': total_after_tax,
    }

    # render the shopping cart page
    return render(request, 'website/shopping_cart.html', context)

    
def update_cart(request, product_id):
    """
    This function updates the quantity of a product in the shopping cart.
    Args:
        request: the HTTP request object.
        product_id: the id of the product to update.
    Returns:
        a redirect to the shopping cart.
    """

    # check if user is logged in
    if not request.user.is_authenticated:
        return redirect('login')
    # get the product from the database
    product = Product.objects.get(id=product_id)
    # get the quantity from the form
    quantity = int(request.POST['quantity'])
    # get shopping cart from session
    shopping_cart = request.session.get('shopping_cart', {})
    # update the quantity
    shopping_cart[product_id] = quantity
    # save the shopping cart back to session
    request.session['shopping_cart'] = shopping_cart
    
    return redirect('shopping_cart')



def add_to_cart(request, product_id):
    
    if not request.user.is_authenticated:
        return redirect('login')
    
    product = Product.objects.get(id=product_id)

    shopping_cart = request.session.get('shopping_cart', {})

    if product not in shopping_cart:
        shopping_cart[product_id] = 1
    else:
        shopping_cart[product_id] += 1

    request.session['shopping_cart'] = shopping_cart

    return redirect('shopping_cart')


def checkout(request):
    """
    This function displays the checkout page.
    Args:
        request: the HTTP request object.
    Returns:
        the rendered checkout page.
    """

    return render(request, 'website/checkout.html')

def calculate_tax(total):
    tax = 0
    tax_rate = Decimal('0.0625')
    tax = total * tax_rate
    tax = round (tax, 2)
    return tax


def display_cart(shopping_cart):
    cart_items = []
    for product_id, quantity in shopping_cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity

        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    return cart_items

def place_order(request):

    if not request.user.is_authenticated:
        return redirect('login')
    
    shipping_address = request.POST['shipping_address']
    payment_method = request.POST['payment_method']

    shopping_cart = request.session.get('shopping_cart', {})

    total_price = sum(Product.objects.get(id=product_id).price * quantity for product_id, quantity in shopping_cart.items())
    total_quantity = sum(quantity for quantity in shopping_cart.values())

    for product_id, quantity in shopping_cart.items():
        product = get_object_or_404(Product, id=product_id)
        order = Order.objects.create(
            user = request.user,
            product = product,
            quantity = quantity,
            total_price = total_price,
            date = datetime.now(),
            shipping_address = shipping_address,
            payment_method = payment_method
        )

    cart_items = display_cart(shopping_cart)

    request.session['shopping_cart'] = {}

    context = {
        'total': calculate_tax(total_price) + total_price,
        'total_quantity': total_quantity,
        'shipping_address': shipping_address,
        'order_date': order.date,
        'payment_method': payment_method,
        'cart_items': cart_items
    }
    return render(request, 'website/order_complete.html', context)

def order_complete(request):
    return render(request, 'website/order_complete.html')




def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'website/register.html', {'form': form})

def productview(request, product_id):
    # Retrieve the product parameters from the request's GET parameters
    image_url = request.GET.get('image_url', '')
    name = request.GET.get('name', '')
    price = request.GET.get('price', '')
    description = request.GET.get('description', '')
    availability = request.GET.get('availability', '')

    return render(request, 'website/productview.html', {'product_id': product_id, 'image_url': image_url, 'name': name, 'price': price, 'description': description, 'availability': availability})


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        auth_login(request, user)
        return redirect('homepage')
    else:
        error = 'Invalid username or password'
        return render(request, 'website/login.html', {'error': error})
    
def logout(request):
    auth_logout(request)
   # messages.success(request, ("You Have Successfully Logged Out"))
    return redirect('homepage')

def search_view(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        results = Product.objects.filter(name__icontains=query)
    else:
        results = []
    return render(request, 'search_results.html', {'form': form, 'results': results})

def categoryresults(request, category):
    if category == 'Pant':
        pants = Product.objects.filter(name__contains='Pants').values()
        jeans = Product.objects.filter(name__contains='Jeans').values()
        results = pants | jeans
    elif category == 'Shoe':
        shoes = Product.objects.filter(name__contains=category).values()
        boots = Product.objects.filter(name__contains='Boots').values()
        results = shoes | boots
    else:
        results = Product.objects.filter(name__contains=category).values()
    return render(request, 'website/categoryresults.html', {'results': results, 'category': category})
    