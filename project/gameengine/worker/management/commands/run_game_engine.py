"""
Management command to run the game engine process
"""
import logging
import signal
import sys
from django.core.management.base import BaseCommand

from worker.src.game_engine_process import GameEngineProcess

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the game engine process that polls for ready games and starts game subprocesses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_engine = None
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        self.stdout.write(self.style.WARNING(f"Received signal {signum}, shutting down..."))
        if self.game_engine:
            self.game_engine.stop()
        sys.exit(0)

    def handle(self, *args, **options):
        """Run the game engine process"""
        self.stdout.write(self.style.SUCCESS('Starting Game Engine Process'))
        
        try:
            # Create and start the game engine process
            self.game_engine = GameEngineProcess()
            self.game_engine.start()
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Game Engine Process interrupted by user'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error running Game Engine Process: {str(e)}'))
            logger.exception("Error in Game Engine Process")
        finally:
            if self.game_engine:
                self.game_engine.stop()
            
            self.stdout.write(self.style.SUCCESS('Game Engine Process stopped'))
