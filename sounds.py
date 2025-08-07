from pygame import mixer
import pygame
import random
import os

class Sounds:
    def __init__(self):
        mixer.init()

        # General destroy sound (legacy)
        self.destroySound = pygame.mixer.Sound("assets/none.wav")
        
        # New sounds for yes/no balls
        self.yes_sound = pygame.mixer.Sound("assets/YES.wav")
        self.no_sound = pygame.mixer.Sound("assets/NO.wav")
        
        # Load all Gravity Falls songs for touch events
        self.gravity_fall_songs = []
        
        # First try to load the base file
        base_file = "assets/gravity fall.wav"
        if os.path.exists(base_file):
            self.gravity_fall_songs.append(pygame.mixer.Sound(base_file))
        
        # Then try to load numbered files (1-15)
        for i in range(2, 16):  # Start from 2 since "gravity fall.wav" is already loaded
            # Try both formats of the filename
            file_patterns = [
                f"assets/gravity fall ({i}).wav",  # Format: "gravity fall (2).wav"
                f"assets/gravity fall{i}.wav"      # Format: "gravity fall2.wav"
            ]
            
            for file_path in file_patterns:
                if os.path.exists(file_path):
                    self.gravity_fall_songs.append(pygame.mixer.Sound(file_path))
                    break  # Found a valid file for this number, move to next
        
        # Print status message
        print(f"Loaded {len(self.gravity_fall_songs)} gravity fall songs")
                
        # If no gravity fall songs were found, add a placeholder
        if not self.gravity_fall_songs:
            print("Warning: No gravity fall songs found. Using placeholder.")
            self.gravity_fall_songs = [self.destroySound]

        # Extract note segments
        self.segments = [
            pygame.mixer.Sound("assets/none.wav"),
        ]
        self.i = 0
        
        # Track currently playing song to avoid overlap
        self.current_playing_song = None

    def play(self):
        for s in self.segments:
            s.stop()
        sound = self.segments[self.i]
        sound.play()
        self.i += 1
        if self.i >= len(self.segments):
            self.i = 0

    def playDestroySound(self):
        self.destroySound.play()
        
    def playYesSound(self):
        """Play sound when Yes ball breaks a ring"""
        self.yes_sound.play()
        
    def playNoSound(self):
        """Play sound when No ball breaks a ring"""
        self.no_sound.play()
        
    def playRandomGravityFallSong(self):
        """Play a random Gravity Fall song when a ball touches a ring without breaking"""
        # Stop currently playing song if there is one
        if self.current_playing_song:
            self.current_playing_song.stop()
            
        # Pick a random song from the collection
        if self.gravity_fall_songs:
            self.current_playing_song = random.choice(self.gravity_fall_songs)
            self.current_playing_song.play()


sounds = Sounds()