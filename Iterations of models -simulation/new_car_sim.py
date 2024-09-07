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
GREY2 = (100, 100, 100)
YELLOW = (255, 255, 0)
GREEN = (100,150,100)
SIGNAL_GREEN = (50,200,50)
ROAD_COLOR = (100,100,100)

BLOCK_SIZE = 20
SPEED = 20

class ScreenProperties:
    def __init__(self, width, height, color, title):
        self.width = width
        self.height = height
        self.color = color
        self.title = title
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

    def fill(self):
        self.screen.fill(self.color)

class Intersection:
    def __init__(self, screen_properties):
        self.screen = screen_properties.screen
        self.lanes = self.initialize_lanes()
        self.guide_lines_width = 7

    def initialize_lanes(self):
        # Define the lanes with specific coordinates
        lanes = {
            'input_north': pygame.Rect(720, 0, 100, 350),
            'guide_north': pygame.Rect(715, 0, 7, 320),
            'output_north': pygame.Rect(620, 0, 100, 350),
            'input_south': pygame.Rect(620, 550, 100, 350),
            'guide_south': pygame.Rect(715, 590, 7, 350),
            'output_south': pygame.Rect(720, 550, 100, 350),
            'input_east': pygame.Rect(820, 450, 620, 100),
            'guide_east': pygame.Rect(860, 445, 600, 7),
            'output_east': pygame.Rect(820, 350, 620, 100),
            'input_west': pygame.Rect(0, 350, 620, 100),
            'guide_west': pygame.Rect(0, 445, 580, 7),
            'output_west': pygame.Rect(0, 450, 620, 100),
            'intersection': pygame.Rect(620, 350, 200, 200)
        }
        return lanes

    def draw(self):
        # Draw the lanes
        # North Lanes
        pygame.draw.rect(self.screen, ROAD_COLOR, self.lanes['input_north'])
        pygame.draw.rect(self.screen, GREY, self.lanes['output_north'])
        pygame.draw.rect(self.screen, WHITE, self.lanes['guide_north'])
        
        # South Lanes
        pygame.draw.rect(self.screen, ROAD_COLOR, self.lanes['input_south'])
        pygame.draw.rect(self.screen, GREY, self.lanes['output_south'])
        pygame.draw.rect(self.screen, WHITE, self.lanes['guide_south'])
        
        # East Lanes
        pygame.draw.rect(self.screen, ROAD_COLOR, self.lanes['input_east'])
        pygame.draw.rect(self.screen, GREY, self.lanes['output_east'])
        pygame.draw.rect(self.screen, WHITE, self.lanes['guide_east'])
        
        # West Lanes
        pygame.draw.rect(self.screen, ROAD_COLOR, self.lanes['input_west'])
        pygame.draw.rect(self.screen, GREY, self.lanes['output_west'])
        pygame.draw.rect(self.screen, WHITE, self.lanes['guide_west'])

        # Draw the intersection
        pygame.draw.rect(self.screen, GREY2, self.lanes['intersection'])
        
        #Draw Intersection White line
        pygame.draw.aalines(self.screen,BLACK, True, [(620, 350), (820, 350), (820, 550), (620, 550)])
        ### Use above line to detect how many car passed the intersection ###

class Signal:
    def __init__(self, screen, position, size, name):
        self.screen = screen
        self.position = position
        self.size = size
        self.name = name
        self.color = RED
        self.colors = [RED, YELLOW, SIGNAL_GREEN]
        self.color_index = 0
        self.image = pygame.Surface(size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=position)

    def draw(self):
        self.image.fill(self.color)
        self.screen.blit(self.image, self.position)

    def handle_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.color_index = (self.color_index + 1) % len(self.colors)
            self.color = self.colors[self.color_index]

class Car(pygame.sprite.Sprite):
    def __init__(self, image, position, direction):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=position)
        self.direction = direction

    def move(self):
        if self.direction == Direction.RIGHT:
            self.rect.x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            self.rect.x -= BLOCK_SIZE
        elif self.direction == Direction.UP:
            self.rect.y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            self.rect.y += BLOCK_SIZE
            
