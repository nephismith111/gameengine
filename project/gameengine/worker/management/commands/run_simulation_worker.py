from django.core.management.base import BaseCommand
import os
import django
import asyncio
from channels.worker import Worker
from channels.routing import ProtocolTypeRouter, ChannelNameRouter
from channels.layers import get_channel_layer
from project.gameengine.worker.src.simulation import SimulationConsumer


class Command(BaseCommand):
    help = 'Runs the simulation worker for game engine'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting simulation worker...'))
        
        # Set up the application routing
        application = ProtocolTypeRouter({
            "channel": ChannelNameRouter({
                "simulation": SimulationConsumer.as_asgi(),
            }),
        })
        
        # Get the channel layer
        channel_layer = get_channel_layer()
        
        # Create a worker that listens to the 'simulation' channel
        worker = Worker(
            application=application,
            channels=["simulation"],
            channel_layer=channel_layer,
        )
        
        self.stdout.write(self.style.SUCCESS('Worker configured, starting event loop...'))
        
        # Run the worker (this is blocking)
        asyncio.run(worker.run())
