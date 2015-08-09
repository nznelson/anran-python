from random import randint
import requests
import json
import time

BASE_URL = "http://localhost:8080/"
USER = "bot"
PASS = "bot"
GAME_ID = "16"
WAIT_SECONDS = 5

#client
session = requests.Session()

def sum_without_carry(bnums):
    r = [0]*32
    zipped = zip(*bnums)
    # print zipped
    for i in range(0,32):
        # print sum(zipped[i])
        r[i] = sum(zipped[i]) % 2
    return r

def anran_sum(numbers):
    bnums = []
    for n in numbers:
        bl = [int(i) for i in '{0:032b}'.format(n)]
        # print bl
        bnums.append(bl)
    bsum_str = "".join([str(n) for n in sum_without_carry(bnums)])
    # print bsum_str
    return int(bsum_str, 2)

def login():
    data = {'username': USER, 'password': PASS}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    return session.post(BASE_URL + "login/", data=json.dumps(data), headers=headers)
    

def join_game():
    data = {}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    return session.post(BASE_URL + "games/%s/join" % GAME_ID, data=json.dumps(data), headers=headers)

def get_game():
    data = {}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = session.get(BASE_URL + "games/%s" % GAME_ID, headers=headers)
    return json.loads(r.text)


def still_playing(game):
    return sum([pile.get('amount') for pile in game.get('piles')]) != 0

def do_move(pile_position, amount):
    print "made move pile:%s amount:%s" % (str(pile_position), str(amount))
    data = {
        'pile'  : pile_position,
        'taken' : amount
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    return session.post(BASE_URL + "games/%s/move" % GAME_ID, data=json.dumps(data), headers=headers)

def move(game):

    #for now look at whether i should take all or all-1 from each pile
    pile_numbers = [pile.get('amount') for pile in game.get('piles')]
    for i, pile in enumerate(pile_numbers):
        tmp = pile_numbers[:]
        a = tmp[i]
        if (a == 0):
            continue

        #look them all up, because its fast anyway
        for p in range(0, a+1):
            tmp[i]=p
            if anran_sum(tmp) == 0:
                print tmp
                do_move(i, a-p)
                return
    #didnt find a good move, take one randomly
    print "make random move"
    do_move(randint(0,len(pile_numbers)-1), 1)
    return


def run_bot():
    print login()
    print join_game()
    game = get_game()
    print game
    while still_playing(game):
        print 'yep still playing'
        moves = game.get('moves')
        # 'player': {u'username': u'bot'}
        if (len(moves) == 0 or moves[-1].get('player').get('username')!=USER):
            #if no ones gone yet or its our go
            move(game)

        else:
            print "zzzzz i'll wait for the human"
            time.sleep(WAIT_SECONDS)

        game = get_game()


if __name__ == "__main__":
    assert anran_sum([3,4,5]) == 2, 'anram not working'
    run_bot()