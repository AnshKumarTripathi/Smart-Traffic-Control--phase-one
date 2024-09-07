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
YELLOW = (255, 255, 0)
GREEN = (0, 100, 0)
BLACK = (0,0,0)
GREY = (128, 128, 128)
ROAD_COLOR = (50, 50, 50)

BLOCK_SIZE = 50
SPEED = 20
STOPPING_DISTANCE = 25
OFFSET = 50  # Define the offset distance


class Signal:
    def __init__(self, screen, position, size, name):
        self.screen = screen
        self.position = position
        self.size = size
        self.name = name
        self.color = '---'  # Default value indicating the simulation hasn't started
        self.colors = [RED, YELLOW, GREEN]
        self.color_index = 0
        self.timers = [180, 5, 30]  # Timers for RED, YELLOW, GREEN
        self.counter = self.timers[self.color_index]
        self.running = False
        self.last_update_time = time.time()

    def draw(self):
        pygame.draw.rect(self.screen, self.color if self.color != '---' else BLACK, (*self.position, *self.size))
        if self.color != '---':
            font = pygame.font.SysFont('arial', 25)
            text = font.render(str(self.counter), True, WHITE)
            self.screen.blit(text, (self.position[0] + 5, self.position[1] + 5))

    def handle_click(self, mouse_pos):
        mouse_rect = pygame.Rect(mouse_pos[0], mouse_pos[1], 1, 1)  # Convert mouse_pos to a Rect
        rect = pygame.Rect(*self.position, *self.size)
        if rect.colliderect(mouse_rect):
            self.color_index = (self.color_index + 1) % len(self.colors)
            self.color = self.colors[self.color_index]
            self.counter = self.timers[self.color_index]

    def update(self):
        if self.running and self.color != '---':
            current_time = time.time()
            if current_time - self.last_update_time >= 1:  # Update every second
                self.counter -= 1
                self.last_update_time = current_time
                if self.counter <= 0:
                    self.color_index = (self.color_index + 1) % len(self.colors)
                    self.color = self.colors[self.color_index]
                    self.counter = self.timers[self.color_index]

    def start(self):
        self.running = True
        self.color = RED
        self.counter = self.timers[0]
        self.last_update_time = time.time()

class Button:
    def __init__(self, screen, position, size, text):
        self.screen = screen
        self.position = position
        self.size = size
        self.text = text
        self.rect = pygame.Rect(*self.position, *self.size)
        self.font = pygame.font.SysFont('arial', 25)

    def draw(self):
        pygame.draw.rect(self.screen, GREY, self.rect)
        text_surf = self.font.render(self.text, True, WHITE)
        self.screen.blit(text_surf, (self.position[0] + 10, self.position[1] + 10))

    def handle_click(self, mouse_pos):
        mouse_rect = pygame.Rect(mouse_pos[0], mouse_pos[1], 1, 1)  # Convert mouse_pos to a Rect
        if self.rect.colliderect(mouse_rect):
            return True
        return False
 
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
        pygame.draw.rect(self.screen, GREY, self.lanes['intersection'])
        
        # Draw Intersection White line
        pygame.draw.aalines(self.screen, BLACK, True, [(620, 350), (820, 350), (820, 550), (620, 550)])

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

