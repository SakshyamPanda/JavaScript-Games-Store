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
from .models import DeveloperGame
from .files import *
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
import json
from django.http import JsonResponse
from hashlib import md5
import cloudinary, cloudinary.uploader, cloudinary.forms
import datetime
from datetime import date, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#For banking service
secret_key = "26d3858162e10dc081f786319f286025" #This is from the secret key generator they provided. Dunno if this is the right way to put it

import cloudinary, cloudinary.uploader, cloudinary.api
#from cloudinary.uploader import upload
#from cloudinary.utils import cloudinary_url
#from cloudinary.api import delete_resources_by_tag, resources_by_tag
from django import forms
from cloudinary.forms import cl_init_js_callbacks
#from .models import GameImage, ProfileImage
#from .files import GameImageForm, ProfileImageForm
from .files import UploadPhoto
from cloudinary.models import CloudinaryField

cloudinary.config(
  cloud_name = "sakshyam",
  api_key = "623965587187774",
  api_secret = "Lf7ULK0njrZJlVdwopnjsMeLdfM"
)


#For Email Verification
fromaddr='wsdAwsomeProject@gmail.com'
username=fromaddr
password='reljathegreat'


# Landing page showing recent uploaded games
def home(request):
	enddate = date.today()
	startdate = enddate - timedelta(days=31)
	print(startdate, enddate)
	games = Game.objects.filter(created__range=[startdate, enddate])
	return render(request, "home.html", {'games': games })


@login_required(login_url='/login/')
def myProfile(request):
    userProfile = UserProfile.objects.get(user=request.user)
    context = dict( backend_form = UploadGameForm())
    if request.method == 'POST' and userProfile.isDeveloper:
        form = UploadGameForm(request.POST, request.FILES)
        context['posted'] = form.instance
        success = False
        if form.is_valid():
			#game = Game(name=form.cleaned_data['name'], url=form.cleaned_data['url'], price=form.cleaned_data['price'], description=form.cleaned_data['description'], image=form.cleaned_data['image'])
			#game.save()
			#form = UploadGameForm()
            success = True
            form.save()
            devGame = DeveloperGame(user=request.user, game=Game.objects.get(name=form.cleaned_data['name']))
            devGame.save()
    else:
        form = UploadGameForm()
        success = False
    return render(request, "myProfile.html", {"userProfile" : userProfile, "form" : form, "success" : success, "context" : context  })

@login_required(login_url='/login/')
@csrf_protect
def editProfile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            update = form.save(commit=False)
            update.set_password(form.cleaned_data['password'])
            update.save()
            #User.objects.get().update(email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
    else:
        form = UpdateProfileForm()
    return render(request, "editProfile.html", {'form' : form} )

def browseGames(request):
    games = Game.objects.all()
    return render(request, "browseGames.html", {"games" : games })


# About page- introduction to the project and Team members
def about(request):
    return render(request, "about.html", {})


@login_required(login_url='/login/')
def buyGame(request, game_name):
        #I am defining the variables here and then the buyGame.html will only have the variable names
        #This is querying the game object with the name parameter
        game = Game.objects.get(name = game_name)  #game primary key to be queried from the game table
        pid = game.pk
        sid = "pandareljasharbel" #this is fxed for our service
        amount = game.price #this is game price queried form game table



        #The next three could be implemented in one url and then the response parameter from the paymen service will be different
        success_url = request.build_absolute_uri("../payment")
        cancel_url =  success_url
        error_url =  success_url

        #The checksum is calculated from pid, sid, amount, and your secret key. The string is formed like this:
        checksumstr = "pid={}&sid={}&amount={}&token={}".format(pid, sid, amount, secret_key)


        # checksumstr is the string concatenated above
        m = md5(checksumstr.encode("ascii"))
        # checksum is the value that should be used in the payment request
        checksum = m.hexdigest()


        return render(request, "buyGame.html", {"pid": pid, "sid":sid, "amount":amount,
            "success_url": success_url, "cancel_url":cancel_url, "error_url":error_url,
            "checksum":checksum})

