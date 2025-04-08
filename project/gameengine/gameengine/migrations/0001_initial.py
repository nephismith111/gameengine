# Generated manually
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GameType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('image_url', models.URLField(blank=True)),
                ('max_players', models.PositiveIntegerField(default=4)),
                ('description', models.TextField(blank=True)),
                ('default_settings', models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='GameInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('instance_name', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('ongoing', 'Ongoing'), ('ended', 'Ended')], default='pending', max_length=20)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('started_datetime', models.DateTimeField(blank=True, null=True)),
                ('ended_datetime', models.DateTimeField(blank=True, null=True)),
                ('game_data', models.JSONField(default=dict)),
                ('game_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instances', to='gameengine.gametype')),
            ],
            options={
                'ordering': [models.Case(models.When(status='pending', then=0), models.When(status='ongoing', then=1), models.When(status='ended', then=2), default=3, output_field=models.IntegerField()), 'started_datetime'],
            },
        ),
    ]
