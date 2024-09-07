# Smart-Traffic-Control--phase-one
A simulation project that optimizes traffic signal timings using reinforcement learning. The project integrates Pygame for simulation and visualization. The model learns from previous generations to improve traffic flow and reduce waiting times.


# Traffic Signal Optimization using Reinforcement Learning and Pygame


## Features
- **Traffic Signal Simulation**: Simulates traffic signals and vehicle movements using Pygame.
- **Reinforcement Learning**: Uses a linear regression model to predict green light durations and optimize traffic flow.
- **Visualization**: Provides real-time visualization of traffic flow and model performance.

## Installation
1. Clone the repository:

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
1. Run the simulation:
    ```bash
    python simulation.py
    ```

2. The simulation window will open, showing the traffic signal and vehicle movements. The model will learn and optimize the signal timings over generations.

## Project Structure
- `simulation.py`: Contains the main simulation code using Pygame.
- `AI-Model.py`: Contains the code for generating synthetic data and training the linear regression model.
- `requirements.txt`: Lists the required dependencies for the project.

## How It Works
1. **Simulation**: The simulation initializes traffic signals and vehicles. Vehicles move according to the signal timings.
2. **Reinforcement Learning**: The model predicts green light durations based on vehicle counts and updates the signal timings to maximize traffic flow.
3. **Visualization**: The simulation provides real-time visualization of traffic flow and model performance, including the number of cars passed and rewards gained over generations.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgements
- Pygame for the simulation framework.
- Scikit-learn for the linear regression model.

## Contact
For any questions or inquiries, please contact anshtrips07@gmail.com
