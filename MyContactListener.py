import Box2D
from Box2D import b2ContactListener

from sounds import sounds


class MyContactListener(b2ContactListener):
    def __init__(self):
        super(MyContactListener, self).__init__()
        self.collisions = []
        self.ring_collisions = []  # Track ring collisions specifically

    def BeginContact(self, contact):
        fixtureA = contact.fixtureA
        fixtureB = contact.fixtureB
        bodyA = fixtureA.body
        bodyB = fixtureB.body

        # Check if one of the fixtures is the circle and the other is the box
        from Ball import Ball
        from RingB import RingB
        
        # Check for collisions between balls and rings
        if (isinstance(bodyA.userData, RingB) and isinstance(bodyB.userData, Ball)) or \
           (isinstance(bodyA.userData, Ball) and isinstance(bodyB.userData, RingB)):
            
            # Add to standard collisions
            self.collisions.append((bodyA, bodyB))
            
            # Extract ball and ring objects
            ball = bodyB.userData if isinstance(bodyB.userData, Ball) else bodyA.userData
            ring = bodyA.userData if isinstance(bodyA.userData, RingB) else bodyB.userData
            
            # Add to ring collisions with information about which ball collided
            self.ring_collisions.append((ball, ring))
            
            # Play a random Gravity Fall song when the ball touches a ring
            # (this is for all collisions, we'll handle the "without breaking" logic in game.py)
            sounds.playRandomGravityFallSong()

    def EndContact(self, contact):
        pass  # Can be implemented if needed
        
    def clear_ring_collisions(self):
        """Clear the ring collisions list"""
        self.ring_collisions = []