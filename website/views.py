from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template import loader
from .models import Product, Order
from django.contrib.auth.decorators import login_required
from .forms import SearchForm
#from django.contrib import messages

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

    
        

def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'website/register.html', {'form': form})


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
    