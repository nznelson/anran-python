from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):

    #status'
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"

    #id - auto handled
    #piles - foreign key above
    players = models.ManyToManyField(User)
    status = models.CharField(max_length=255) #open or closed

    def as_json(self):
        return dict(
            id=self.id,
            status=self.status,
            piles=[pile.as_json() for pile in self.pile_set.all().order_by('position')], 
            players=[{"username" : user.username} for user in self.players.all()],
            moves=[move.as_json() for move in self.move_set.all().order_by('date')]
        )

class Pile(models.Model):
    
    position = models.IntegerField() #starts at 0
    amount = models.IntegerField()
    game = models.ForeignKey(Game)

    def as_json(self):
        return dict(
            position = self.position,
            amount = self.amount
        )

class Move(models.Model):
    #for fun maybe we'll track the moves so you can look at past games
    order = models.IntegerField() #when the move happened, start at 0
    game = models.ForeignKey(Game)
    pile = models.ForeignKey(Pile)
    taken = models.IntegerField()
    user = models.ForeignKey(User, null=True)
    date = models.DateTimeField(auto_now_add = True, null=True)

    def __str__(self):
        return " ,".join([str(self.order), str(self.game), str(self.pile), str(self.taken), str(self.user), str(self.date)])

    def as_json(self):
        return dict(
            order=self.order,
            taken=self.taken,
            player={"username" : self.user.username},
            date=str(self.date),
        )