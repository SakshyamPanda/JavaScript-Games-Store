from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404
from .models import Game
from .models import Scores
from .models import Gameplay
from .models import PlayerItem
from .models import UserProfile
from .models import Transaction
from .models import Comment
from .files import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
import json
from django.http import JsonResponse
import cloudinary, cloudinary.uploader, cloudinary.api
#from cloudinary.uploader import upload
#from cloudinary.utils import cloudinary_url
#from cloudinary.api import delete_resources_by_tag, resources_by_tag
from django import forms
from cloudinary.forms import cl_init_js_callbacks
#from .models import GameImage, ProfileImage
from .files import GameImageForm, ProfileImageForm

cloudinary.config( 
  cloud_name = "sakshyam", 
  api_key = "623965587187774", 
  api_secret = "Lf7ULK0njrZJlVdwopnjsMeLdfM" 
)


#@login_required
def index(request):
    return render(request, "index.html", {})

@login_required(login_url='/login/')
def myProfile(request):
    userProfile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST' and userProfile.isDeveloper:
        form = UploadGameForm(request.POST, request.FILES)
        success = False
        if form.is_valid():
            game = Game(name=form.cleaned_data['name'], url=form.cleaned_data['url'], price=form.cleaned_data['price'], description=form.cleaned_data['description'], image=form.cleaned_data['image'])
            game.save()
            form = UploadGameForm()
            success = True
    else:
        form = UploadGameForm()
        success = False

    return render(request, "myProfile.html", {"userProfile" : userProfile, "form" : form, "success" : success   })

def browseGames(request):
    games = Game.objects.all()
    return render(request, "browseGames.html", {"games" : games })

#TODO: implement
@login_required(login_url='/login/')
def buyGame(request, game_name):

    return render(request, "buyGame.html", {})

#Main view where user plays game
@login_required(login_url='/login/')
def game(request, game_name):
    try:
        game = Game.objects.get(name=game_name)
        # TODO: What if highscores dont exist
        scores = Scores.objects.all().filter(game=game).order_by("-score")
        #check if user has bought the game a.k.a. has access to it
        if Transaction.objects.filter(game=game, user=request.user).exists():
            gameBought = True
        else:
            gameBought = False
        comments = Comment.objects.all().filter(game=game).order_by("-created")
    # In case game does not exist, display 404
    except Game.DoesNotExist:
        raise Http404
    return render(request, "game.html", {"game" : game, "scores" : scores, "gameBought" : gameBought, "comments": comments})

@login_required(login_url='/login/')
@csrf_protect
def saveScore(request):
    # Only available as ajax post call
    if request.method == "POST" and request.is_ajax():
        #create python dictionary from data sent through post request
        root = dict(request.POST.iterlists())
        user = request.user
        #extract data from root
        game = Game.objects.get(pk = root['game'][0])
        score = root['score'][0]
        # Do not save dupicates of Scores (same score from same user for same game)
        if not Scores.objects.filter(user=user, game=game, score=score).exists():
            data = Scores(user=user, game=game, score=score)
            data.save()
        return HttpResponse("Score Saved")
    else:
        return HttpResponse("Not authorized.")

@login_required(login_url='/login/')
@csrf_protect
def saveGame(request):
    if request.method == "POST" and request.is_ajax():
        #create python dictionary from data sent through post request
        root = dict(request.POST.iterlists())

        user = request.user
        #extract data from root
        game = Game.objects.get(pk = root['game'][0])
        score = root['score'][0]
        #If user has some items. If 'items' array is sent through POST
        if 'items[]' in root:
            items = root['items[]']
        else:
            items = []
        # If USER already has saved games for current game, just update it
        # Save space in the database with this
        if Gameplay.objects.filter(user=user, game=game).exists():
            Gameplay.objects.filter(user=user, game=game).update(score=score)
        #If not, create new save game
        else:
            data = Gameplay(user=user, game=game, score=score)
            data.save()

        # no need to check if gameplay exists, we created it in previous step
        # if it hasnt existed before
        gameplay = Gameplay.objects.get(user=user, game=game)
        # Delete previous items from same Gameplay
        PlayerItem.objects.filter(gameplay=gameplay).delete()
        for item in items:
            data = PlayerItem(gameplay=gameplay, itemName = item)
            data.save()
        return HttpResponse("Game Saved!")
    else:
        return HttpResponse("Not authorized.")

