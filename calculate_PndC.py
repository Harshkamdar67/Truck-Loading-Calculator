import streamlit as st
from itertools import product

def best_combination_with_constraints(truck_volume, truck_weight_capacity, box_dimensions, box_weights):
    combinations = []
    num_box_types = len(box_dimensions)

    # Generate all combinations dynamically for the number of box types provided
    max_boxes = [int(truck_volume // dim) for dim in box_dimensions]
    
    for combo in product(*(range(n + 1) for n in max_boxes)):
        total_volume = sum(combo[i] * box_dimensions[i] for i in range(num_box_types))
        total_weight = sum(combo[i] * box_weights[i] for i in range(num_box_types))
        if total_volume <= truck_volume and total_weight <= truck_weight_capacity:
            combinations.append(combo + (total_volume, total_weight))
    
    # Sort combinations by volume and weight, and select the most optimal ones
    combinations.sort(key=lambda x: (-x[-2], -x[-1]))
    optimal_combinations = combinations[:10]  # Limiting to top 10 most optimal combinations

    return optimal_combinations

def convert_volume_to_dimensions(volume):
    length = volume[0]
    width = volume[1]
    height = volume[2]
    length_ft = int(length)
    length_in = int((length - length_ft) * 12)
    width_ft = int(width)
    width_in = int((width - width_ft) * 12)
    height_ft = int(height)
    height_in = int((height - height_ft) * 12)
    return length_ft, length_in, width_ft, width_in, height_ft, height_in

# Streamlit UI
st.title("Truck Loading Permutations and Combinations")

# Input fields for truck specifications
truck_length = st.number_input("Truck storage Length (in feet)", min_value=0.0, value=24.0833)
truck_width = st.number_input("Truck storage Width (in feet)", min_value=0.0, value=8.0)
truck_height = st.number_input("Truck storage Height (in feet)", min_value=0.0, value=9.5)
truck_weight_capacity = st.number_input("Truck Weight Capacity (in kg)", min_value=0.0, value=29600.0)

truck_volume = truck_length * truck_width * truck_height

# Input fields for box specifications
box_dimensions = []
box_weights = []
num_boxes = st.number_input("Number of Box Types (in sizes)", min_value=1, value=1)

for i in range(num_boxes):
    st.header(f"Box Type {i + 1}")
    box_length = st.number_input(f"Box type {i + 1} Length (in feet)", min_value=0.0)
    box_width = st.number_input(f"Box type {i + 1} Width (in feet)", min_value=0.0)
    box_height = st.number_input(f"Box type {i + 1} Height (in feet)", min_value=0.0)
    box_weight = st.number_input(f"Box type {i + 1} Weight (in kg)", min_value=0.0)
    
    box_volume = box_length * box_width * box_height
    box_dimensions.append(box_volume)
    box_weights.append(box_weight)

# Calculate and display combinations
if st.button("Calculate Combinations"):
    combinations = best_combination_with_constraints(truck_volume, truck_weight_capacity, box_dimensions, box_weights)
    
    st.write(f"Total Truck Volume: {truck_volume:.2f} cubic feet")
    st.write(f"Truck Weight Capacity: {truck_weight_capacity} kg")

    for combo in combinations:
        result = ", ".join(f"Box {i + 1}: {count}" for i, count in enumerate(combo[:-2]))
        total_volume, total_weight = combo[-2], combo[-1]
        
        volume_limit_reached = total_volume >= truck_volume * 0.95
        weight_limit_reached = total_weight >= truck_weight_capacity * 0.95
        
        if volume_limit_reached:
            volume_status = "Volume limit reached!"
        else:
            volume_status = "Volume OK"
            
        if weight_limit_reached:
            weight_status = "Weight limit reached!"
        else:
            weight_status = "Weight OK"

        st.write(f"{result}, Total Volume: {total_volume:.2f} cubic feet ({volume_status}), Total Weight: {total_weight} kg ({weight_status})")
