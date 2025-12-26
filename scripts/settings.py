import pygame
import math
from os.path import join 
from os import walk
from re import sub
from random import randrange, randint, choice, uniform

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 660
# WINDOW_WIDTH, WINDOW_HEIGHT = 1920, 1020
WORLD_SCALE = 2.5
TILE_SIZE = 32 * WORLD_SCALE
PLAYER_SIZE = 48 * WORLD_SCALE
BAT_SIZE = 32 * WORLD_SCALE
BAT_ATTACK_SIZE = 38 * WORLD_SCALE
SKELETON_SIZE = 56 * WORLD_SCALE
SKELETON_ATTACK_SIZE = 24 * WORLD_SCALE
