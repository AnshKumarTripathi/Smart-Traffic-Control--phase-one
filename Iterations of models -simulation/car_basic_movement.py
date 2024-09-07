import pygame
import random
from enum import Enum
from collections import namedtuple
import time

pygame.init()
font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)

BLOCK_SIZE = 20
SPEED = 20

class CarGame:
    
    def __init__(self, w=1440, h=900):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Traffic')
        self.clock = pygame.time.Clock()
        
        # load car image
        self.car_image = pygame.image.load('car1.png')
        self.car_image = pygame.transform.scale(self.car_image, (50, 50))
        
        # load arrow images
        self.right_arrow = pygame.image.load('Right_pointing_arrow.png')
        self.left_arrow = pygame.image.load('Left_pointing_arrow.png')
        self.up_arrow = pygame.image.load('Up_pointing_arrow.png')
        self.down_arrow = pygame.image.load('Down_pointing_arrow.png')
        
        # scale arrow images
        self.right_arrow = pygame.transform.scale(self.right_arrow, (50, 50))
        self.left_arrow = pygame.transform.scale(self.left_arrow, (50, 50))
        self.up_arrow = pygame.transform.scale(self.up_arrow, (50, 50))
        self.down_arrow = pygame.transform.scale(self.down_arrow, (50, 50))
        
        # init game state
        self.cars = []
        self.spawn_time = time.time()
        
    def _spawn_car(self):
        lane = random.choice([Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN])
        if lane == Direction.RIGHT:
            return [Point(0, self.h // 2 - 60), Direction.RIGHT]
        elif lane == Direction.LEFT:
            return [Point(self.w, self.h // 2 + 40), Direction.LEFT]
        elif lane == Direction.UP:
            return [Point(self.w // 2 - 60, self.h), Direction.UP]
        elif lane == Direction.DOWN:
            return [Point(self.w // 2 + 40, 0), Direction.DOWN]
        
    def play_step(self):
        # 1. collect user input    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # Spawn new car every 1 second
        if time.time() - self.spawn_time > 1:
            self.cars.append(self._spawn_car())
            self.spawn_time = time.time()
        
        # 2. move
        for car in self.cars:
            self._move(car)
               
        # 3. check if game over
        self.cars = [car for car in self.cars if not self._is_collision(car)]
        
        # 4. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        
    def _is_collision(self, car):
        x, y = car[0].x, car[0].y
        if x < 0 or x > self.w or y < 0 or y > self.h:
            return True
        return False
        
    def _update_ui(self):
        self.display.fill(WHITE)
        self._draw_intersection()
        for car in self.cars:
            self.display.blit(self.car_image, (car[0].x, car[0].y))
        pygame.display.flip()
        
    def _draw_intersection(self):
        road_width = 200
        center_x, center_y = self.w // 2, self.h // 2
        
        # Draw horizontal road
        pygame.draw.rect(self.display, GREY, (0, center_y - road_width // 2, self.w, road_width))
        
        # Draw vertical road
        pygame.draw.rect(self.display, GREY, (center_x - road_width // 2, 0, road_width, self.h))
        
        # Draw yellow lines for lanes
        pygame.draw.line(self.display, YELLOW, (0, center_y), (center_x - road_width // 2, center_y), 5)
        pygame.draw.line(self.display, YELLOW, (center_x + road_width // 2, center_y), (self.w, center_y), 5)
        pygame.draw.line(self.display, YELLOW, (center_x, 0), (center_x, center_y - road_width // 2), 5)
        pygame.draw.line(self.display, YELLOW, (center_x, center_y + road_width // 2), (center_x, self.h), 5)
        
        # Draw arrow images
        self.display.blit(self.right_arrow, (self.w // 2 - 200, self.h // 2 - 70))
        self.display.blit(self.left_arrow, (self.w // 2 + 150, self.h // 2 + 30))
        self.display.blit(self.up_arrow, (self.w // 2 - 70, self.h // 2 + 150))
        self.display.blit(self.down_arrow, (self.w // 2 + 30, self.h // 2 - 200))
        
    def _move(self, car):
        direction = car[1]
        if direction == Direction.RIGHT:
            car[0] = Point(car[0].x + BLOCK_SIZE, car[0].y)
        elif direction == Direction.LEFT:
            car[0] = Point(car[0].x - BLOCK_SIZE, car[0].y)
        elif direction == Direction.UP:
            car[0] = Point(car[0].x, car[0].y - BLOCK_SIZE)
        elif direction == Direction.DOWN:
            car[0] = Point(car[0].x, car[0].y + BLOCK_SIZE)
        
        # Change direction at the intersection
        center_x, center_y = self.w // 2, self.h // 2
        if (center_x - 50 < car[0].x < center_x + 50) and (center_y - 50 < car[0].y < center_y + 50):
            new_direction = random.choice([d for d in Direction if d != direction])
            car[1] = new_direction
            

if __name__ == '__main__':
    game = CarGame()
    
    # game loop
    running = True
    while running:
        game.play_step()
        
    pygame.quit()
