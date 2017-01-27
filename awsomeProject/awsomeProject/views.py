from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404
from .models import Product
from .models import Game
from .models import Scores
from .models import Gameplay
from .models import PlayerItem
from .files import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
import json
from django.http import JsonResponse
#@login_required
def index(request):
    if not Product.objects.filter(pk=1).exists():
        data = Product(title="Panda")
        data.save()
    return render(request, "index.html", {"title" : Product.objects.values('title').filter(pk=1)[0]['title']})

@login_required
def game(request, game_name):
    try:
        game = Game.objects.get(name=game_name)
        # TODO: What if highscores dont exist
        scores = Scores.objects.all().filter(game=game).order_by("-score")
    except Game.DoesNotExist:
        raise Http404
    return render(request, "game.html", {"game" : game, "scores" : scores})

@login_required
@csrf_protect
def saveScore(request):
    if request.method == "POST" and request.is_ajax():
        root = dict(request.POST.iterlists())
        user = User.objects.get(pk = root['user'][0])
        game = Game.objects.get(pk = root['game'][0])
        score = root['score'][0]
        if not Scores.objects.filter(user=user, game=game, score=score).exists():
            data = Scores(user=user, game=game, score=score)
            data.save()
        return HttpResponse(root)
    else:
        HttpResponse("Not authorized.")

@login_required
@csrf_protect
def saveGame(request):
    if request.method == "POST" and request.is_ajax():
        root = dict(request.POST.iterlists())

        user = User.objects.get(pk = root['user'][0])
        game = Game.objects.get(pk = root['game'][0])
        score = root['score'][0]
        items = root['items[]']
        if Gameplay.objects.filter(user=user, game=game).exists():
            Gameplay.objects.filter(user=user, game=game).update(score=score)
        else:
            data = Gameplay(user=user, game=game, score=score)
            data.save()

        gameplay = Gameplay.objects.get(user=user, game=game)
        for item in items:
            data = PlayerItem(gameplay=gameplay, itemName = item)
            data.save()
        return HttpResponse(root)
    else:
        HttpResponse("Not authorized.")

@login_required
@csrf_protect
def loadGame(request):
    if request.method == "POST" and request.is_ajax():
        root = dict(request.POST.iterlists())

        user = User.objects.get(pk = root['user'][0])
        game = Game.objects.get(pk = root['game'][0])

        if Gameplay.objects.filter(user=user, game=game).exists():
            gameplay = Gameplay.objects.get(user=user, game=game)
            response = {'messageType' : 'LOAD', 'gameState' : {'playerItems' : [], 'score' : gameplay.score}}
            # Same as PlayerItem.objects.all().filter(gameplay=gameplay)
            for item in PlayerItem.objects.filter(gameplay=gameplay):
                response['gameState']['playerItems'].append(item.itemName)
            return JsonResponse(response)
        else:
            HttpResponse("No saved games to load.")
    else:
        HttpResponse("Not authorized.")

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
@csrf_protect
def login(request):
    if request.method == 'POST':
        pass


















#FOR TESTING PURPOSES
def addGame(request, game_name):
    game = Game(name=game_name, url="http://webcourse.cs.hut.fi/example_game.html")
    game.save()
    return render(request, "index.html", {"title" : Product.objects.values('title').filter(pk=1)[0]['title']})
