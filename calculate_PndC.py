import streamlit as st
from itertools import product
import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

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

def calculate_distance(from_location, to_location):
    geolocator = Nominatim(user_agent="distance_calculator")
    location1 = geolocator.geocode(from_location)
    location2 = geolocator.geocode(to_location)

    if location1 and location2:
        coords_1 = (location1.latitude, location1.longitude)
        coords_2 = (location2.latitude, location2.longitude)
        return geodesic(coords_1, coords_2).kilometers
    else:
        return None

def calculate_transport_cost(distance, total_weight, petrol_price=94.97, mileage=4, weight_factor=0.1, base_weight=6000):
    fuel_needed = distance / mileage
    weight_adjustment = 1 + (weight_factor * (total_weight / base_weight))
    total_cost = fuel_needed * petrol_price * weight_adjustment
    return total_cost

import math

def suggest_reduction(volume_exceeded, weight_exceeded):
    suggestions = []
    if volume_exceeded:
        excess_volume = st.session_state.combo_details['Total Volume Utilized'] - st.session_state.truck_volume
        small_volume_reduction = math.ceil(excess_volume / st.session_state.small_box_volume)
        medium_volume_reduction = math.ceil(excess_volume / st.session_state.medium_box_volume)
        large_volume_reduction = math.ceil(excess_volume / st.session_state.large_box_volume)
        suggestions.append(f"Reduce by at least {small_volume_reduction} small boxes, or {medium_volume_reduction} medium boxes, or {large_volume_reduction} large boxes to fit within volume limit.")
    
    if weight_exceeded:
        excess_weight = st.session_state.combo_details['Total Weight'] - st.session_state.truck_weight_capacity
        small_weight_reduction = math.ceil(excess_weight / st.session_state.small_box_weight)
        medium_weight_reduction = math.ceil(excess_weight / st.session_state.medium_box_weight)
        large_weight_reduction = math.ceil(excess_weight / st.session_state.large_box_weight)
        suggestions.append(f"Reduce by at least {small_weight_reduction} small boxes, or {medium_weight_reduction} medium boxes, or {large_weight_reduction} large boxes to fit within weight limit.")
    
    return suggestions


# Streamlit UI
st.set_page_config(page_title="Truck Loading Optimization", page_icon="🚚", layout="centered")

