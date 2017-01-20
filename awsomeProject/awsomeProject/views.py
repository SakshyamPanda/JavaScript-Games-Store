from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404
from .models import Product
from .models import Game
from .files import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

@login_required
def index(request):
    if not Product.objects.filter(pk=1).exists():
        data = Product(title="Panda")
        data.save()
    return render(request, "index.html", {"title" : Product.objects.values('title').filter(pk=1)[0]['title']})

def game(request, game_name):
    try:
        game = Game.objects.get(name=game_name)
    except Game.DoesNotExist:
        raise Http404
    return render(request, "game.html", {"game" : game})

@csrf_protect
def register(request):
    if request.method == 'POST':

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
    'form': form
    })

    return render(request,
    'registration/register.html', {'form' : form}
    )
def register_success(request):
    return render(request,
    'registration/success.html', {}
    )
#FOR TESTING PURPOSES
def addGame(request, game_name):
    game = Game(name=game_name, url="http://webcourse.cs.hut.fi/example_game.html")
    game.save()
    return render(request, "index.html", {"title" : Product.objects.values('title').filter(pk=1)[0]['title']})
