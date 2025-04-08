import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class GameType(models.Model):
    """
    Model representing a type of game available in the system.
    Game types are predefined and loaded from GAMES.md.
    """
    name = models.CharField(max_length=100, unique=True)
    image_url = models.URLField(blank=True)
    max_players = models.PositiveIntegerField(default=4)
    description = models.TextField(blank=True)
    default_settings = models.JSONField(default=dict)
    
    def __str__(self):
        return self.name

class GameInstance(models.Model):
    """
    Model representing an instance of a game.
    Each instance has a unique UUID, status, and game-specific data.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ONGOING = 'ongoing', 'Ongoing'
        ENDED = 'ended', 'Ended'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_type = models.ForeignKey(GameType, on_delete=models.CASCADE, related_name='instances')
    instance_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_datetime = models.DateTimeField(auto_now_add=True)
    started_datetime = models.DateTimeField(null=True, blank=True)
    ended_datetime = models.DateTimeField(null=True, blank=True)
    game_data = models.JSONField(default=dict)
    
    class Meta:
        ordering = [
            models.Case(
                models.When(status=Status.PENDING, then=0),
                models.When(status=Status.ONGOING, then=1),
                models.When(status=Status.ENDED, then=2),
                default=3,
                output_field=models.IntegerField(),
            ),
            'started_datetime'
        ]
    
    def __str__(self):
        return f"{self.instance_name} ({self.game_type.name})"
    
    @property
    def joined_users(self):
        """Return the list of users who have joined this game."""
        return self.game_data.get('joined_users', [])
    
    @property
    def player_count(self):
        """Return the number of players who have joined this game."""
        return len(self.joined_users)
    
    @property
    def is_joinable(self):
        """Check if the game can be joined by new players."""
        return (
            self.status == self.Status.PENDING and 
            self.player_count < self.game_type.max_players
        )
