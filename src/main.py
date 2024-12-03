import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
from tkinter import Tk, Scale, Button, Label, HORIZONTAL, Entry
import math
from datetime import datetime

def parse_gpx(file_path):
    """
    Parse a .gpx file and extract GPS coordinates with timestamps.
    """
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    data = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if point.time:
                    data.append((point.latitude, point.longitude, point.time))
    return data

def rotate_coordinates(coordinates, angle, center):
    """
    Rotate coordinates around a center point by a given angle.

    Args:
        coordinates (list): List of (latitude, longitude) tuples.
        angle (float): Angle in degrees to rotate the coordinates.
        center (tuple): The (latitude, longitude) of the center point.

    Returns:
        list: Rotated coordinates.
    """
    angle_rad = math.radians(angle)
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)

    center_lat, center_lon = center

    rotated = []
    for lat, lon in coordinates:
        # Translate the point relative to the center
        lat_shifted = lat - center_lat
        lon_shifted = lon - center_lon

        # Apply rotation
        lat_rotated = lat_shifted * cos_theta - lon_shifted * sin_theta
        lon_rotated = lat_shifted * sin_theta + lon_shifted * cos_theta

        # Translate back to original position
        lat_final = lat_rotated + center_lat
        lon_final = lon_rotated + center_lon

        rotated.append((lat_final, lon_final))

    return rotated

def filter_coordinates_by_time(data, start_time, end_time):
    """
    Filter coordinates by time range.

    Args:
        data (list): List of (latitude, longitude, timestamp) tuples.
        start_time (str): Start time in "HH:MM" format.
        end_time (str): End time in "HH:MM" format.

    Returns:
        list: Filtered (latitude, longitude) tuples.
    """
    filtered = []
    for lat, lon, time in data:
        time_str = time.strftime("%H:%M")
        if start_time <= time_str <= end_time:
            filtered.append((lat, lon))
    return filtered

def plot_path(coordinates, zoom=1, rotation=0):
    """
    Plot the GPS path using matplotlib with zoom and rotation functionality.

    Args:
        coordinates (list): List of (latitude, longitude) tuples.
        zoom (float): Zoom level, where 1 is default and higher values zoom in.
        rotation (float): Rotation angle in degrees.
    """
    if not coordinates:
        print("No coordinates to plot.")
        return

    # Calculate the center of the path
    latitudes, longitudes = zip(*coordinates)
    center_lat = (max(latitudes) + min(latitudes)) / 2
    center_lon = (max(longitudes) + min(longitudes)) / 2
    center = (center_lat, center_lon)

    # Rotate coordinates
    rotated_coordinates = rotate_coordinates(coordinates, rotation, center)

    # Calculate zoomed bounds
    rotated_latitudes, rotated_longitudes = zip(*rotated_coordinates)
    range_lat = (max(rotated_latitudes) - min(rotated_latitudes)) / zoom
    range_lon = (max(rotated_longitudes) - min(rotated_longitudes)) / zoom

    min_lat, max_lat = center_lat - range_lat / 2, center_lat + range_lat / 2
    min_lon, max_lon = center_lon - range_lon / 2, center_lon + range_lon / 2

    # Plot the path with zoomed and rotated bounds
    plt.figure(figsize=(10, 8))
    plt.plot(rotated_longitudes, rotated_latitudes, marker='o', linestyle='-', color='blue')
    plt.xlim(min_lon, max_lon)
    plt.ylim(min_lat, max_lat)
    plt.title(f"Running Path (Zoom: {zoom}x, Rotation: {rotation}°)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid()
    plt.show()

def create_gui_with_time_filter(data):
    """
    Create a GUI with live updates for zoom and rotation and time filtering.
    """
    # Initialize GUI state
    filtered_coordinates = data

    def update_plot():
        """
        Update the plot based on slider and time input values.
        """
        nonlocal filtered_coordinates

        # Get user inputs
        zoom_value = zoom_slider.get()
        rotation_value = rotation_slider.get()
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()

        # Filter by time
        try:
            filtered_coordinates = filter_coordinates_by_time(data, start_time, end_time)
        except ValueError:
            print("Invalid time format. Use HH:MM.")

        # Plot the filtered coordinates
        plot_path(filtered_coordinates, zoom=zoom_value, rotation=rotation_value)

    # Create the main window
    root = Tk()
    root.title("Running Path Viewer with Time Filter")

    # Time Filter Inputs
    Label(root, text="Start Time (HH:MM)").pack()
    start_time_entry = Entry(root)
    start_time_entry.insert(0, "00:00")
    start_time_entry.pack()

    Label(root, text="End Time (HH:MM)").pack()
    end_time_entry = Entry(root)
    end_time_entry.insert(0, "23:59")
    end_time_entry.pack()

    # Zoom Slider
    Label(root, text="Adjust Zoom").pack()
    zoom_slider = Scale(root, from_=1, to=10, resolution=0.1, orient=HORIZONTAL)
    zoom_slider.set(1)
    zoom_slider.pack()

    # Rotation Slider
    Label(root, text="Adjust Rotation (Degrees)").pack()
    rotation_slider = Scale(root, from_=-180, to=180, resolution=1, orient=HORIZONTAL)
    rotation_slider.set(0)
    rotation_slider.pack()

    # Update Plot Button
    Button(root, text="Update Plot", command=update_plot).pack()

    # Run the GUI loop
    root.mainloop()

if __name__ == "__main__":
    # Absolute path to your .gpx file
    gpx_file_path = "C:/Users/danie/PycharmProjects/FinishLine/data/your_file.gpx"

    # Parse the .gpx file
    print("Parsing GPX file...")
    gps_data = parse_gpx(gpx_file_path)

    # Create the GUI with time filtering
    print("Launching GUI with time filtering...")
    create_gui_with_time_filter(gps_data)
