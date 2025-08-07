import math
import random
import pygame
from Box2D import b2TestOverlap
from pygame import Vector2
from Ball import Ball
from RingB import RingB
from particle import Explosion
from sounds import Sounds, sounds
from util import utils
import time

class Game:
    def __init__(self):
        # Existing attributes
        self.balls = []
        
        # Create "Yes" ball with green color
        self.ball_yes = Ball(Vector2(utils.width / 2 - 30, utils.height / 2 - 50), 1, (0, 255, 0), "Yes")
        # Create "No" ball with red color
        self.ball_no = Ball(Vector2(utils.width / 2 + 30, utils.height / 2 - 50), 1, (255, 0, 0), "No")
        
        # Add initial velocity to make them move in different directions
        self.ball_yes.circle_body.linearVelocity = (1, 0.5)
        self.ball_no.circle_body.linearVelocity = (-1, 0.5)
        
        # Add point counters for both balls
        self.yes_points = 0
        self.no_points = 0
        
        self.particles = []
        self.boxes = []
        self.rings = []
        
        self.paused = False  # Add paused attribute to track simulation state

        # Initialize ring generation parameters
        self.max_rings = 30  # Maximum number of rings we can have
        self.initial_rings = 25  # Start with more rings
        self.next_ring_id = self.initial_rings + 1  # Next ID for new rings
        self.largest_radius = 0  # Track the largest radius to keep adding outwards
        self.initial_smallest_radius = 1  # Track the smallest initial radius

        # Create initial rings
        radius = self.initial_smallest_radius
        numRings = self.initial_rings  # Increased from 20 to 25
        dir = 1.5
        sar = 0.5
        hue = 0.0
        hueStep = 1.0 / numRings
        sarStep = 0.1 / numRings
        for i in range(numRings):
            ring = RingB(i + 1, radius, dir, sar, hue)
            radius += 1.1
            sar += sarStep
            hue += hueStep
            dir *= 0.97
            self.rings.append(ring)
            self.largest_radius = radius  # Update largest radius

        # Store the initial radii for reference
        self.initial_ring_radii = [ring.radius for ring in self.rings]
        
        # Track the shrink factor with exponential growth
        self.base_shrink_factor = 0.90  # Base shrink factor (10% reduction)
        self.shrink_base = 1.025  # Base for exponential growth (5% increase each time)
        self.shrink_exponent = 1.025  # Exponent for more aggressive exponential growth
        self.rings_broken_count = 0     # Count of broken rings
        # Track if we need to trigger a shrink event
        self.trigger_shrink = False

        self.collide = False
        self.waitTime = 0
        self.sounds = Sounds()
        self.complete = False
        self.spawnTimeInterval = 0
        self.spawnTime = 0.5

        # Pulse effect parameters
        self.pulses = []  # List to track multiple pulses
        self.pulse_duration = 0.05  # The duration of the pulse per ring
        self.pulse_colors_yes = [(68, 122, 52), (33, 180, 43), (34, 255, 0)]  # Green pulse for Yes ball
        self.pulse_colors_no = [(122, 52, 52), (180, 43, 33), (255, 0, 0)]    # Red pulse for No ball
        self.current_pulse_colors = self.pulse_colors_yes  # Default to green

        # Countdown timer attributes
        self.timer_start = 65.0  # Start time for the countdown in seconds
        self.timer_current = self.timer_start
        
        # Track which rings are broken for collision detection
        self.broken_rings = set()  # Set to track broken ring IDs
    
    def handle_events(self):
        # Check for key press events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:  # If the "0" key is pressed
                    self.paused = not self.paused  # Toggle pause state

    def start_pulse(self, is_yes_ball=True):
        # Add a new pulse, starting at the first ring
        # Set the color based on which ball destroyed the ring
        if is_yes_ball:
            self.current_pulse_colors = self.pulse_colors_yes
        else:
            self.current_pulse_colors = self.pulse_colors_no
            
        pulse = {
            "ring_index": 0,
            "start_time": time.time(),
            "colors": self.current_pulse_colors
        }
        self.pulses.append(pulse)

    def update_pulses(self):
        if self.paused:
            return  # Skip pulse updates if paused

        current_time = time.time()

        # Iterate over each active pulse
        for pulse in self.pulses[:]:
            elapsed_time = current_time - pulse["start_time"]

            # If enough time has passed, move the pulse to the next ring
            if elapsed_time > self.pulse_duration:
                pulse["ring_index"] += 1
                pulse["start_time"] = current_time  # Reset the time for the next ring

            # If the pulse has gone through all the rings, remove it
            if pulse["ring_index"] >= len(self.rings):
                self.pulses.remove(pulse)
                # Restore original colors for all rings after pulse is complete
                for ring in self.rings:
                    # We don't need to reset because rings now have their own colors
                    pass
            else:
                # Update the colors of the rings for this pulse
                for i, ring in enumerate(self.rings):
                    if pulse["ring_index"] <= i < pulse["ring_index"] + 3 and i < len(self.rings):  # Cover 3 consecutive rings
                        # Save the original color before changing it for pulse effect
                        ring_pulse_index = i - pulse["ring_index"]
                        if 0 <= ring_pulse_index < len(pulse["colors"]):
                            ring.color = pulse["colors"][ring_pulse_index]  # Use the color sequence

    def generate_new_ring(self):
        # Always generate a new ring
        if len(self.rings) < self.max_rings:
            # Create a new ring with parameters based on the last destroyed ring
            new_radius = self.largest_radius + 1.1
            new_dir = random.uniform(0.8, 1.2)  # Random direction for variety
            new_sar = random.uniform(0.1, 0.9)
            new_hue = random.random()  # Random hue
            
            # Create the new ring
            new_ring = RingB(self.next_ring_id, new_radius, new_dir, new_sar, new_hue)
            self.rings.append(new_ring)
            
            # Update tracking variables
            self.next_ring_id += 1
            self.largest_radius = new_radius

    def update_timer(self):
        if self.paused:
            return  # Skip timer updates if paused

        # Decrease the timer by delta time (adjusted for frames per second)
        self.timer_current -= utils.deltaTime()

        # Ensure the timer doesn't go below 0
        if self.timer_current < 0:
            self.timer_current = 0

    def get_current_shrink_factor(self):
        # Calculate the current shrink factor with exponential growth
        # Formula: base_shrink_factor - (shrink_base^(rings_broken_count^shrink_exponent) - 1) * adjustment_factor
        
        if self.rings_broken_count == 0:
            return self.base_shrink_factor
        
        # Calculate exponential increment
        exponential_increment = pow(self.shrink_base, pow(self.rings_broken_count, self.shrink_exponent)) - 1
        
        # Apply a scaling factor to control the intensity
        scaling_factor = 0.01  # Adjust this to control how aggressive the exponential growth is
        
        current_factor = self.base_shrink_factor - (exponential_increment * scaling_factor)
        
        # Ensure it doesn't go below a minimum threshold (e.g., 0.3 = 70% shrink)
        return max(current_factor, 0.3)

    def shrink_all_rings(self):
        # Skip if no rings
        if len(self.rings) == 0:
            return
            
        # Get the current shrink factor
        shrink_factor = self.get_current_shrink_factor()
        
        # Shrink all rings proportionally by the current shrink factor
        for i, ring in enumerate(self.rings):
            # Calculate the new target radius
            new_radius = ring.radius * shrink_factor
            
            # Set the target radius for smooth shrinking
            ring.shrink_to(new_radius)

    def update(self):
        self.handle_events()  # Check for events before updating

        if self.paused:
            return  # Skip updates if paused

        utils.world.Step(1.0 / 60.0, 6, 2)
        utils.time += utils.deltaTime()

        if utils.contactListener:
            # Process collisions (removing handled ones for clarity)
            utils.contactListener.collisions = []
            
            # Process ring collisions that are not breaking events
            for ball, ring in list(utils.contactListener.ring_collisions):
                # Skip if this is a ring that's being broken this frame
                # or if it's already been broken
                if ring.id in self.broken_rings:
                    continue
                    
                # Check if the ring-breaking conditions are met
                if len(self.rings) > 0 and ring.id == self.rings[0].id:  # Is it the innermost ring?
                    ball_pos = ball.getPos()
                    
                    # Check if the ball is about to exit the ring's boundaries
                    # If not, it's just a touch, not a break
                    if ring.is_point_in_polygon(ball_pos, ring.points):
                        # This is just a touch, not a break - leave it to contact listener
                        pass
            
            # Clear ring collisions after processing
            utils.contactListener.clear_ring_collisions()

        # Update the countdown timer
        self.update_timer()

        # Update all active pulses
        self.update_pulses()

        # Apply ring shrinking if triggered
        if self.trigger_shrink:
            self.shrink_all_rings()
            self.trigger_shrink = False

        # Update all rings simultaneously
        for ring in self.rings:
            if not ring.destroyFlag:
                ring.update()

        # Update both balls
        self.ball_yes.update()
        self.ball_no.update()

        # Check both balls for ring destruction
        if len(self.rings) > 0:
            first_ring = self.rings[0]
            
            # Check if either ball exits the first ring's boundaries
            ball_yes_pos = self.ball_yes.getPos()
            ball_no_pos = self.ball_no.getPos()
            
            yes_broke_ring = not first_ring.is_point_in_polygon(ball_yes_pos, first_ring.points)
            no_broke_ring = not first_ring.is_point_in_polygon(ball_no_pos, first_ring.points)
            
            if yes_broke_ring or no_broke_ring:
                first_ring.destroyFlag = True
                utils.world.DestroyBody(first_ring.body)
                
                # Add the ring ID to the broken rings set
                self.broken_rings.add(first_ring.id)

                # Increment the broken rings counter
                self.rings_broken_count += 1

                # MODIFICATION: Only increment points if timer is at 60s or below
                if self.timer_current <= 60.0:
                    if yes_broke_ring:
                        self.yes_points += 1
                        # Play "Yes" sound when Yes ball breaks a ring
                        self.sounds.playYesSound()
                    if no_broke_ring:
                        self.no_points += 1
                        # Play "No" sound when No ball breaks a ring
                        self.sounds.playNoSound()

                # Trigger a new pulse when the first ring is destroyed
                # Pass which ball broke the ring
                self.start_pulse(is_yes_ball=yes_broke_ring)
                
                # Set the flag to trigger ring shrinking
                self.trigger_shrink = True
                
                # Always generate a new ring to keep the animation infinite
                self.generate_new_ring()

        # Destroy rings and spawn particles if necessary
        for ring in self.rings[:]:
            if ring.destroyFlag:
                self.particles += ring.spawParticles()
                self.rings.remove(ring)
                # Don't play the generic destroy sound here as we now play specific yes/no sounds
                # when the ring is actually broken

        # Update particles
        for exp in self.particles:
            exp.update()
            if len(exp.particles) == 0:
                self.particles.remove(exp)

    def draw_timer(self):
        # Positionner le timer à 1/3 de l'écran en hauteur
        timer_text = f"{self.timer_current:.3f}s"
        font = pygame.font.Font(None, 30)  # Taille de police réduite
        text_surface = font.render(timer_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(utils.width / 2, utils.height / 1.2))

        # Créer un fond légèrement plus grand que le texte
        padding = 8
        bg_rect = pygame.Rect(
            text_rect.left - padding,
            text_rect.top - padding,
            text_rect.width + 2 * padding,
            text_rect.height + 2 * padding,
        )
        pygame.draw.rect(utils.screen, (20, 20, 20), bg_rect)  # Fond gris foncé

        # Dessiner le texte du timer
        utils.screen.blit(text_surface, text_rect)

    def draw_points(self):
        # Positionner les compteurs plus bas (par exemple +30px)
        y_pos = utils.height / 3.35

        font = pygame.font.Font(None, 32)
        
        # MODIFICATION: Show points only if timer is at 60s or below
        if self.timer_current <= 60.0:
            yes_points_display = self.yes_points
            no_points_display = self.no_points
        else:
            yes_points_display = 0
            no_points_display = 0
        
        # Yes ball points avec fond vert
        yes_text = f"Yes:{yes_points_display}"
        yes_surface = font.render(yes_text, True, (0, 255, 0))
        yes_rect = yes_surface.get_rect(midleft=(utils.width / 2 - 90, y_pos))

        yes_bg_rect = pygame.Rect(
            yes_rect.left - 8,
            yes_rect.top - 4,
            yes_rect.width + 16,
            yes_rect.height + 8
        )
        pygame.draw.rect(utils.screen, (30, 60, 30), yes_bg_rect, border_radius=6)
        utils.screen.blit(yes_surface, yes_rect)

        # No ball points avec fond rouge
        no_text = f"No:{no_points_display}"
        no_surface = font.render(no_text, True, (255, 0, 0))
        no_rect = no_surface.get_rect(midright=(utils.width / 2 + 90, y_pos))

        no_bg_rect = pygame.Rect(
            no_rect.left - 8,
            no_rect.top - 4,
            no_rect.width + 16,
            no_rect.height + 8
        )
        pygame.draw.rect(utils.screen, (60, 30, 30), no_bg_rect, border_radius=6)
        utils.screen.blit(no_surface, no_rect)

    def draw(self):
        for ring in self.rings:
            ring.draw()
            
        # Draw both balls
        self.ball_yes.draw()
        self.ball_no.draw()

        for exp in self.particles:
            exp.draw()

        # Draw the countdown timer
        self.draw_timer()
        
        # Draw the point counters
        self.draw_points()

    def check_collision(self, ball, box):
        ballPos = utils.to_Pos(ball.circle_body.position)
        boxPos = utils.to_Pos(box.box_body.position)

        if utils.distance(ballPos[0], ballPos[1], boxPos[0], boxPos[1]) < 67:
            return True
        return False
