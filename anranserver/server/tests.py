from django.test import TestCase
from models import Game, Pile, Move
from django.contrib.auth.models import User
from django.test import Client
import json

class ModelTest(TestCase):

    def setUp(self):
        game = Game(status=Game.OPEN)
        game.save()

    def test_pile_move_added(self):
        game = Game.objects.get()

        new_pile = Pile(
                    position = 0,
                    amount = 3,
                    game = game
                )
        new_pile.save()
        new_move = Move(
            #start at 0th move
            order = 0,
            game = game,
            pile = new_pile,
            taken = 2
        )
        new_move.save()
        self.assertEqual(len(game.pile_set.all()), 1)
        self.assertEqual(len(game.move_set.all()), 1)

    def test_simple_game(self):

        game = Game.objects.get()
        #create 3 piles - 2,3,4
        for i, p in enumerate([2,3,4]):
            new_pile = Pile(
                position = i,
                amount = p,
                game = game
            )
            new_pile.save()
        self.assertEqual(len(game.pile_set.all()), 3)

        #create a couple users
        user_one = User.objects.create_user("one", password="one")
        user_one.save()
        user_two = User.objects.create_user("two", password="two")
        user_two.save()
        
        #add them to the game
        game.players.add(user_one)
        game.players.add(user_two)
        game.save()

        #reget the game
        game = Game.objects.get()
        self.assertEqual(len(game.players.all()), 2)

        #test a basic set of three moves, each player taking the max on each
        for i, (user, take) in enumerate([(user_one, 2), (user_two, 3), (user_one, 4)]):

            pile = game.pile_set.get(position = i)
            self.assertEqual(pile.amount, take)
            pile.amount = 0
            pile.save()
            #create a corresponding move
            new_move = Move(
                #start at 0th move
                order = i,
                game = game,
                pile = pile,
                taken = take,
                user = user
            )
            new_move.save()
        
        #check it went user 1, user 2, user 1
        moves = game.move_set.all().order_by('date')
        self.assertEqual(len(moves), 3)
        # print moves[0]
        # print moves[1]
        # print moves[2]
        self.assertEqual(moves[0].user, user_one)
        self.assertEqual(moves[1].user, user_two)
        self.assertEqual(moves[2].user, user_one)

class ViewTest(TestCase):

    def test_simple_flow(self):

        #john create account
        c1 = Client()
        info = {'username': 'john', 'password': 'smith'}
        response = c1.post('/users/', data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # print response.content

        #bot create account
        c2 = Client()
        info = {'username': 'bot', 'password': 'bot'}
        response = c2.post('/users/', data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # print response.content
        #check that games returns empty list
        
        response = c1.get('/games/', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.content, [])

        #john create a game
        info = {
            'amounts' : [3,4,5] # counts of tokens
        }
        response = c1.post('/games/', data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        # print response.content
        json_data = json.loads(response.content)
        game_id = json_data.get('id')
        # print "gameid %s" % game_id

        #john gets the individual game to check
        response = c1.get('/games/%s' % game_id,
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # print response.content

        #bot join
        
        response = c2.post('/games/%s/join' % game_id, data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # print response.content

        #john make a move
        info = {
            #take 4 off the last one that started with 5
            'pile' : 2,
            'taken' : 4
        }
        response = c1.post('/games/%s/move' % game_id, data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # print response.content
        #make sure that pile 2 was updated to 1
        json_data = json.loads(response.content)
        self.assertEqual(json_data.get('piles')[2].get('amount'), 1)

        #bot make a move
        #try to take more than possible
        info = {
            #take 2 off the last one that only has 1 left
            'pile' : 2,
            'taken' : 2
        }
        response = c2.post('/games/%s/move' % game_id, data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 500)
        #now take a good amount
        info = {
            #take 4 off the last one that started with 5
            'pile' : 2,
            'taken' : 1
        }
        response = c2.post('/games/%s/move' % game_id, data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # print response.content
        #make sure that pile 2 was updated to 0
        json_data = json.loads(response.content)
        self.assertEqual(json_data.get('piles')[2].get('amount'), 0)

        #now bot try to make a move when he can't again
        response = c2.post('/games/%s/move' % game_id, data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 500)
        # print response.content

        #john take all of 1
        info = {
            'pile' : 1,
            'taken' : 4
        }
        response = c1.post('/games/%s/move' % game_id, data=json.dumps(info),
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # print response.content
        #make sure that pile 2 was updated to 1
        json_data = json.loads(response.content)
        self.assertEqual(json_data.get('piles')[1].get('amount'), 0)

        #bot take the rest
        info = {
            'pile' : 0,
            'taken' : 3
        }
        response = c2.post('/games/%s/move' % game_id, data=json.dumps(info),
                                content_type='application/json')
        # print response.content
        json_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_data.get('piles')[0].get('amount'), 0)
        










        
        