@login_required(login_url='/login/')
@csrf_protect
def loadGame(request):
    if request.method == "POST" and request.is_ajax():
        #create python dictionary from data sent through post request
        root = dict(request.POST.iterlists())
        user = request.user
        game = Game.objects.get(pk = root['game'][0])

        # If previously saved games exists, load them
        if Gameplay.objects.filter(user=user, game=game).exists():
            gameplay = Gameplay.objects.get(user=user, game=game)
            # Prepare response to send to game
            response = {'messageType' : 'LOAD', 'gameState' : {'playerItems' : [], 'score' : gameplay.score}}
            # Fill items array one item a time
            # Same as PlayerItem.objects.all().filter(gameplay=gameplay)
            for item in PlayerItem.objects.filter(gameplay=gameplay):
                response['gameState']['playerItems'].append(item.itemName)
            return JsonResponse(response)
        else:
            return HttpResponse("No saved games to load.")
    else:
        return HttpResponse("Not authorized.")

@login_required(login_url='/login/')
@csrf_protect
def addComment(request,game_name):
    if request.method == "POST" and request.is_ajax():
        #create python dictionary from data sent through post request
        root = dict(request.POST.iterlists())
        if (str(root["comment"][0]) != ""):
            comment = Comment(user=request.user,
                                game=Game.objects.get(name=game_name),
                                commentText=str(root["comment"][0]))
            comment.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("Your comment is empty")
    else:
        return HttpResponse("Not authorized.")

@csrf_protect
def register(request):
    if request.method == 'POST':
        # Render the form from data sent through POST
        form = RegistrationForm(request.POST)
        # If the form is valid, validity of a form is specified in files.py
        # where the form is defined
        if form.is_valid():
            #create user
            user = User.objects.create_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
            email=form.cleaned_data['email']
            )
            # Create our custom user profile
            userProfile = UserProfile(user=user, isDeveloper=form.cleaned_data['isDeveloper'])
            userProfile.save()
            # redirect to success page
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    return render(request,
    'registration/register.html', {'form' : form}
    )
def register_success(request):
    return render(request,
    'registration/success.html', {}
    )

"""
#@csrf_exempt
def upload_prompt(request):
	#direct_upload_complete(request)
	context = dict(direct_form = PhotoDirectForm())
	cl_init_js_callbacks(context['direct_form'], request)
	return render(request, 'cloudinary.html', context)

@csrf_exempt
def direct_upload_complete(request):
	form = PhotoDirectForm(request.POST)
	print(form)
	if form.is_valid():
		form.save()
		print("image saved.............................")
		ret = dict(photo_id = form.instance.id)
	else:
		ret = dict(errors = form.errors)
		print("Not there......")
		
	return HttpResponse(json.dumps(ret), content_type='application/json')

def test(request):
	print("inside test..")
	uploded_image = cloudinary.uploader.upload("C:/Users/user/Desktop/Bluetooth/Sakshyam_Panda.jpg", folder="WSD/", use_filename= 1, unique_filename = 0)
	image_id = uploded_image['public_id']
	return render(request, 'test_cloudinary.html', {'id': image_id })
"""

@login_required(login_url='/login/')	
@csrf_protect
def upload(request):
	context = dict( backend_form = GameImageForm())
	
	if request.method == 'POST':
		form = GameImageForm(request.POST, request.FILES)
		context['posted'] = form.instance
		if form.is_valid():
			form.save()
		
	return render(request, 'myProfile.html', context)

def editProfile(request):
	return render(request, 'editProfile.html', {})