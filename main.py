import numpy
import matplotlib.pyplot as plot

# Constants
G = 9.81        # Acceleration due to gravity (m/s^2)
RHO = 1.225     # Air density at sea level (kg/m^3)
CD = 0.47       # Drag Coefficient for a sphere
RADIUS = 0.05   # Radius of projectile (meters)
MASS  = 0.5     # Mass of projectile (kg)
AREA = numpy.pi * (RADIUS ** 2)
DT = 0.005      # Time step (sec)

def run_simulation(v0, angle_deg, v_wind, drag=True):
    """
    Simulates the flight of a projectile with or without air resistance. Returns: (list of x and y coordinates and final range)
    """
    
    angle_rad = numpy.radians(angle_deg)

    # Initial components
    vx = v0 * numpy.cos(angle_rad)
    vy = v0 * numpy.sin(angle_rad)

    x, y = 0.0, 0.0
    x_path = [x]
    y_path = [y]

    while y >= 0:
        # Velocity relative to air
        v_rel_x = vx + v_wind
        v_rel_y = vy     # No vertical wind

        # Total velocity
        v_rel = numpy.sqrt(v_rel_x**2 + v_rel_y**2)

        # Forces (Fd = 0.5 * rho * v^2 * Cd * A)
        # a = Fd/m -> we include one 'v' in the drag_factor to handle components easily
        if drag:
            drag_val = 0.5 * RHO * v_rel * CD * AREA / MASS
        else:
            drag_val = 0.0

        ax = -(drag_val * v_rel_x)
        ay = - G - (drag_val * v_rel_y)

        # Updating Velocities
        vx += ax * DT
        vy += ay * DT

        # Updating Positions
        x += vx * DT
        y += vy * DT

        # Store Positions
        x_path.append(x)
        y_path.append(y)

        # Prevent infinite loops
        if len(x_path) > 100000:
            break
    
    return x_path, y_path, x

def find_optimal_angle(v0, v_wind, drag=True):
    """
    Iterates through angles to find which one produces the maximum range. Returns: (best_angle, best_x_path, best_y_path)
    """
    best_range = 0.0
    best_angle = 0.0
    best_path = ([],[])

    for i in range(0,180):
        angle = i * 0.5
        x_pts, y_pts, final_range = run_simulation(v0, angle, v_wind, drag=drag)

        if final_range > best_range:
            best_range = final_range
            best_angle = angle
            best_path = (x_pts, y_pts)

    return best_angle, best_path[0], best_path[1], best_range

def main():
    try:
        user_v0 = float(input("Enter Initial Velocity (m/s): "))
        user_angle = float(input("Enter Launch Angle (degrees): "))
        user_v_wind = float(input("Enter Wind Speed (m/s, positive for tailwind, negative for headwind): "))
        user_drag_str = input("Include drag? (y/n): ").strip().lower()
    except ValueError:
        print("Invalid input. Please enter numbers.")
        return

    user_drag = user_drag_str == 'y'

    # Simulation for user input
    u_x_drag, u_y_drag, u_range_drag = run_simulation(user_v0, user_angle, user_v_wind, drag=True)
    u_x_nodrag, u_y_nodrag, u_range_nodrag = run_simulation(user_v0, user_angle, user_v_wind, drag=False)

    # Optimizer
    opt_angle_drag, opt_x_drag, opt_y_drag, opt_range_drag = find_optimal_angle(user_v0, user_v_wind, drag=True)
    opt_angle_nodrag, opt_x_nodrag, opt_y_nodrag, opt_range_nodrag = find_optimal_angle(user_v0, user_v_wind, drag=False)

    print(f"\n---Results---")
    print(f"User Drag Choice: {'Yes' if user_drag else 'No'}")
    print(f"[With Drag]")
    print(f"User angle: {user_angle} | Range: {u_range_drag:.2f}")
    print(f"Optimal angle: {opt_angle_drag} | Range: {opt_range_drag:.2f}")
    print(f"[Without Drag]")
    print(f"User angle: {user_angle} | Range: {u_range_nodrag:.2f}")
    print(f"Optimal angle: {opt_angle_nodrag} | Range: {opt_range_nodrag:.2f}")

    # Plotting
    plot.figure(figsize=(10, 5))
    plot.plot(u_x_drag, u_y_drag, label=f"User Angle ({user_angle}°) w/ Drag", color='blue', linewidth=2)
    plot.plot(u_x_nodrag, u_y_nodrag, label=f"User Angle ({user_angle}°) w/o Drag", color='cyan', linewidth=2)
    plot.plot(opt_x_drag, opt_y_drag, label=f"Optimal Angle ({opt_angle_drag}°) w/ Drag", color='red', linestyle='--')
    plot.plot(opt_x_nodrag, opt_y_nodrag, label=f"Optimal Angle ({opt_angle_nodrag}°) w/o Drag", color='orange', linestyle='--')
    
    plot.axhline(0, color='black', lw=1) # Ground line
    plot.title(f"Projectile Motion (v0 = {user_v0} m/s and v-wind = {user_v_wind} m/s)")
    plot.xlabel("Distance (m)")
    plot.ylabel("Height (m)")
    plot.legend()
    plot.grid(True, linestyle=':', alpha=0.6)
    plot.show()


if __name__ == "__main__":
    main()
