# Game Configurations

This document defines the default settings and configurations for all games in the platform.

## TowerDefense

### Description
A strategic defense game where players place various types of towers to defend against waves of enemies. The game features 10 different tower types and 10 enemy types with a continuous flow of enemies. Players don't "win" in the traditional sense - the goal is to survive as long as possible and see how far they can progress. Once all enemies in a wave are cleared, the next wave begins with increased difficulty.

### Game Parameters
- **Max Players**: 1
- **Frames Per Second**: 1

### Settings
- **per_wave_enemies**: 20
- **per_wave_difficulty_multiplier**: 1.2
- **initial_money**: 1000
- **initial_lives**: 20
- **max_total_powerups**: 5
- **max_tower_upgrades**: 3

## StarDefenders

### Description
A space-themed shooter where players pilot starships and defend against incoming enemy waves. Players must shoot enemies to clear them while collecting powerups and dodging enemy fire. The game tests reflexes and strategic positioning.

### Game Parameters
- **Max Players**: 4
- **Frames Per Second**: 1

### Settings
- **initial_lives**: 3
- **map_length**: 1000
- **map_height**: 800

## Bong

### Description
A unique take on the classic pong concept. Players control a small rectangle that moves around a square room with a bouncing ball. When the player's paddle makes contact with the ball, it emits a flashy wave and the text "BONG!" appears and floats upward before disappearing. Players earn a point for each hit and win when they reach the target score. The ball bounces randomly around the room and reacts to contact with the player's colored rectangle. Players can move their rectangle using arrow keys but cannot change its orientation.

### Game Parameters
- **Max Players**: 1
- **Frames Per Second**: 1

### Settings
- **hits_to_win**: 10
