import math
import random
import pygame
from util import utils

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # CHANGE 1: Reduce particle size
        self.radius = random.uniform(1,1)  # Reduced from 1,1
        angle = random.uniform(80, 90)
        # CHANGE 2: Reduce particle speed/dispersion
        speed = random.uniform(-4, 4)  # Reduced from -3,3
        self.vel_x = math.cos(math.radians(angle)) * speed
        self.vel_y = math.sin(math.radians(angle)) * speed
        # CHANGE 3: Reduce particle lifetime
        self.life = random.randint(10, 30)  # Reduced from 100,150

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Explosion:
    def __init__(self, x, y, color):
        # Create particles
        self.particles = []
        COLORS = [color]
        # CHANGE 4: Reduce number of particles per explosion
        for _ in range(1):  # Reduced from 5
            color = random.choice(COLORS)
            particle = Particle(x, y, color)
            self.particles.append(particle)

    def update(self):
        for particle in self.particles:
            particle.update()
        self.particles = [particle for particle in self.particles if particle.life > 0]

    def draw(self):
        for particle in self.particles:
            particle.draw(utils.screen)

class Raindrop:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.uniform(1, 1)  # Make the raindrops small
        self.vel_y = random.uniform(2, 10)  # Set the speed for the raindrops
        self.vel_x = 0  # Horizontal velocity (can be adjusted if needed)
        self.life = random.randint(300, 500)  # Adjust as needed

    def update(self, rings):
        self.y += self.vel_y
        self.x += self.vel_x

        # Check for collision with the rings
        for ring in rings:
            if self.is_colliding_with_ring(ring):
                self.resolve_collision_with_ring(ring)

        # If the raindrop goes off the bottom, respawn at the top
        if self.y > utils.height:
            self.y = -10
            self.x = random.uniform(0, utils.width)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))

    def is_colliding_with_ring(self, ring):
        """Check if the raindrop is colliding with the ring."""
        ring_center = ring.center
        distance = math.sqrt((self.x - ring_center.x) ** 2 + (self.y - ring_center.y) ** 2)
        ring_outer_radius = ring.radius + 5  # Add some padding for collision
        ring_inner_radius = ring.radius - 5  # Consider the thickness of the ring

        return ring_inner_radius <= distance <= ring_outer_radius

    def resolve_collision_with_ring(self, ring):
        """Adjust raindrop's position so it gets pushed to the side of the ring."""
        ring_center = ring.center

        # Calculate the direction from the ring center to the raindrop
        direction_x = self.x - ring_center.x
        direction_y = self.y - ring_center.y

        # Normalize the direction vector
        magnitude = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if magnitude > 0:
            direction_x /= magnitude
            direction_y /= magnitude



class Rain:
    def __init__(self, num_drops, color):
        self.raindrops = []
        self.color = color
        for _ in range(num_drops):
            x = random.uniform(0, utils.width)
            y = random.uniform(0, utils.height)
            raindrop = Raindrop(x, y, self.color)
            self.raindrops.append(raindrop)

    def update(self, rings):
        for raindrop in self.raindrops:
            raindrop.update(rings)

    def draw(self, screen):
        for raindrop in self.raindrops:
            raindrop.draw(screen)