class CarGame:
    
    def __init__(self, w=1440, h=900):
        self.w = w
        self.h = h
        self.screen_properties = ScreenProperties(self.w, self.h, GREEN, 'Traffic Simulation')
        self.intersection = Intersection(self.screen_properties)
        self.clock = pygame.time.Clock()
        
        # load car image
        # self.car_image = pygame.image.load('car1.png')
        # self.car_image = pygame.transform.scale(self.car_image, (50, 50))
        
        # init game state
        self.cars = []
        self.spawn_time = time.time()
        
        # Initialize signals
        self.signals = [
            Signal(self.screen_properties.screen, (620, 350), (20, 100), 'Signal_West'),  # Signal West
            Signal(self.screen_properties.screen, (820, 450), (20, 100), 'Signal_East'),  # Signal East
            Signal(self.screen_properties.screen, (720, 350), (100, 20), 'Signal_North'),  # Signal North
            Signal(self.screen_properties.screen, (620, 550), (100, 20), 'Signal_South')  # Signal South
        ]
        
        # Initialize start button
        self.start_button = Button(self.screen_properties.screen, (self.w - 150, 50), (100, 50), 'Start')
        self.simulation_started = False
        
        # Initialize car counter
        self.car_counter = 0
        
    def _spawn_car(self):
        lane_coordinates = {
            Direction.LEFT: Point(1440, 475),
            Direction.RIGHT: Point(0, 375),
            Direction.DOWN: Point(745, 0),
            Direction.UP: Point(645, 900)
        }
        
        lane = random.choice(list(lane_coordinates.keys()))
        car = [lane_coordinates[lane], lane, SPEED]  # Add speed attribute
        # print(f"Spawned car at {car[0]} going {car[1]}")
        return car
    
    # def _check_signal_collision(self, car):
    #     for signal in self.signals:
    #         signal_rect = pygame.Rect(*signal.position, *signal.size)
    #         car_rect = pygame.Rect(car[0].x, car[0].y, BLOCK_SIZE, BLOCK_SIZE)
    #         if signal_rect.colliderect(car_rect):
    #             if signal.color in [RED, YELLOW]:
    #                 car[2] = 0  # Stop the car
    #             # else:
    #             #     car[2] = SPEED  # Restore the car's speed
    #             elif signal.color == GREEN:
    #                 car[2] = SPEED  # Restore the car's speed
            
                    
    def _check_signal_collision(self, car):
        for signal in self.signals:
            signal_rect = pygame.Rect(*signal.position, *signal.size)
            car_rect = pygame.Rect(car[0].x, car[0].y, BLOCK_SIZE, BLOCK_SIZE)
            if signal_rect.colliderect(car_rect):
                if signal.color in [RED, YELLOW]:
                    car[2] = 0  # Stop the car
                    # Adjust car position to stop just before the signal
                    if car[1] == Direction.RIGHT:
                        car[0] = Point(signal_rect.left - BLOCK_SIZE, car[0].y)
                    elif car[1] == Direction.LEFT:
                        car[0] = Point(signal_rect.right, car[0].y)
                    elif car[1] == Direction.UP:
                        car[0] = Point(car[0].x, signal_rect.bottom)
                    elif car[1] == Direction.DOWN:
                        car[0] = Point(car[0].x, signal_rect.top - BLOCK_SIZE)
                elif signal.color == GREEN:
                    car[2] = SPEED  # Restore the car's speed
            else:
                car[2] = SPEED  # Ensure the car's speed is restored if it's not colliding with any signal
                    
    # def _check_car_collision(self):
    #     for i, car1 in enumerate(self.cars):
    #         for j, car2 in enumerate(self.cars):
    #             if i != j:
    #                 car1_rect = pygame.Rect(car1[0].x, car1[0].y, BLOCK_SIZE, BLOCK_SIZE)
    #                 car2_rect = pygame.Rect(car2[0].x, car2[0].y, BLOCK_SIZE, BLOCK_SIZE)
    #                 if car1_rect.colliderect(car2_rect):
    #                     if car1[2] == 0:  # If car1 is stopped
    #                         car2[2] = 0  # Stop car2
    
    # OFFSET = 10  # Define the offset distance

    # def _check_car_collision(self):
    #     for i, car1 in enumerate(self.cars):
    #         for j, car2 in enumerate(self.cars):
    #             if i != j:
    #                 car1_rect = pygame.Rect(car1[0].x, car1[0].y, BLOCK_SIZE, BLOCK_SIZE)
    #                 car2_rect = pygame.Rect(car2[0].x, car2[0].y, BLOCK_SIZE, BLOCK_SIZE)
    #                 if car1_rect.colliderect(car2_rect):
    #                     if car1[2] == 0:  # If car1 is stopped
    #                         car2[2] = 0  # Stop car2
    #                         # Adjust car2 position to stop with an offset from car1
    #                         if car2[1] == Direction.RIGHT:
    #                             car2[0] = Point(car1[0].x - BLOCK_SIZE - OFFSET, car2[0].y)
    #                         elif car2[1] == Direction.LEFT:
    #                             car2[0] = Point(car1[0].x + BLOCK_SIZE + OFFSET, car2[0].y)
    #                         elif car2[1] == Direction.UP:
    #                             car2[0] = Point(car2[0].x, car1[0].y + BLOCK_SIZE + OFFSET)
    #                         elif car2[1] == Direction.DOWN:
    #                             car2[0] = Point(car2[0].x, car1[0].y - BLOCK_SIZE - OFFSET)
    def _check_car_collision(self):
      for i, car1 in enumerate(self.cars):
        for j, car2 in enumerate(self.cars):
            if i != j:
                car1_rect = pygame.Rect(car1[0].x, car1[0].y, BLOCK_SIZE, BLOCK_SIZE)
                car2_rect = pygame.Rect(car2[0].x, car2[0].y, BLOCK_SIZE, BLOCK_SIZE)
                if car1_rect.colliderect(car2_rect):
                    if car1[2] == 0:  # If car1 is stopped
                        car2[2] = 0  # Stop car2
                        # Adjust car2 position to stop with an offset from car1
                        if car2[1] == Direction.RIGHT:
                            car2[0] = Point(car1[0].x - BLOCK_SIZE - OFFSET, car2[0].y)
                        elif car2[1] == Direction.LEFT:
                            car2[0] = Point(car1[0].x + BLOCK_SIZE + OFFSET, car2[0].y)
                        elif car2[1] == Direction.UP:
                            car2[0] = Point(car2[0].x, car1[0].y + BLOCK_SIZE + OFFSET)
                        elif car2[1] == Direction.DOWN:
                            car2[0] = Point(car2[0].x, car1[0].y - BLOCK_SIZE - OFFSET)
                else:
                    # Ensure the car maintains the offset if it's not colliding
                    if car1[2] == 0:  # If car1 is stopped
                        if car2[1] == Direction.RIGHT and car2[0].x > car1[0].x - BLOCK_SIZE - OFFSET:
                            car2[2] = 0  # Stop car2
                            car2[0] = Point(car1[0].x - BLOCK_SIZE - OFFSET, car2[0].y)
                        elif car2[1] == Direction.LEFT and car2[0].x < car1[0].x + BLOCK_SIZE + OFFSET:
                            car2[2] = 0  # Stop car2
                            car2[0] = Point(car1[0].x + BLOCK_SIZE + OFFSET, car2[0].y)
                        elif car2[1] == Direction.UP and car2[0].y < car1[0].y + BLOCK_SIZE + OFFSET:
                            car2[2] = 0  # Stop car2
                            car2[0] = Point(car2[0].x, car1[0].y + BLOCK_SIZE + OFFSET)
                        elif car2[1] == Direction.DOWN and car2[0].y > car1[0].y - BLOCK_SIZE - OFFSET:
                            car2[2] = 0  # Stop car2
                            car2[0] = Point(car2[0].x, car1[0].y - BLOCK_SIZE - OFFSET)

    # def _check_car_distance(self):
    #   for i, car1 in enumerate(self.cars):
    #     for j, car2 in enumerate(self.cars):
    #         if i != j:
    #             car1_rect = pygame.Rect(car1[0].x, car1[0].y, BLOCK_SIZE, BLOCK_SIZE)
    #             car2_rect = pygame.Rect(car2[0].x, car2[0].y, BLOCK_SIZE, BLOCK_SIZE)
    #             if car1_rect.colliderect(car2_rect):
    #                 if car1[2] == 0:  # If car1 is stopped
    #                     car2[2] = 0  # Stop car2
    #                     # Adjust car2 position to stop with an offset from car1
    #                     if car2[1] == Direction.RIGHT:
    #                         car2[0] = Point(car1[0].x - BLOCK_SIZE - OFFSET, car2[0].y)
    #                     elif car2[1] == Direction.LEFT:
    #                         car2[0] = Point(car1[0].x + BLOCK_SIZE + OFFSET, car2[0].y)
    #                     elif car2[1] == Direction.UP:
    #                         car2[0] = Point(car2[0].x, car1[0].y + BLOCK_SIZE + OFFSET)
    #                     elif car2[1] == Direction.DOWN:
    #                         car2[0] = Point(car2[0].x, car1[0].y - BLOCK_SIZE - OFFSET)
    #             else:
    #                 # Ensure the car maintains the offset if it's not colliding
    #                 if car1[2] == 0:  # If car1 is stopped
    #                     if car2[1] == Direction.RIGHT and car2[0].x > car1[0].x - BLOCK_SIZE - OFFSET:
    #                         car2[2] = 0  # Stop car2
    #                         car2[0] = Point(car1[0].x - BLOCK_SIZE - OFFSET, car2[0].y)
    #                     elif car2[1] == Direction.LEFT and car2[0].x < car1[0].x + BLOCK_SIZE + OFFSET:
    #                         car2[2] = 0  # Stop car2
    #                         car2[0] = Point(car1[0].x + BLOCK_SIZE + OFFSET, car2[0].y)
    #                     elif car2[1] == Direction.UP and car2[0].y < car1[0].y + BLOCK_SIZE + OFFSET:
    #                         car2[2] = 0  # Stop car2
    #                         car2[0] = Point(car2[0].x, car1[0].y + BLOCK_SIZE + OFFSET)
    #                     elif car2[1] == Direction.DOWN and car2[0].y > car1[0].y - BLOCK_SIZE - OFFSET:
    #                         car2[2] = 0  # Stop car2
    #                         car2[0] = Point(car2[0].x, car1[0].y - BLOCK_SIZE - OFFSET)
                            
    def play_step(self):
        # 1. collect user input    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.start_button.handle_click(mouse_pos):
                    self.simulation_started = True
                    for signal in self.signals:
                        signal.start()
                for signal in self.signals:
                    signal.handle_click(mouse_pos)
        
        if self.simulation_started:
            # Spawn new car every 1 second
            if time.time() - self.spawn_time > 2:
                self.cars.append(self._spawn_car())
                self.spawn_time = time.time()
            
            # 2. move
            for car in self.cars:
                self._check_signal_collision(car)
                self._move(car)
            
            self._check_car_collision()
            
            # Update signals
            for signal in self.signals:
                signal.update()
        
        # 3. check if game over
        self.cars = [car for car in self.cars if not self._is_collision(car)]
        
        # 4. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        
    def _update_ui(self):
        self.screen_properties.fill()
        self.intersection.draw()
        for car in self.cars:
            # print(f"Drawing car at {car[0]}")
            pygame.draw.rect(self.screen_properties.screen, RED, (car[0].x, car[0].y, BLOCK_SIZE, BLOCK_SIZE))
        for signal in self.signals:
            signal.draw()
        self.start_button.draw()
        
        # Display car counter
        # font = pygame.font.SysFont('arial', 25)
        # counter_text = font.render(f"Cars Passed: {self.car_counter}", True, BLACK)
        # self.screen_properties.screen.blit(counter_text, (self.w - 200, 100))
        print(f"Cars Passed: {self.car_counter}")
        
        pygame.display.flip()
    
    def _is_collision(self, car):
      x, y = car[0].x, car[0].y
      if x < 0 or x > self.w or y < 0 or y > self.h:
        return True
      return False
        
    # def _move(self, car):
    #     direction = car[1]
    #     if car[2] == 0:  # If speed is zero, the car is stopped
    #         return
        
    #     if direction == Direction.RIGHT:
    #         car[0] = Point(car[0].x + car[2], car[0].y)
    #     elif direction == Direction.LEFT:
    #         car[0] = Point(car[0].x - car[2], car[0].y)
    #     elif direction == Direction.UP:
    #         car[0] = Point(car[0].x, car[0].y - car[2])
    #     elif direction == Direction.DOWN:
    #         car[0] = Point(car[0].x, car[0].y + car[2])
        
    #     # Change direction at the intersection
    #     center_x, center_y = self.w // 2, self.h // 2
    #     if ((center_x - 30 < car[0].x < center_x + 30) and (center_y - 30 < car[0].y < center_y + 30)):
    #         output_routes = {
    #             Direction.RIGHT: Point(820, car[0].y),  # Move to the right output lane
    #             Direction.LEFT: Point(620, car[0].y),   # Move to the left output lane
    #             Direction.UP: Point(car[0].x, 350),     # Move to the top output lane
    #             Direction.DOWN: Point(car[0].x, 550)    # Move to the bottom output lane
    #         }
    #         new_direction = random.choice(list(output_routes.keys()))
    #         car[0] = output_routes[new_direction]
    #         car[1] = new_direction
    #         self.car_counter += 1  # Increment the car counter
    def _move(self, car):
      direction = car[1]
      if car[2] == 0:  # If speed is zero, the car is stopped
        return
    
      if direction == Direction.RIGHT:
        car[0] = Point(car[0].x + car[2], car[0].y)
      elif direction == Direction.LEFT:
        car[0] = Point(car[0].x - car[2], car[0].y)
      elif direction == Direction.UP:
        car[0] = Point(car[0].x, car[0].y - car[2])
      elif direction == Direction.DOWN:
        car[0] = Point(car[0].x, car[0].y + car[2])
    
      # Change direction at the intersection
      center_x, center_y = self.w // 2, self.h // 2
      intersection_rect = pygame.Rect(center_x - 30, center_y - 30, 60, 60)
      car_rect = pygame.Rect(car[0].x, car[0].y, BLOCK_SIZE, BLOCK_SIZE)
    
      if intersection_rect.colliderect(car_rect):
        output_routes = {
            Direction.RIGHT: Point(790, 375), #820-30=790
            Direction.LEFT: Point(650, 475), #620+30=650
            Direction.UP: Point(645, 380),  #350+30 = 380
            Direction.DOWN: Point(745, 520) #550-30=520
        }
        new_direction = random.choice(list(output_routes.keys()))
        car[0] = output_routes[new_direction]
        car[1] = new_direction
        self.car_counter += 1  # Increment the car counter
   
        

if __name__ == '__main__':
    game = CarGame()
    
    # game loop
    running = True
    while running:
        game.play_step()
        
    pygame.quit()
