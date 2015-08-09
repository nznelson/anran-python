from models import Game, Pile, Move
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseServerError, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

logger = logging.getLogger(__name__)


def get_model_json(objects):
    data = serializers.serialize('json', objects)
    struct = json.loads(data)
    if (len(struct) > 0):
        struct = struct[0]
    
    data = json.dumps(struct)
    # return data
    return HttpResponse(data, content_type='application/json')

def get_json(objects):
    if type(objects) is list:
        processed = [obj.as_json() for obj in objects]
    else:
        processed = objects.as_json()
    data = json.dumps(processed)
    # return data
    return HttpResponse(data, content_type='application/json')

def user_json_response(user):
    
    data =  json.dumps({
        "username"    : user.username,
        "last_login"  : str(user.last_login),
        "date_joined" : str(user.date_joined)
    })
    return HttpResponse(data, content_type='application/json')

#/login
@csrf_exempt
def login_user(request):

    if request.method == 'POST':
        json_data = json.loads(request.body)
        user = authenticate(username=json_data['username'], password=json_data['password'])
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                print("User is valid, active and authenticated")
                return user_json_response(user)
            else:
                print("The password is valid, but the account has been disabled!")
                return HttpResponse('Unauthorized', status=401)
        else:
            # the authentication system was unable to verify the username and password
            print("The username and password were incorrect.")
            return HttpResponse('Unauthorized', status=401)
    else:
        return HttpResponseNotFound("Page doesnt exist")

#/user/
@csrf_exempt
def signup_user(request):
    logger.debug("here")
    if request.method == 'POST':
        #create a user
        try:
            json_data = json.loads(request.body)
            user = User.objects.create_user(json_data['username'], password = json_data['password'])
            user.save()
            #now log them in
            login_user(request)
            return user_json_response(user)
        except:
            HttpResponseServerError("Something went wrong :(")
    else:
        return HttpResponseNotFound("Page doesnt exist")

#/game/
@csrf_exempt
def game(request):

    #check if authed
    # print "user " + str(request.user)
    if not request.user.is_authenticated():
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'GET':
        #return a list of games available
        return get_json(list(Game.objects.all()))
    elif request.method == 'POST':
        # make sure authed

        try:
            json_data = json.loads(request.body)
            # user = this user
            new_game = Game(status = Game.OPEN)
            new_game.save()
            new_game.players.add(request.user)
            amounts = json_data['amounts']
            for i, amount in enumerate(amounts):
                new_pile = Pile(
                    position = i,
                    amount = amount,
                    game = new_game
                )
                new_pile.save()
            return get_json(new_game)
        except Exception, e:
            return HttpResponseServerError("Malformed data!")

#/game/id
@csrf_exempt
def game_single(request, game_id):

    #check if authed
    if not request.user.is_authenticated():
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'GET':
        #return the specific game
        try:
            game = Game.objects.get(id = game_id)
            return get_json(game)
        except Game.DoesNotExist:
            return HttpResponseNotFound("Game doesnt exist")
        except Exception, e:
            # print e
            HttpResponseServerError("Something went wrong :(")
    else:
        return HttpResponseNotFound("Page not found")
        

#/game/{id}/join
@csrf_exempt
def join_game(request, game_id):

    if not request.user.is_authenticated():
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        #get current user
        # make sure authed
        try:
            game = Game.objects.get(id = game_id)
            players = list(game.players.all())
            if (len(players) >= 2):
                return HttpResponseServerError("Already maxed out game")
            if (players[0].username == request.user.username):
                return HttpResponseServerError("You've already joined")
            game.players.add(request.user)
            game.save()
            return get_json(game)
        except Game.DoesNotExist:
            return HttpResponseNotFound("Game doesnt exist")
        except Exception, e:
            return HttpResponseServerError("Something went wrong :(")
    else:
        return HttpResponseNotFound("Page not found")

#/game/{id}/move
@csrf_exempt
def make_move(request, game_id):

    if not request.user.is_authenticated():
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
       # make sure authed & joined
        try:
            json_data = json.loads(request.body)
            #so check that the pile is valid
            game = Game.objects.get(id = game_id)

            usernames = [player.username for player in list(game.players.all())]
            if (request.user.username not in usernames):
                return HttpResponseServerError("Error, you havent joined this game")

            #check that it's this users turn to go
            moves = game.move_set.all().order_by('date')
            
            if (len(moves) > 0 and moves.last().user.username == request.user.username):
                #then this user went last, error pls
                return HttpResponseServerError("Error, wait for the other play to move")

            #expecting a "move"
            # {
            #     pile : 0
            #     taken : 5
            # }
            # By default, this Manager is named FOO_set, where FOO is the source model name, lowercased.
            piles = game.pile_set.all() # Returns all pile objects related to game.
            pile_pos = json_data['pile']
            if not (pile_pos >=0 and pile_pos < len(piles)):
                #invalid pile id
                return HttpResponseServerError("invalid pile id")
            pile_pull = game.pile_set.get(position=pile_pos)
            taken = int(json_data['taken'])
            if (taken > pile_pull.amount):
                return HttpResponseServerError("invalid, trying to take more than %s available" % (str(pile_pull.amount)))
            if (taken <= 0):
                return HttpResponseServerError("invalid, trying to take 0 or less")
            #we should be good
            #update the pile

            pile_pull.amount = pile_pull.amount - taken
            pile_pull.save()
            #create a move
            new_move = Move(
                #start at 0th move
                order = len(moves),
                game = game,
                pile = pile_pull,
                taken = taken,
                user = request.user
            )
            new_move.save()
            return get_json(Game.objects.get(id = game_id)) 
        except Game.DoesNotExist:
            return HttpResponseNotFound("Game doesnt exist")
        except Exception, e:
            return HttpResponseServerError("Malformed data!")

