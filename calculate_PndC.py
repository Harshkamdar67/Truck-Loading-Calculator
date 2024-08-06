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

# Function to calculate distance between two locations
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

# Streamlit UI
st.set_page_config(page_title="Truck Loading Optimization", page_icon="🚚", layout="centered")

# Apply custom CSS styles
st.markdown(
    """
    <style>
    .main {
        background-color: #1e1e1e;
        color: #ffffff;
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
    .btn-select {
        background-color: #27ae60;
        color: white;
        border: none;
        padding: 5px 10px;
        text-align: center;
        font-size: 12px;
        cursor: pointer;
        border-radius: 5px;
    }
    .btn-select:hover {
        background-color: #2ecc71;
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

# Step 1: Input truck specifications
if st.session_state.selected_combo is None:
    st.markdown("<div class='header'>Step 1: Enter Truck Specifications</div>", unsafe_allow_html=True)
    truck_length = st.number_input("Truck Storage Length (cm)", min_value=0.0, value=734.0, help="Enter the internal length of the truck storage area.")
    truck_width = st.number_input("Truck Storage Width (cm)", min_value=0.0, value=244.0, help="Enter the internal width of the truck storage area.")
    truck_height = st.number_input("Truck Storage Height (cm)", min_value=0.0, value=290.0, help="Enter the internal height of the truck storage area.")
    truck_weight_capacity = st.number_input("Truck Weight Capacity (kg)", min_value=0.0, value=29600.0, help="Enter the maximum weight capacity of the truck.")

    truck_volume = truck_length * truck_width * truck_height

    # Step 2: Input box specifications
    st.markdown("<div class='header'>Step 2: Enter Box Specifications</div>", unsafe_allow_html=True)
    box_types = ["Small", "Medium", "Large"]
    box_dimensions = []
    box_weights = []
    num_boxes = len(box_types)

    for i in range(num_boxes):
        st.markdown(f"<div class='subheader'>{box_types[i]} Box</div>", unsafe_allow_html=True)
        default_length = 140.0
        default_width = 53.0
        default_height = 70.0 + (i * 20.0)
        default_weight = 170.0 + (i * 10.0)
        
        box_length = st.number_input(f"{box_types[i]} Box Length (cm)", min_value=0.0, value=default_length, help=f"Enter the length of the {box_types[i].lower()} box.")
        box_width = st.number_input(f"{box_types[i]} Box Width (cm)", min_value=0.0, value=default_width, help=f"Enter the width of the {box_types[i].lower()} box.")
        box_height = st.number_input(f"{box_types[i]} Box Height (cm)", min_value=0.0, value=default_height, help=f"Enter the height of the {box_types[i].lower()} box.")
        box_weight = st.number_input(f"Bale Weight for {box_types[i]} Box (kg)", min_value=0.0, value=default_weight, help=f"Enter the weight of one {box_types[i].lower()} box.")
        
        box_volume = box_length * box_width * box_height
        box_dimensions.append(box_volume)
        box_weights.append(box_weight)

    # Step 3: Calculate and display combinations
    st.markdown("<div class='header'>Step 3: Calculate Optimal Loading</div>", unsafe_allow_html=True)
    if st.button("Calculate Combinations", key="calculate", help="Click to calculate the optimal loading combinations for your truck."):
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

        headers = ["Combination", "Small Box", "Medium Box", "Large Box", "Total Volume Utilized", "Total Weight", "Select"]
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

else:
    st.markdown("<div class='header'>Selected Combination</div>", unsafe_allow_html=True)
    combo = st.session_state.selected_combo
    st.write(f"### Selected Combination Details:")
    st.write(f"Small Boxes: {combo['Small Box']}")
    st.write(f"Medium Boxes: {combo['Medium Box']}")
    st.write(f"Large Boxes: {combo['Large Box']}")
    st.write(f"Total Volume Utilized: {combo['Total Volume Utilized']} cubic cm")
    st.write(f"Total Weight: {combo['Total Weight']} kg")

    # New section for transport pricing
    st.markdown("<div class='header'>Estimate transport pricing for this combination</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    from_location = col1.text_input("From", help="Enter the starting location.")
    to_location = col2.text_input("To", help="Enter the destination location.")

    if st.button("Estimate Cost"):
        if from_location and to_location:
            distance = calculate_distance(from_location, to_location)
            if distance is not None:
                price_per_km = 5  # Placeholder for pricing logic
                estimated_price = calculate_transport_cost(distance , combo['Total Weight'])
                st.write(f"Distance: {distance:.2f} km")
                st.write(f"Estimated Transport Price: ₹{estimated_price:.2f}")
            else:
                st.write("Error: Unable to calculate distance. Please check the locations and try again.")
        else:
            st.write("Please enter both the starting location and the destination.")

    if st.button("Go Back"):
        st.session_state.selected_combo = None

st.markdown("</div>", unsafe_allow_html=True)
