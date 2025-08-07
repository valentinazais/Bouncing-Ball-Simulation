import colorsys
import pygame
import math
from Box2D import b2World
from pygame.locals import *
from pygame import Vector2, mixer, time
from MyContactListener import MyContactListener

class Utils:
    def __init__(self):
        pygame.init()
        
        # Obtenir les dimensions de l'écran
        info = pygame.display.Info()
        screen_height = info.current_h - 100  # Laisser un peu d'espace pour la barre de tâches/menu
        
        # Calculer la largeur proportionnelle (ratio 2:3)
        self.height = screen_height
        self.width = int(screen_height * (9/16))

        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF, 16)
        self.dt = 0
        self.clock = pygame.time.Clock()

        self.currentScreen = None

        self.font8 = pygame.font.Font('assets/pixel.ttf', 8)
        self.font12 = pygame.font.Font('assets/pixel.ttf', 12)
        self.font16 = pygame.font.Font('assets/pixel.ttf', 16)
        self.font32 = pygame.font.Font('assets/pixel.ttf', 32)

        self.world = b2World(gravity=(0, -20), doSleep=True)
        self.contactListener = MyContactListener()
        self.world.contactListener = self.contactListener

        self.PPM = 10.0  # Pixels per meter

        self.fps = 0
        self.fpsCounter = 0
        self.fpsTimeCount = 0
        self.time = 0

    # Le reste du code reste inchangé...


    def to_Pos(self, pos):
        """Convert from Box2D to Pygame coordinates."""
        return (pos[0] * self.PPM, self.height - (pos[1] * self.PPM))

    def from_Pos(self, pos):
        """Convert from Pygame to Box2D coordinates."""
        return (pos[0] / self.PPM, (self.height - pos[1]) / self.PPM)

    def initDeltaTime(self):
        t = self.clock.tick(60 * 2)
        self.dt = t / 1000

    def deltaTime(self):
        return self.dt

    def showFps(self):
        self.fpsTimeCount += self.deltaTime()
        self.fpsCounter += 1
        if self.fpsTimeCount > 1:
            self.fpsTimeCount = 0
            self.fps = self.fpsCounter
            self.fpsCounter = 0

        if self.fps >= 50:
            self.drawText(Vector2(0, 0), "fps: " + str(self.fps), (0, 0, 0), self.font16)
        else:
            self.drawText(Vector2(0, 0), "fps: " + str(self.fps), (0, 0, 0), self.font16)

    def drawText(self, pos, text, color, font):
        """Draw text at a specific position using a given font."""
        text = font.render(text, True, color)
        self.screen.blit(text, (pos.x, pos.y))

    def draw_text(self, text, position, font_size=30, color=(255, 255, 255)):
        """A simple utility to draw text centered at a position."""
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        self.screen.blit(text_surface, text_rect)

    def distance(self, x1, y1, x2, y2):
        return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) * 1.0)

    def rotate(self, surface, angle, pivot, offset):
        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)
        rotated_offset = offset.rotate(angle)
        rect = rotated_image.get_rect(center=pivot + rotated_offset)
        return rotated_image, rect

    def hueToRGB(self, hue):
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        return int(r * 255), int(g * 255), int(b * 255)

    def saturationToRGB(self, saturation, hue=0.0, value=1.0):
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return int(r * 255), int(g * 255), int(b * 255)


utils = Utils()  # util is global object
