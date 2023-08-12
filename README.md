# LED Simulation

This repository contains a Dash application for LED simulation.

## Overview

The application allows users to simulate the power density of LEDs based on several parameters like the number of LEDs, LED intensity, environment factor, windshield factor, and more.

## Parameters:

- **LED Type**: Select between "Power LED" and "TSAL6400". This will change the default LED intensity and the angle intensities.
- **LED Intensity (mw/sr)**: Intensity of the LED.
- **Number of LEDs**: The total number of LEDs used.
- **Environment Factor**: Factor representing the environmental condition.
- **Windshield Factor**: Factor representing the windshield's effect.

## Setup & Running:

1. Clone and navigate to the repository:
git clone https://github.com/YOUR_USERNAME/led-simulation.git
cd led-simulation

2. Set up a Virtual Environment
Using venv:
- On Windows:
  ```
  py -3 -m venv .venv
  ```

- On Linux:
  ```
  python3 -m venv .venv
  ```

3. Activate the virtual environment:

- On Windows:
  ```
  .venv\Scripts\activate
  ```

- On Linux:
  ```
  source .venv/bin/activate
  ```

4. Install required packages:
pip install -r requirements.txt

5. Run the Dash app:
After running the above command, open your web browser and navigate to http://127.0.0.1:8050/ to view the simulator.

**Parameters:**

- LED Type: Choose between different types of LEDs, each with its unique radiant intensity profile.
- LED Intensity: Radiant intensity (in mW/sr) of the selected LED.
- Number of LEDs: Total number of LEDs.
- Environment Factor: External factor affecting received power density.
- Windshield Factor: Factor due to the windshield that affects received power density.