#TODO: implement the different pages for the different results
@login_required
def buyGameResult(request,game_name):
	if request.method == "GET":
		#this is supposed to be the result from the payment service, whether success, error, or cancel. (Step 3 in bank api)
		#print(game_name)
		root = request.GET
		pid = root['pid']
		ref = root['ref']
		result = root['result']
		checksum_from_url = root['checksum']

		#The checksum is calculated from pid, sid, amount, and your secret key. The string is formed like this:
		checksumstr = "pid={}&ref={}&result={}&token={}".format(pid, ref, result, secret_key)

		# checksumstr is the string concatenated above
		m = md5(checksumstr.encode("ascii"))
		checksum = m.hexdigest()

		if checksum != checksum_from_url:
			print('la ya 7abeebi')
			response = "No Habeebi, don't even try that"
			return render(request, "buyGameResult.html", {'response' : response})
			#return HttpResponseRedirect('/game/'+game_name+'/')
			#raise Http404

		else:
			if( result == 'error'):
				#'pass' if you comment the rest and don't want to do anything here
				response = "Oops.. Something went wrong with the payment. Don't worry, your money is still in your pocket, though."
				#raise Http404

			if( result == 'success'):
				user = request.user #The user is passed from "request"
				game= Game.objects.get(name=game_name) #query the game from the Game object
				transaction = Transaction(user=user,game=game)
				transaction.save() #save the transactio to the database
				return HttpResponseRedirect('/game/'+game_name+'/')

			if( result == 'cancel'):
				response = 'cancel'
				return HttpResponseRedirect('/game/'+game_name+'/')


			print(root)
			return render(request, "buyGameResult.html", {'response' : response})

	else:
		return HttpResponse('Not authorised')

#Main view where user plays game
@login_required(login_url='/login/')
def game(request, game_name):
	print(request.FILES)
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

		# userComments holds information about comments and userProfile of users who made comments
		userComments = []
		for comment in comments:
			userProfile = UserProfile.objects.filter(user=comment.user).first()
			userComments.append([comment,userProfile])
		#print(userComments)
	# In case game does not exist, display 404
	except Game.DoesNotExist:
		raise Http404
	return render(request, "game.html", {"game" : game, "scores" : scores, "gameBought" : gameBought, "userComments": userComments})

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

            username=request.POST['username']
            password=request.POST['password1']
            user=authenticate(username=username,password=password)

            user.is_active=False
            user.save()

            id=user.id
            email=user.email
            url = request.build_absolute_uri(reverse('activation', args=(id, )))
            send_email(email,url)

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

def activation(request,id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Http404
    user.is_active=True
    user.save()
    return HttpResponseRedirect('/')

def send_email(toaddr,url):

	text = "Hi!\n To finish registration, follow this link to activate your account:%s" %(url)
	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	msg = MIMEMultipart('alternative')
	msg.attach(part1)
	subject="Activate your account at WSD Awsome Project"
	msg="""\From: %s\nTo: %s\nSubject: %s\n\n%s""" %(fromaddr,toaddr,subject,msg.as_string())
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr,[toaddr],msg)
	server.quit()


def upload(request):
	context = dict( backend_form = UploadPhoto())
	if request.method == 'POST':
		form = UploadPhoto(request.POST, request.FILES)
		print("form instance: ", form.instance)
		context['posted'] = form.instance
		if form.is_valid():
			form.save()

	return render(request, 'test.html', context)

# TODO: @sharbel, As a developer, they should be able to: see list of game sales
@login_required(login_url='/login/')
def manageUploadedGames(request):
    # This should be the view for the developer to see all the games she created, who bought their games, edit game details, and request to remove their uploaded games.

    developerProfile = UserProfile.objects.get(user=request.user)
    if developerProfile.isDeveloper:
        DeveloperGames = DeveloperGame.objects.all().filter(user=request.user)
        games = []
        for game in DeveloperGames:
            games.append(game.game)
        #Display the games
    else:
        return HttpResponseRedirect('/') #in case address is typed, this redirects them to hom (secure stuff)
    #games = DeveloperGame.objects.get(user=request.user, game = request.game) #QUERY the games by this developer (.get or .filter?)

    return render(request, "manageUploadedGames.html", {"developerProfile": developerProfile, 'games' : games})

# TODO: @sharbel, When a game is clicked in manageUploadedGames, you can Edit its details, request to change the price (or just lock the price), and view the game sales
@login_required(login_url='/login/')
def manageGame(request):
    #Import all game details to view them.
    #Make some changeable while others locked (like price?)
    #This is probably implemented as a form.. check about POST resquest

    #View game sales
    return render(response, "manageGame.html", {"game": game})
