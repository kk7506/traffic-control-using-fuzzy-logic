# Libraries #
import time # for time delay.
import random # for generating numbers.
import numpy as np # numerical operations.
import skfuzzy as fuzzy # fuzzy operations.
from skfuzzy import control # fuzzy operations.
import matplotlib.pyplot as plot # data visualization.

# Variables / Inputs-Outputs #
simulations = 10
cars_inlane = control.Antecedent(np.arange(0, 41, 1), 'cars_inlane') # range of cars that can be waiting in a traffic light/lane (0-40).
green_light_time = control.Consequent(np.arange(15, 31, 1), 'green_light') # range of seconds green light can be lit (15-30sec).

# Linguistic Variables - Labels #                 # tringular values #
# Assigning labels to determine low-medium-high queue of cars waiting.
cars_inlane['low'] = fuzzy.trimf(cars_inlane.universe, [0, 0, 50])
cars_inlane['medium'] = fuzzy.trimf(cars_inlane.universe, [0, 50, 100])
cars_inlane['high'] = fuzzy.trimf(cars_inlane.universe, [50, 100, 100])

# Assigning labels to determine short-medium-high time of green light being lit.
green_light_time['short'] = fuzzy.trimf(green_light_time.universe, [10, 10, 20])
green_light_time['medium'] = fuzzy.trimf(green_light_time.universe, [10, 20, 30])
green_light_time['long'] = fuzzy.trimf(green_light_time.universe, [20, 30, 30])

# Rule Set - Determining how much the light will be lit dependign on the total cars waiting in the lane #
rule1 = control.Rule(cars_inlane['low'], green_light_time['short'])
rule2 = control.Rule(cars_inlane['medium'], green_light_time['medium'])
rule3 = control.Rule(cars_inlane['high'], green_light_time['long'])

# Parameters #
delay = 2 # seconds between simulations.

# Initialize the Control System #
data = {'west': 0, 'south': 0, 'east': 0, 'north': 0} # Each traffic light is named based on its geographical position - starting with 0 cars in each lane.
traffic_control = control.ControlSystem([rule1, rule2, rule3]) # Passing the rules.
traffic = control.ControlSystemSimulation(traffic_control) # Creating the Control System.

### Functions - Classes ###
# Pair of Lights Class - the pairs are based on the mirroring positions of the lanes, so: west<->east and north<->south #
class TrafficLightPairs:
    PAIR1 = ('west', 'east')
    PAIR2 = ('north', 'south')

# Switch the status for the traffic light pairs if:green->red / if:red->green #
def switch_traffic_light_pairs(c_pair):
    if c_pair == TrafficLightPairs.PAIR1:
        return TrafficLightPairs.PAIR2
    else:
        return TrafficLightPairs.PAIR1

# Get user input for arrival rates #
def get_user_input():
    print("[SYSTEM] Provide the average number of cars arriving on each traffic light.")
    inputs = {} # Empty dictionary.
    for light in data:
        while True:
            try:
                rate = float(input(f"[SYSTEM] Enter arrival rate (/sec) for traffic light in the {light} [Range: 0.2-5] -> "))
                if 0.2 <= rate <= 5:
                    inputs[light] = float(rate) # Store the input.
                    break
                else:
                    print("[SYSTEM] Out of bounds! Please try again [Range: 0.2-5].")
            except ValueError:
                print("[SYSTEM] Invalid input. Please enter a float number")
    return inputs

# Visualize the most frequent times for the green light - histograma #
def green_light_times_fun(gl_times): # green_light_times
    plot.hist(gl_times, bins=10, edgecolor='black')
    plot.title('Distribution of data')
    plot.xlabel('Green Light (in seconds)')
    plot.ylabel('Frequency')
    plot.show()

# Main/Core #
def main():
    print("----- Starting simulation of Traffic Control using Fuzzy Logic -----\n")
    
    # Initializations #
    car_arrivals = get_user_input() # Get user input for the rate of arrivals.
    green_light_times = [] # Empty list to store each simulation's green light time.
    
    # Pass the first pair to start the simulations #
    current_traffic_light_pair = TrafficLightPairs.PAIR1 # west-east.
    
    # Simulations #
    for simulation in range(simulations):
        print(f"\n(Simulation: {simulation+1})")
        
        # Update user and system which pair of lights is green and red #
        if current_traffic_light_pair == TrafficLightPairs.PAIR1:
            green_pair = TrafficLightPairs.PAIR1
            red_pair = TrafficLightPairs.PAIR2
        else:
            green_pair = TrafficLightPairs.PAIR2
            red_pair = TrafficLightPairs.PAIR1
        
        print(f"\n[SYSTEM] Traffic Lights of {green_pair[0]} and {green_pair[1]} are green! Clearing them out...")
        
        max_green_of_pair = 0
        # Green Light Pair Segment - emptying their lanes #
        for light in green_pair:
            traffic.input['cars_inlane'] = data[light] # Takes the number of cars in the lane as input.
            traffic.compute() # Computes results as the Fuzzy Logic Controller.
            green_light_time_value = float(traffic.output['green_light']) # Duration of light pair being green.
            max_green_of_pair = max(max_green_of_pair, green_light_time_value)
            print(f"[SYSTEM] {light} cleared out {data[light]} cars.")
            data[light] = 0
        
        # Cut down the time output for each pair to 2 decimal points for observation #
        green_light_time_format = "{:.2f}".format(green_light_time_value) # :.2f -> decimal points.
        print(f"\n[SYSTEM] Green Light time for {green_pair[0]} and {green_pair[1]}: {green_light_time_format} seconds.")
        
        # Red Light Pair Segment - calculate cars piling up on the lanes #
        for light in red_pair:
            arrivals = car_arrivals[light]*max_green_of_pair # Based on the arrival rates the user has provided and the green light duration.
            data[light] += random.randint(0, int(arrivals)) # Add the piled cars to each traffic light/lane.
        
        # Store it to the list #
        green_light_times.append(max_green_of_pair)
            
        # Time delay for data observation #
        time.sleep(delay)
        
        # Switch traffic light pair - status #
        current_traffic_light_pair = switch_traffic_light_pairs(current_traffic_light_pair)
    
    print("\n----- Exiting Program -----")
    
    # Visualize data about the total green times #
    green_light_times_fun(green_light_times)
    
# Execute the program # 
if __name__ == "__main__":
    main()