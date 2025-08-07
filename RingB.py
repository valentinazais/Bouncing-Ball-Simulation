import math
import random

import pygame
from Box2D import b2EdgeShape, Box2D, b2Filter
from pygame import Vector2

from particle import Explosion
from util import utils

class RingB:
    def __init__(self, id, radius, dir=1, sar=0, hue=0):
        # Generate a random color for the ring
        self.original_color = self.generate_random_color()
        self.color = self.original_color  # Current display color
        self.pulse_color = None  # Color to blend with during pulse
        self.pulse_intensity = 0.0  # 0.0 = original color, 1.0 = full pulse color
        
        self.radius = radius
        self.target_radius = radius  # New property to track target radius for shrinking
        self.id = id
        self.sar = sar
        self.hue = hue
        self.center = Vector2(utils.width/2, utils.height/2)
        self.shrink_speed = 15.0  # Speed of shrinking animation

        self.rotateDir = dir
        self.size = 50
        self.vertices = []
        for i in range(self.size):
            angle = i * (2 * math.pi / self.size)
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            self.vertices.append((x, y))

        pos = Vector2(utils.width / 2, utils.height / 2)
        self.body = utils.world.CreateStaticBody(position=utils.from_Pos(pos))
        self.body.userData = self

        self.create_edge_shape()
        self.destroyFlag = False

        self.points = []
        for i in range(self.size):
            angle = i * (2 * math.pi / self.size)
            x = self.center.x + radius * 10 * math.cos(angle)
            y = self.center.y + radius * 10 * math.sin(angle)
            self.points.append(Vector2(x, y))

        self.body.angle = math.radians(90 + 20)
        
        # Flag to indicate if this ring is currently shrinking
        self.is_shrinking = False
    
    def generate_random_color(self):
        """Generate a random vibrant color for the ring."""
        # Method 1: Using HSV for more vibrant colors
        h = random.random()  # Random hue between 0 and 1
        s = random.uniform(0.7, 1.0)  # High saturation for vibrant colors
        v = random.uniform(0.7, 1.0)  # High value for bright colors
        r, g, b = utils.hueToRGB(h)
        return (r, g, b)

    def set_pulse_color(self, pulse_color, intensity):
        """Set the pulse color and intensity for blending."""
        self.pulse_color = pulse_color
        self.pulse_intensity = max(0.0, min(1.0, intensity))  # Clamp between 0 and 1
        self.update_display_color()

    def clear_pulse(self):
        """Clear the pulse effect and return to original color."""
        self.pulse_color = None
        self.pulse_intensity = 0.0
        self.color = self.original_color

    def update_display_color(self):
        """Update the display color by blending original and pulse colors."""
        if self.pulse_color is None or self.pulse_intensity <= 0.0:
            self.color = self.original_color
        else:
            # Blend the original color with the pulse color
            r1, g1, b1 = self.original_color
            r2, g2, b2 = self.pulse_color
            
            # Linear interpolation between colors
            r = int(r1 * (1 - self.pulse_intensity) + r2 * self.pulse_intensity)
            g = int(g1 * (1 - self.pulse_intensity) + g2 * self.pulse_intensity)
            b = int(b1 * (1 - self.pulse_intensity) + b2 * self.pulse_intensity)
            
            self.color = (r, g, b)

    def create_edge_shape(self):
        if self.size == 50:
            for i in range(self.size):
                angle = i * (360 / self.size)
                if (90 <= angle <= 360):  # Modified: Changed from (0 <= angle <= 300) to move hole higher
                    v1 = self.vertices[i]
                    v2 = self.vertices[(i + 1) % self.size]
                    edge = b2EdgeShape(vertices=[v1, v2])
                    self.body.CreateEdgeFixture(shape=edge, density=1, friction=0.0, restitution=1.2)
        if self.size <= 16:
            for i in range(self.size):
                v1 = self.vertices[i]
                v2 = self.vertices[(i + 1) % self.size]
                edge = b2EdgeShape(vertices=[v1, v2])
                self.body.CreateEdgeFixture(shape=edge, density=1, friction=0.0, restitution=1.2)

    def update(self):
        # Update the angle of the body based on the rotation speed and direction
        self.body.angle += utils.deltaTime() * self.rotateDir * 1.5  # Adjust speed multiplier as needed
        
        # Handle smooth shrinking if needed
        if self.is_shrinking and self.radius != self.target_radius:
            # Calculate the shrink amount for this frame
            shrink_amount = self.shrink_speed * utils.deltaTime() * 1.15
            
            # Make sure we don't overshoot the target radius
            if abs(self.radius - self.target_radius) <= shrink_amount:
                self.radius = self.target_radius
                self.is_shrinking = False
            else:
                # Shrink towards the target radius
                if self.radius > self.target_radius:
                    self.radius -= shrink_amount
                else:
                    self.radius += shrink_amount
            
            # Update the vertices and physics body based on new radius
            self.update_physics_body()
        
        # Update the points array for collision detection and rendering
        self.points = []
        for fixture in self.body.fixtures:
            v1 = utils.to_Pos(self.body.transform * fixture.shape.vertices[0])
            v2 = utils.to_Pos(self.body.transform * fixture.shape.vertices[1])
            self.points.append(Vector2(v1[0], v1[1]))
            self.points.append(Vector2(v2[0], v2[1]))

    def update_physics_body(self):
        # Clear existing fixtures
        for fixture in list(self.body.fixtures):
            self.body.DestroyFixture(fixture)
        
        # Recreate vertices with new radius
        self.vertices = []
        for i in range(self.size):
            angle = i * (2 * math.pi / self.size)
            x = self.radius * math.cos(angle)
            y = self.radius * math.sin(angle)
            self.vertices.append((x, y))
        
        # Recreate edge shape
        self.create_edge_shape()

    def shrink_to(self, target_radius):
        # Set the target radius to shrink to
        self.target_radius = target_radius
        self.is_shrinking = True

    def draw(self):
        self.draw_edges()

    def spawParticles(self):
        particles = []
        center = Vector2(utils.width/2, utils.height/2)
        if self.size == 90:
            for i in range(0, 360, 1):
                x = math.cos(math.radians(i)) * self.radius * 10
                y = math.sin(math.radians(i)) * self.radius * 10
                pos = center + Vector2(x, y)
                exp = Explosion(pos.x, pos.y, self.original_color)  # Use original color for particles
                particles.append(exp)
        else:
            for p in self.points:
                pos = p
                exp = Explosion(pos.x, pos.y, self.original_color)  # Use original color for particles
                particles.append(exp)
        return particles

    def draw_edges(self):
        for fixture in self.body.fixtures:
            v1 = utils.to_Pos(self.body.transform * fixture.shape.vertices[0])
            v2 = utils.to_Pos(self.body.transform * fixture.shape.vertices[1])
            
            # Draw line with the current display color (which may be blended)
            pygame.draw.line(utils.screen, self.color, v1, v2, 4)

    def is_point_in_polygon(self, point, vertices):
        # Ray-casting algorithm to check if the point is inside the polygon
        num_vertices = len(vertices)
        j = num_vertices - 1  # The last vertex is the previous one to the first
        inside = False
        for i in range(num_vertices):
            xi, yi = vertices[i]
            xj, yj = vertices[j]
            if ((yi > point.y) != (yj > point.y)) and \
                    (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside
