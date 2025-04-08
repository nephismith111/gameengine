# Generated manually
from django.db import migrations


def load_initial_game_types(apps, schema_editor):
    """
    Load initial game types from GAMES.md configuration.
    This is idempotent - it won't create duplicates if run multiple times.
    """
    GameType = apps.get_model('gameengine', 'GameType')
    
    # TowerDefense game
    tower_defense, created = GameType.objects.get_or_create(
        name='TowerDefense',
        defaults={
            'description': 'A strategic defense game where players place various types of towers to defend against waves of enemies.',
            'image_url': '/static/gameengine/images/tower_defense.svg',
            'max_players': 4,
            'default_settings': {
                'frames_per_second': 1,
                'per_wave_enemies': 20,
                'per_wave_difficulty_multiplier': 1.2,
                'initial_money': 1000,
                'initial_lives': 20,
                'max_total_powerups': 5,
                'max_tower_upgrades': 3
            }
        }
    )
    
    # StarDefenders game
    star_defenders, created = GameType.objects.get_or_create(
        name='StarDefenders',
        defaults={
            'description': 'A space-themed shooter where players pilot starships and defend against incoming enemy waves.',
            'image_url': '/static/gameengine/images/star_defenders.svg',
            'max_players': 4,
            'default_settings': {
                'frames_per_second': 1,
                'initial_lives': 3,
                'map_length': 1000,
                'map_height': 800
            }
        }
    )
    
    # Bong game
    bong, created = GameType.objects.get_or_create(
        name='Bong',
        defaults={
            'description': 'A unique take on the classic pong concept.',
            'image_url': '/static/gameengine/images/bong.svg',
            'max_players': 2,
            'default_settings': {
                'frames_per_second': 1,
                'hits_to_win': 10
            }
        }
    )


def reverse_func(apps, schema_editor):
    """
    This migration is idempotent, so we don't need to do anything for reverse.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gameengine', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_game_types, reverse_func),
    ]
