import math
import random
import pygame
from Box2D import b2Filter
from pygame import Vector2
from util import utils

class Ball:
    def __init__(self, pos, radius, color, text="Yes", vel=Vector2(random.uniform(-0, 0), random.uniform(-0, 0))):
        self.color = color
        self.radius = radius # The ball's radius
        self.text = text  # Text parameter ("Yes" or "No")
        
        # Set colors based on text
        if self.text == "Yes":
            self.edge_color = (0, 255, 0)  # Green edge for "Yes"
            self.text_color = (0, 255, 0)  # Green text for "Yes"
            self.trail_color = (0, 255, 0)  # Green trail for "Yes"
        else:  # "No"
            self.edge_color = (255, 0, 0)  # Red edge for "No"
            self.text_color = (255, 0, 0)  # Red text for "No"
            self.trail_color = (255, 0, 0)  # Red trail for "No"
        
        self.circle_body = utils.world.CreateDynamicBody(position=(utils.from_Pos((pos.x, pos.y))))
        self.circle_shape = self.circle_body.CreateCircleFixture(radius=self.radius, density=1, friction=0.0, restitution=1.01)
        self.circle_body.linearVelocity = vel
        self.circle_body.userData = self
        self.destroyFlag = False

        self.trail = []
        self.trail_length = 30
        self.isPlaySound = False

    def update(self):
        # Update the trail
        self.trail.append(Vector2(self.getPos()))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

    def draw(self):
        # Draw the trail with color based on ball type
        if len(self.trail) > 0:
            trail_radius = self.radius * 10  # 10x the size of the ball
            for i, pos in enumerate(self.trail):
                alpha = int(255 * (i / self.trail_length)*0.1)  # Keep your current transparency
                # Use the ball's trail color with transparency
                trail_color = (*self.trail_color[:3], alpha)  # Convert RGB to RGBA with alpha
                surface = pygame.Surface((trail_radius * 2, trail_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, trail_color, (trail_radius, trail_radius), int(trail_radius))
                utils.screen.blit(surface, (int(pos.x - trail_radius), int(pos.y - trail_radius)))

        # Get the current position
        position = utils.to_Pos(self.circle_body.position)
        pos_x, pos_y = int(position[0]), int(position[1])
        radius_px = int(self.radius * utils.PPM)
        
        # Draw the main ball as black
        pygame.draw.circle(utils.screen, (0, 0, 0), (pos_x, pos_y), radius_px)
        
        # Draw the edge with custom color
        edge_thickness = max(1, int(radius_px * 0.1))  # Edge thickness, minimum 1px
        pygame.draw.circle(utils.screen, self.edge_color, (pos_x, pos_y), radius_px, edge_thickness)
        
        # Add the text with custom color
        font_size = int(radius_px * 2.0)  # Font size proportional to radius
        font = pygame.font.SysFont(None, font_size)  # Use default font
        text = font.render(self.text, True, self.text_color)
        
        # Center the text on the ball
        text_rect = text.get_rect(center=(pos_x, pos_y))
        utils.screen.blit(text, text_rect)

    def getPos(self):
        # Get the current position of the ball
        p = utils.to_Pos(self.circle_body.position)
        return Vector2(p[0], p[1])