# Apply custom CSS styles
st.markdown(
    """
    <style>
    /* Common styles for both light and dark modes */
    .main {
        background-color: #f4f4f4; /* Light mode background */
        color: #333; /* Dark text color for light mode */
        font-family: 'Helvetica Neue', sans-serif;
        padding: 20px;
    }
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #e74c3c;
        text-align: center;
        margin-bottom: 20px;
    }
    .header {
        font-size: 24px;
        color: #3498db;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #34495e;
    }
    .subheader {
        font-size: 20px;
        color: #95a5a6;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .container {
        max-width: 800px;
        margin: 0 auto;
    }
    .btn-calculate {
        background-color: #2980b9;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        font-size: 16px;
        margin: 20px 0;
        cursor: pointer;
        border-radius: 5px;
    }
    .btn-calculate:hover {
        background-color: #3498db;
    }
    .btn-select, .btn-3d-view {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 5px 10px;
        text-align: center;
        font-size: 12px;
        cursor: pointer;
        border-radius: 5px;
        margin-right: 5px;
    }
    .btn-select:hover, .btn-3d-view:hover {
        background-color: #2ecc71;
    }

    /* Styles for dark mode (if applicable) */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: #1e1e1e; /* Dark mode background */
            color: #ffffff; /* Light text color for dark mode */
        }
        .header {
            color: #3498db; /* Light color for dark mode */
            border-bottom: 2px solid #34495e;
        }
        .subheader {
            color: #95a5a6; /* Light color for dark mode */
        }
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown("<div class='container'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🚚 Truck Loading Optimization</div>", unsafe_allow_html=True)

st.write("""
Welcome to the Truck Loading Optimization tool! 
Follow the steps below to calculate the optimal loading configuration for your truck.
""")

# Initialize session state if it does not exist
if 'selected_combo' not in st.session_state:
    st.session_state.selected_combo = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'combo_details' not in st.session_state:
    st.session_state.combo_details = None

# Navigation buttons
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def update_combo_details(box_type, action):
    if action == 'add':
        st.session_state.combo_details[box_type] += 1
    elif action == 'subtract' and st.session_state.combo_details[box_type] > 0:
        st.session_state.combo_details[box_type] -= 1

    # Update total volume and weight
    st.session_state.combo_details['Total Volume Utilized'] = (
        st.session_state.combo_details['Small Box'] * st.session_state.small_box_volume +
        st.session_state.combo_details['Medium Box'] * st.session_state.medium_box_volume +
        st.session_state.combo_details['Large Box'] * st.session_state.large_box_volume
    )
    st.session_state.combo_details['Total Weight'] = (
        st.session_state.combo_details['Small Box'] * st.session_state.small_box_weight +
        st.session_state.combo_details['Medium Box'] * st.session_state.medium_box_weight +
        st.session_state.combo_details['Large Box'] * st.session_state.large_box_weight
    )

# Step 1: Input truck specifications
if st.session_state.step == 1:
    st.markdown("<div class='header'>Step 1: Enter Truck Specifications</div>", unsafe_allow_html=True)
    truck_length = st.number_input("Truck Storage Length (cm)", min_value=0.0, value=734.0, help="Enter the internal length of the truck storage area.")
    truck_width = st.number_input("Truck Storage Width (cm)", min_value=0.0, value=244.0, help="Enter the internal width of the truck storage area.")
    truck_height = st.number_input("Truck Storage Height (cm)", min_value=0.0, value=290.0, help="Enter the internal height of the truck storage area.")
    truck_weight_capacity = st.number_input("Truck Weight Capacity (kg)", min_value=0.0, value=29600.0, help="Enter the maximum weight capacity of the truck.")

    if st.button("Next"):
        truck_volume = truck_length * truck_width * truck_height
        st.session_state.truck_volume = truck_volume
        st.session_state.truck_weight_capacity = truck_weight_capacity
        next_step()

# Step 2: Input small box specifications
elif st.session_state.step == 2:
    st.markdown("<div class='header'>Step 2: Enter Small Box Specifications</div>", unsafe_allow_html=True)
    box_length = st.number_input("Small Box Length (cm)", min_value=0.0, value=140.0, help="Enter the length of the small box.")
    box_width = st.number_input("Small Box Width (cm)", min_value=0.0, value=53.0, help="Enter the width of the small box.")
    box_height = st.number_input("Small Box Height (cm)", min_value=0.0, value=70.0, help="Enter the height of the small box.")
    box_weight = st.number_input("Small Box Weight (kg)", min_value=0.0, value=170.0, help="Enter the weight of one small box.")

    if st.button("Next"):
        small_box_volume = box_length * box_width * box_height
        st.session_state.small_box_volume = small_box_volume
        st.session_state.small_box_weight = box_weight
        next_step()
    if st.button("Previous"):
        prev_step()

# Step 3: Input medium box specifications
elif st.session_state.step == 3:
    st.markdown("<div class='header'>Step 3: Enter Medium Box Specifications</div>", unsafe_allow_html=True)
    box_length = st.number_input("Medium Box Length (cm)", min_value=0.0, value=160.0, help="Enter the length of the medium box.")
    box_width = st.number_input("Medium Box Width (cm)", min_value=0.0, value=53.0, help="Enter the width of the medium box.")
    box_height = st.number_input("Medium Box Height (cm)", min_value=0.0, value=90.0, help="Enter the height of the medium box.")
    box_weight = st.number_input("Medium Box Weight (kg)", min_value=0.0, value=180.0, help="Enter the weight of one medium box.")

    if st.button("Next"):
        medium_box_volume = box_length * box_width * box_height
        st.session_state.medium_box_volume = medium_box_volume
        st.session_state.medium_box_weight = box_weight
        next_step()
    if st.button("Previous"):
        prev_step()

# Step 4: Input large box specifications and calculate combinations
elif st.session_state.step == 4:
    st.markdown("<div class='header'>Step 4: Enter Large Box Specifications and Calculate Combinations</div>", unsafe_allow_html=True)
    box_length = st.number_input("Large Box Length (cm)", min_value=0.0, value=180.0, help="Enter the length of the large box.")
    box_width = st.number_input("Large Box Width (cm)", min_value=0.0, value=53.0, help="Enter the width of the large box.")
    box_height = st.number_input("Large Box Height (cm)", min_value=0.0, value=110.0, help="Enter the height of the large box.")
    box_weight = st.number_input("Large Box Weight (kg)", min_value=0.0, value=190.0, help="Enter the weight of one large box.")

    if st.button("Calculate Combinations", key="calculate", help="Click to calculate the optimal loading combinations for your truck."):
        large_box_volume = box_length * box_width * box_height
        st.session_state.large_box_volume = large_box_volume
        st.session_state.large_box_weight = box_weight

        box_dimensions = [
            st.session_state.small_box_volume,
            st.session_state.medium_box_volume,
            st.session_state.large_box_volume
        ]
        box_weights = [
            st.session_state.small_box_weight,
            st.session_state.medium_box_weight,
            st.session_state.large_box_weight
        ]
        truck_volume = st.session_state.truck_volume
        truck_weight_capacity = st.session_state.truck_weight_capacity

        combinations = best_combination_with_constraints(truck_volume, truck_weight_capacity, box_dimensions, box_weights)
        
        st.write("### Optimal Loading Combinations:")
        data = {
            "Combination": [f"Combo {i+1}" for i in range(len(combinations))],
            "Small Box": [combo[0] for combo in combinations],
            "Medium Box": [combo[1] for combo in combinations],
            "Large Box": [combo[2] for combo in combinations],
            "Total Volume Utilized": [combo[-2] for combo in combinations],
            "Total Weight": [combo[-1] for combo in combinations]
        }
        df = pd.DataFrame(data)

        st.write(df)

        def select_combo(idx):
            st.session_state.selected_combo = df.iloc[idx]
            st.session_state.combo_details = st.session_state.selected_combo.to_dict()
            next_step()

        def view_3d(idx):
            st.session_state.view = '3d_view'
            st.session_state.image_path = "https://ibb.co/0JzgqcF"  # Replace with your image path


        headers = ["Combination", "Small Box", "Medium Box", "Large Box", "Total Volume Utilized", "Total Weight", "Select", "3D View"]
        cols = st.columns(len(headers))
        for col, header in zip(cols, headers):
            col.write(f"**{header}**")

        for idx, row in df.iterrows():
            cols = st.columns(len(headers))
            cols[0].write(row['Combination'])
            cols[1].write(row['Small Box'])
            cols[2].write(row['Medium Box'])
            cols[3].write(row['Large Box'])
            cols[4].write(row['Total Volume Utilized'])
            cols[5].write(row['Total Weight'])
            cols[6].button("Select", key=f"select_{idx}", on_click=select_combo, args=(idx,))
            cols[7].button("3D View", key=f"3d_view_{idx}", on_click=view_3d, args=(idx,))

    if st.button("Previous"):
        prev_step()

elif st.session_state.step == 5 and st.session_state.selected_combo is not None:
    st.markdown("<div class='header'>Selected Combination</div>", unsafe_allow_html=True)
    combo = st.session_state.combo_details

    st.write(f"### Selected Combination Details:")
    col1, col2, col3 = st.columns([1, 1, 1])
    col1.write(f"Small Boxes: {combo['Small Box']}")
    col2.button("➕", key="add_small", on_click=update_combo_details, args=('Small Box', 'add'))
    col3.button("➖", key="subtract_small", on_click=update_combo_details, args=('Small Box', 'subtract'))

    col1, col2, col3 = st.columns([1, 1, 1])
    col1.write(f"Medium Boxes: {combo['Medium Box']}")
    col2.button("➕", key="add_medium", on_click=update_combo_details, args=('Medium Box', 'add'))
    col3.button("➖", key="subtract_medium", on_click=update_combo_details, args=('Medium Box', 'subtract'))

    col1, col2, col3 = st.columns([1, 1, 1])
    col1.write(f"Large Boxes: {combo['Large Box']}")
    col2.button("➕", key="add_large", on_click=update_combo_details, args=('Large Box', 'add'))
    col3.button("➖", key="subtract_large", on_click=update_combo_details, args=('Large Box', 'subtract'))

    st.write(f"Total Volume Utilized: {combo['Total Volume Utilized']} cubic cm")
    st.write(f"Total Weight: {combo['Total Weight']} kg")

    # Check if the total volume or weight exceeds the truck's capacity
    volume_exceeded = st.session_state.combo_details['Total Volume Utilized'] > st.session_state.truck_volume
    weight_exceeded = st.session_state.combo_details['Total Weight'] > st.session_state.truck_weight_capacity

    if volume_exceeded or weight_exceeded:
        st.error("The current configuration exceeds the truck's capacity. Please reduce the number of boxes.")
        suggestions = suggest_reduction(volume_exceeded, weight_exceeded)
        for suggestion in suggestions:
            st.write(suggestion)
    
    # # New section for transport pricing
    # st.markdown("<div class='header'>Estimate transport pricing for this combination</div>", unsafe_allow_html=True)
    # col1, col2 = st.columns(2)
    # from_location = col1.text_input("From", help="Enter the starting location.")
    # to_location = col2.text_input("To", help="Enter the destination location.")

    # if st.button("Estimate Cost"):
    #     if from_location and to_location:
    #         distance = calculate_distance(from_location, to_location)
    #         if distance is not None:
    #             price_per_km = 5  # Placeholder for pricing logic
    #             estimated_price = calculate_transport_cost(distance , combo['Total Weight'])
    #             st.write(f"Distance: {distance:.2f} km")
    #             st.write(f"Estimated Transport Price: ₹{estimated_price:.2f}")
    #         else:
    #             st.write("Error: Unable to calculate distance. Please check the locations and try again.")
    #     else:
    #         st.write("Please enter both the starting location and the destination.")

    if st.button("Go Back"):
        st.session_state.selected_combo = None
        st.session_state.combo_details = None
        prev_step()

st.markdown("</div>", unsafe_allow_html=True)
