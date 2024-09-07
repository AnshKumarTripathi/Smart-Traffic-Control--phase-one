import pygame
import random
from enum import Enum
from collections import namedtuple
import time
import joblib
import os
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

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
L_GREEN = (124, 185, 100)
BLACK = (0,0,0)
GREY = (128, 128, 128)
ROAD_COLOR = (50, 50, 50)

BLOCK_SIZE = 20
SPEED = 20
STOPPING_DISTANCE = 25
OFFSET = 50  # Define the offset distance

class Signal:
    def __init__(self, screen, position, size, name):
        self.screen = screen
        self.position = position
        self.size = size
        self.name = name
        self.color = RED
        self.colors = [RED, YELLOW, GREEN]
        self.color_index = 0
        self.green_light_duration = 0  # Initialize green light duration

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (*self.position, *self.size))

    def handle_click(self, mouse_pos):
        rect = pygame.Rect(*self.position, *self.size)
        if rect.collidepoint(mouse_pos):
            self.color_index = (self.color_index + 1) % len(self.colors)
            self.color = self.colors[self.color_index]

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

class Button:
    def __init__(self, screen, position, size, text):
        self.screen = screen
        self.position = position
        self.size = size
        self.text = text
        self.color = GREY
        self.font = pygame.font.SysFont('arial', 25)
        
    def draw(self):
        pygame.draw.rect(self.screen, self.color, (*self.position, *self.size))
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=(self.position[0] + self.size[0] // 2, self.position[1] + self.size[1] // 2))
        self.screen.blit(text_surface, text_rect)
        
    def handle_click(self, mouse_pos):
        rect = pygame.Rect(*self.position, *self.size)
        if rect.collidepoint(mouse_pos):
            return True
        return False

class CarGame:
    
    def __init__(self, w=1440, h=900):
        self.w = w
        self.h = h
        self.screen_properties = ScreenProperties(self.w, self.h, L_GREEN, 'Traffic Simulation')
        self.intersection = Intersection(self.screen_properties)
        self.clock = pygame.time.Clock()
        
        # init game state
        self.cars = []
        self.spawn_time = time.time()
        
        # Initialize signals
        self.signals = [
            Signal(self.screen_properties.screen, (600, 350), (20, 100), 'Signal_West'),  # Signal West
            Signal(self.screen_properties.screen, (820, 450), (20, 100), 'Signal_East'),  # Signal East
            Signal(self.screen_properties.screen, (720, 330), (100, 20), 'Signal_North'),  # Signal North
            Signal(self.screen_properties.screen, (620, 550), (100, 20), 'Signal_South')  # Signal South
        ]
        
        # Initialize start button
        self.start_button = Button(self.screen_properties.screen, (self.w - 150, 20), (120, 50), 'Start')
        self.simulation_started = False
        
        # Initialize counters for each input lane
        self.counters = {
            'input_north': 0,
            'input_south': 0,
            'input_east': 0,
            'input_west': 0
        }
        
        # Load the trained model
        self.model = self.load_or_create_model()
        self.data = []  # Initialize data list for visualization
        self.current_signal_index = 0  # Track the current green signal
        self.last_switch_time = time.time()  # Track the last switch time
        
        # Initialize generation and car passed counters
        self.generation = 0
        self.cars_passed = 0
        self.cycle_count = 0
        
    def load_or_create_model(self):
        model_dir = 'D:/Python Codes/Reinforcement-Learning -Project/Traffic_management/model'
        os.makedirs(model_dir, exist_ok=True)  # Ensure the directory exists

        # Find the next available model file name
        model_index = 0
        while True:
            model_path = os.path.join(model_dir, f'model{"" if model_index == 0 else f".{model_index}"}.pkl')
            if not os.path.exists(model_path):
                break
            model_index += 1

        # If no model file exists, create a new model and save it
        if model_index == 0:
            model = self.create_model()
            joblib.dump(model, model_path)
        else:
            model_path = os.path.join(model_dir, 'model.pkl')
            model = joblib.load(model_path)

        return model
    
    def create_model(self):
        # Generate synthetic data for demonstration purposes
        np.random.seed(42)
        n_samples = 5000
        vehicle_count = np.random.randint(0, 50, n_samples)
        green_light_duration = np.random.normal(2, 0.5, n_samples) * vehicle_count + np.random.randint(1, 5, n_samples)

        # Create and train a simple linear regression model
        X = vehicle_count.reshape(-1, 1)
        y = green_light_duration
        model = LinearRegression()
        model.fit(X, y)

        return model

    def predict_green_light_duration(self):
        vehicle_counts = [
            self.counters['input_north'],
            self.counters['input_south'],
            self.counters['input_east'],
            self.counters['input_west']
        ]
        predictions = self.model.predict(np.array(vehicle_counts).reshape(-1, 1))
        return predictions
      
    # Add this method to update the model based on the reward
    def update_model(self):
        # Collect data for the current generation
        vehicle_counts = [
            self.counters['input_north'],
            self.counters['input_south'],
            self.counters['input_east'],
            self.counters['input_west']
        ]
        green_light_durations = self.predict_green_light_duration()

        # Calculate the reward (e.g., number of cars passed minus total waiting time)
        reward = self.cars_passed - self.calculate_waiting_time()

        # Update the model with new data
        X_new = np.array(vehicle_counts).reshape(-1, 1)
        y_new = np.array(green_light_durations) + reward  # Adjust the green light duration based on the reward
        self.model.fit(X_new, y_new)
        
    def update_signals(self):
      predictions = self.predict_green_light_duration()
      current_time = time.time()

      # Calculate the green light duration for each signal
      green_light_durations = [min(pred, 15) for pred in predictions]  # Ensure max duration is 15 seconds

      # Check if it's time to switch signals
      if current_time - self.last_switch_time >= green_light_durations[self.current_signal_index]:
        # Switch to the next signal in round-robin fashion
        self.current_signal_index = (self.current_signal_index + 1) % len(self.signals)
        self.last_switch_time = current_time

        # Check if a full cycle has passed (all signals have been green once)
        if self.current_signal_index == 0:
            self.cycle_count += 1  # Increment cycle counter

            # Check if two full cycles have passed
            if self.cycle_count == 2:
                self.generation += 1  # Increment generation counter
                self.update_model()  # Update the model after each generation
                self.collect_data()  # Collect data for the current generation
                self.cars_passed = 0  # Reset cars passed counter for the new generation
                self.cycle_count = 0  # Reset cycle counter

      # Update signal colors
      for i, signal in enumerate(self.signals):
        if i == self.current_signal_index:
            signal.color = GREEN
        else:
            signal.color = RED
            
    def _spawn_car(self):
        lane_coordinates = {
            Direction.LEFT: Point(1440, 475),
            Direction.RIGHT: Point(0, 375),
            Direction.DOWN: Point(745, 0),
            Direction.UP: Point(645, 900)
        }
        
        lane = random.choice(list(lane_coordinates.keys()))
        car = [lane_coordinates[lane], lane, SPEED, False]  # Add stopped state attribute
        # print(f"Spawned car at {car[0]} going {car[1]}")
        return car
    
    def _check_signal_collision(self, car):
        for signal in self.signals:
            signal_rect = pygame.Rect(*signal.position, *signal.size)
            car_rect = pygame.Rect(car[0].x, car[0].y, BLOCK_SIZE, BLOCK_SIZE)
            if signal_rect.colliderect(car_rect):
                if signal.color in [RED, YELLOW]:
                    if not car[3]:  # If the car was not already stopped
                        car[2] = 0  # Stop the car
                        car[3] = True  # Mark the car as stopped
                        # Increment the counter for the respective input lane
                        if car[1] == Direction.DOWN:
                            self.counters['input_north'] += 1
                        elif car[1] == Direction.UP:
                            self.counters['input_south'] += 1
                        elif car[1] == Direction.LEFT:
                            self.counters['input_east'] += 1
                        elif car[1] == Direction.RIGHT:
                            self.counters['input_west'] += 1
                elif signal.color == GREEN:
                    if car[3]:  # If the car was stopped
                        car[2] = SPEED  # Restore the car's speed
                        car[3] = False  # Mark the car as moving
                        self.cars_passed += 1  # Increment cars passed counter
                        # Decrement the counter for the respective input lane
                        if car[1] == Direction.DOWN:
                            self.counters['input_north'] -= 1
                        elif car[1] == Direction.UP:
                            self.counters['input_south'] -= 1
                        elif car[1] == Direction.LEFT:
                            self.counters['input_east'] -= 1
                        elif car[1] == Direction.RIGHT:
                            self.counters['input_west'] -= 1

    def _check_car_collision(self):
        for i, car1 in enumerate(self.cars):
            for j, car2 in enumerate(self.cars):
                if i != j:
                    car1_rect = pygame.Rect(car1[0].x, car1[0].y, BLOCK_SIZE, BLOCK_SIZE)
                    car2_rect = pygame.Rect(car2[0].x, car2[0].y, BLOCK_SIZE, BLOCK_SIZE)
                    if car1_rect.colliderect(car2_rect):
                        if car1[2] == 0:  # If car1 is stopped
                            car2[2] = 0  # Stop car2

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
                if self.start_button.handle_click(mouse_pos):
                    self.simulation_started = True
        
        if self.simulation_started:
            self.update_signals()
            # Spawn new car every 1 second
            if time.time() - self.spawn_time > 1:
                self.cars.append(self._spawn_car())
                self.spawn_time = time.time()
            
            # 2. move
            for car in self.cars:
                self._check_signal_collision(car)
                self._move(car)
            
            # self._check_car_distance()
            self._check_car_collision()
            
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
        self.screen_properties.fill()
        self.intersection.draw()
        for car in self.cars:
            print(f"Drawing car at {car[0]}")
            pygame.draw.rect(self.screen_properties.screen, BLACK, (car[0].x, car[0].y, BLOCK_SIZE * 3, BLOCK_SIZE * 3))
        for signal in self.signals:
            signal.draw()
        self.start_button.draw()
        
        # Display counters
        counter_font = pygame.font.SysFont('arial', 20)
        counter_texts = [
            f"North: {self.counters['input_north']}",
            f"South: {self.counters['input_south']}",
            f"East: {self.counters['input_east']}",
            f"West: {self.counters['input_west']}",
            f"Cars Passed: {self.cars_passed}",
            f"Generation: {self.generation}"
        ]
        for i, text in enumerate(counter_texts):
            text_surface = counter_font.render(text, True, BLACK)
            self.screen_properties.screen.blit(text_surface, (self.w - 150, 100 + i * 30))
        
        pygame.display.flip()
    
    # Add this method to calculate the total waiting time
    def calculate_waiting_time(self):
        total_waiting_time = 0
        for car in self.cars:
            if car[2] == 0:  # If the car is stopped
                total_waiting_time += 1  # Increment waiting time for each stopped car
        return total_waiting_time

    def _move(self, car):
        direction = car[1]
        if car[2] == 0:  # If speed is zero, the car is stopped
            return
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
        if ((center_x - 30 < car[0].x < center_x + 30) and (center_y - 30 < car[0].y < center_y + 30)):
            output_routes = {
                Direction.RIGHT: Point(790, 375), #820-30=790
                Direction.LEFT: Point(650, 475), #620+30=650
                Direction.UP: Point(645, 380),  #350+30 = 380
                Direction.DOWN: Point(745, 520) #550-30=520
            }
            new_direction = random.choice(list(output_routes.keys()))
            car[0] = output_routes[new_direction]
            car[1] = new_direction
    
    def collect_data(self):
      # Calculate the reward (e.g., number of cars passed minus total waiting time)
      reward = self.cars_passed - self.calculate_waiting_time()
    
      # Collect data for visualization
      self.data.append({
        'generation': self.generation,
        'cars_passed': self.cars_passed,
        'reward': reward
      })

    def update_plots(self, ax):
      ax.clear()
      generations = [d['generation'] for d in self.data]
      cars_passed = [d['cars_passed'] for d in self.data]
      rewards = [d['reward'] for d in self.data]
    
      ax.plot(generations, rewards, label='Reward per Generation', color='red', marker='o', linestyle='-')
      ax.plot(generations, cars_passed, label='Cars Passed per Generation', color='blue', marker='o', linestyle='-')
      
      ax.set_xlabel('Generation')
      ax.set_ylabel('Number of Cars Passed / Reward')
      ax.legend()
      plt.draw()
      plt.pause(0.01)

if __name__ == '__main__':
    game = CarGame()
    fig, ax = plt.subplots()  # Initialize Matplotlib figure and axis

    # game loop
    running = True
    while running:
        game.play_step()
        game.collect_data()  # Collect data for visualization
        game.update_plots(ax)  # Update Matplotlib plots

    pygame.quit()