class CarGame:
    def __init__(self, w=1440, h=900):
        self.w = w
        self.h = h
        self.screen_properties = ScreenProperties(self.w, self.h, GREEN, 'Traffic Simulation')
        self.intersection = Intersection(self.screen_properties)
        self.clock = pygame.time.Clock()
        
        # load car image
        self.car_image = pygame.image.load('car1.png')
        self.car_image = pygame.transform.scale(self.car_image, (50, 50))
        
        # init game state
        self.cars = pygame.sprite.Group()
        self.spawn_time = time.time()

        
        # Initialize signals
        self.signals = [
            Signal(self.screen_properties.screen, (600, 350), (20, 100), 'Signal_West'),  # Signal West
            Signal(self.screen_properties.screen, (820, 450), (20, 100), 'Signal_East'),  # Signal East
            Signal(self.screen_properties.screen, (720, 330), (100, 20), 'Signal_North'),  # Signal North
            Signal(self.screen_properties.screen, (620, 550), (100, 20), 'Signal_South')  # Signal South
        ]
        
    def _spawn_car(self):
        lane_coordinates = {
            Direction.LEFT: Point(1440, 475),
            Direction.RIGHT: Point(0, 375),
            Direction.DOWN: Point(745, 0),
            Direction.UP: Point(645, 900)
        }
        
        lane = random.choice(list(lane_coordinates.keys()))
        car = Car(self.car_image, lane_coordinates[lane], lane)
        self.cars.add(car)
        print(f"Spawned car at {car.rect.topleft} going {car.direction}")
        
    def play_step(self):
      # 1. collect user input    
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for signal in self.signals:
                signal.handle_click(mouse_pos)
    
      # Spawn new car every 1 second
      if time.time() - self.spawn_time > 1:
        self._spawn_car()
        self.spawn_time = time.time()
    
      # 2. move
      for car in self.cars:
        self._check_signal(car)  # Check signal before moving
        self._move(car)
           
      # 3. check if game over
      for car in self.cars:
        if self._is_collision(car):
            self.cars.remove(car)
    
      # 4. update ui and clock
      self._update_ui()
      self.clock.tick(SPEED)
        
    # def _is_collision(self, car):
    #     x, y = car[0].x, car[0].y
    #     if x < 0 or x > self.w or y < 0 or y > self.h:
    #         return True
    #     return False
    def _is_collision(self, car):
        return car.rect.collidelist([signal.rect for signal in self.signals]) != -1
        
    def _update_ui(self):
        self.screen_properties.fill()
        self.intersection.draw()
        self.cars.draw(self.screen_properties.screen)
        for signal in self.signals:
            signal.draw()
        pygame.display.flip()
        
    def _move(self, car):
      # Check if the car is near a signal
      if self._is_near_signal(car):
        # Check if the signal is green
        if self._check_signal(car):
            car.move()
      else:
        car.move()
        
        # Change direction at the intersection
        # center_x, center_y = self.w // 2, self.h // 2
        # if ((center_x - 30 < car[0].x < center_x + 30) and (center_y - 30 < car[0].y < center_y + 30)):
        #     output_routes = {
        #         Direction.RIGHT: Point(790, 375), #820-30=790
        #         Direction.LEFT: Point(650, 475), #620+30=650
        #         Direction.UP: Point(645, 380),  #350+30 = 380
        #         Direction.DOWN: Point(745, 520) #550-30=520
        #     }
        #     new_direction = random.choice(list(output_routes.keys()))
        #     car[0] = output_routes[new_direction]
        #     car[1] = new_direction
        
        # Move towards the target position if set
        # if car[2] is not None:
        #     target_x, target_y = car[2].x, car[2].y
        #     dx = target_x - car[0].x
        #     dy = target_y - car[0].y
        #     distance = (dx**2 + dy**2)**0.5
        #     if distance > 0:
        #         step_x = BLOCK_SIZE * (dx / distance)
        #         step_y = BLOCK_SIZE * (dy / distance)
        #         car[0] = Point(car[0].x + step_x, car[0].y + step_y)
        #         if abs(dx) < BLOCK_SIZE and abs(dy) < BLOCK_SIZE:
        #             car[0] = car[2]  # Snap to target position
        #             car[2] = None  # Clear target position
        
      #  # Check if the signal is green and clear the target position
      #   self._check_signal(car)
      #   if car[2] is not None:
      #     direction = car[1]
      #     if direction == Direction.RIGHT:
      #       signal = next((s for s in self.signals if s.name == 'Signal_West'), None)
      #     elif direction == Direction.LEFT:
      #       signal = next((s for s in self.signals if s.name == 'Signal_East'), None)
      #     elif direction == Direction.UP:
      #       signal = next((s for s in self.signals if s.name == 'Signal_South'), None)
      #     elif direction == Direction.DOWN:
      #       signal = next((s for s in self.signals if s.name == 'Signal_North'), None)
        
      #     if signal and signal.color == GREEN:
      #       car[2] = None  # Clear target position to resume movement
    def _is_near_signal(self, car):
      direction = car.direction
      if direction == Direction.RIGHT:
        return car.rect.x + car.rect.width >= 600 and car.rect.x <= 620
      elif direction == Direction.LEFT:
        return car.rect.x <= 820 and car.rect.x + car.rect.width >= 800
      elif direction == Direction.UP:
        return car.rect.y <= 550 and car.rect.y + car.rect.height >= 530
      elif direction == Direction.DOWN:
        return car.rect.y + car.rect.height >= 350 and car.rect.y <= 370
      return False
          
    def _check_signal(self, car):
      direction = car.direction
      if direction == Direction.RIGHT:
        signal = next((s for s in self.signals if s.name == 'Signal_West'), None)
      elif direction == Direction.LEFT:
        signal = next((s for s in self.signals if s.name == 'Signal_East'), None)
      elif direction == Direction.UP:
        signal = next((s for s in self.signals if s.name == 'Signal_South'), None)
      elif direction == Direction.DOWN:
        signal = next((s for s in self.signals if s.name == 'Signal_North'), None)
    
      return signal and signal.color == SIGNAL_GREEN

class carMove():
  # Initalize cars
  # spawn car evry 1 second
  # move car from one lane to other using randome choices
  # Kill car when left the screen
  # Follow red signal logic
  # Integrate all the above to make smooth
  pass

if __name__ == '__main__':
    game = CarGame()
    
    # game loop
    running = True
    while running:
        game.play_step()
        
    pygame.quit()


