import pygame
import math
from os.path import join 
from os import walk
from re import sub

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 660
# WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1020
WORLD_SCALE = 2.5
TILE_SIZE = 32 * WORLD_SCALE
PLAYER_SIZE = 120
BAT_SIZE = 80
BAT_ATTACK_SIZE = 96
