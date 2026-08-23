"""
Projectile Motion Simulator
---------------------------

This program simulates projectile motion with and without
air resistance using two numerical methods:

1. Euler Method
2. Fourth-Order Runge-Kutta (RK4) Method

Features:
- Wind resistance
- Optional drag force
- Atmospheric density variation
- Optimal launch angle calculation
- Trajectory plotting

Author: Anant Shrey
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar


# =========================================================
# PHYSICAL CONSTANTS
# =========================================================

# Gravitational acceleration (m/s²)
G = 9.81

# Air properties
RHO = 1.225          # Air density at sea level (kg/m³)
MM = 0.029           # Molar mass of air (kg/mol)
R = 8.314            # Universal gas constant (J/mol·K)
T = 288.15           # Standard temperature at sea level (K)

# Projectile properties
CD = 0.47            # Drag coefficient of a sphere
RADIUS = 0.05        # Radius of projectile (m)
MASS = 0.5           # Mass of projectile (kg)

# Cross-sectional area of projectile
AREA = np.pi * (RADIUS ** 2)

# Numerical simulation timestep
DT = 0.001


# =========================================================
# ACCELERATION CALCULATION
# =========================================================

def compute_acceleration(
    velocity_x: float,
    velocity_y: float,
    wind_speed: float,
    height: float,
    drag: bool
) -> tuple[float, float]:
    """
    Computes acceleration components caused by gravity
    and air resistance.

    Parameters:
        velocity_x (float): Horizontal velocity
        velocity_y (float): Vertical velocity
        wind_speed (float): Horizontal wind speed
        height (float): Current projectile height
        drag (bool): Enables/disables drag force

    Returns:
        tuple:
            acceleration_x (float)
            acceleration_y (float)
    """

    # Relative velocity between projectile and air
    relative_velocity_x = velocity_x + wind_speed
    relative_velocity_y = velocity_y

    # Magnitude of relative velocity
    relative_velocity = np.sqrt(
        relative_velocity_x**2 +
        relative_velocity_y**2
    )

    # Atmospheric density decreases with altitude
    air_density = RHO * np.exp(
        (-MM * G * height) / (R * T)
    )

    # Drag coefficient factor
    drag_factor = (
        (air_density * CD * AREA) / (2 * MASS)
        if drag else 0.0
    )

    # Drag force acts opposite to motion
    acceleration_x = (
        -drag_factor *
        relative_velocity *
        relative_velocity_x
    )

    acceleration_y = (
        -G -
        drag_factor *
        relative_velocity *
        relative_velocity_y
    )

    return acceleration_x, acceleration_y


# =========================================================
# EULER METHOD SIMULATION
# =========================================================

def simulate_euler(
    initial_velocity: float,
    launch_angle_deg: float,
    wind_speed: float,
    drag: bool = True
) -> tuple[list[float], list[float], float]:
    """
    Simulates projectile motion using the Euler Method.

    Euler Method:
    Uses small timestep approximations to update
    velocity and position iteratively.

    Returns:
        tuple:
            x_positions
            y_positions
            final_range
    """

    # Convert angle to radians
    launch_angle_rad = np.radians(launch_angle_deg)

    # Initial velocity components
    velocity_x = initial_velocity * np.cos(launch_angle_rad)
    velocity_y = initial_velocity * np.sin(launch_angle_rad)

    # Initial position
    position_x = 0.0
    position_y = 0.0

    # Lists for plotting trajectory
    x_positions = [position_x]
    y_positions = [position_y]

    # Continue until projectile hits ground
    while position_y >= 0:

        # Compute acceleration
        acceleration_x, acceleration_y = compute_acceleration(
            velocity_x,
            velocity_y,
            wind_speed,
            position_y,
            drag
        )

        # Update velocity using Euler integration
        velocity_x += acceleration_x * DT
        velocity_y += acceleration_y * DT

        # Update position
        position_x += velocity_x * DT
        position_y += velocity_y * DT

        # Store trajectory points
        x_positions.append(position_x)
        y_positions.append(position_y)

        # Safety guard
        if len(x_positions) > 100000 or position_x < -10:
            break

    # =====================================================
    # LANDING POINT INTERPOLATION
    # =====================================================
    # The loop above can only detect that the projectile has
    # crossed y = 0 *after* it has already gone below ground,
    # so the raw final point overshoots the true landing spot
    # by up to one timestep. This introduces an O(DT) error
    # regardless of the integration method's own order of
    # accuracy. Linearly interpolating between the last
    # above-ground point and the first below-ground point
    # removes this endpoint error.
    final_range = position_x

    if len(y_positions) >= 2 and y_positions[-1] < 0:
        y_prev = y_positions[-2]
        y_last = y_positions[-1]
        x_prev = x_positions[-2]
        x_last = x_positions[-1]

        # Fraction of the final timestep at which y = 0
        frac = y_prev / (y_prev - y_last)

        landing_x = x_prev + frac * (x_last - x_prev)

        # Replace the below-ground point with the true landing point
        x_positions[-1] = landing_x
        y_positions[-1] = 0.0

        final_range = landing_x

    return x_positions, y_positions, final_range


# =========================================================
# RK4 METHOD SIMULATION
# =========================================================

def simulate_rk4(
    initial_velocity: float,
    launch_angle_deg: float,
    wind_speed: float,
    drag: bool = True
) -> tuple[list[float], list[float], float]:
    """
    Simulates projectile motion using the
    Fourth-Order Runge-Kutta (RK4) Method.

    RK4 improves numerical accuracy by computing
    weighted averages of intermediate slopes.
    """

    # Convert launch angle to radians
    launch_angle_rad = np.radians(launch_angle_deg)

    # Initial position
    position_x = 0.0
    position_y = 0.0

    # Initial velocity components
    velocity_x = initial_velocity * np.cos(launch_angle_rad)
    velocity_y = initial_velocity * np.sin(launch_angle_rad)

    # Lists for trajectory plotting
    x_positions = [position_x]
    y_positions = [position_y]

    while position_y >= 0:

        # =================================================
        # RK4 STAGE 1
        # =================================================

        k1_vx, k1_vy = compute_acceleration(
            velocity_x,
            velocity_y,
            wind_speed,
            position_y,
            drag
        )

        # =================================================
        # RK4 STAGE 2
        # =================================================

        velocity_x_2 = velocity_x + (DT / 2) * k1_vx
        velocity_y_2 = velocity_y + (DT / 2) * k1_vy

        k2_vx, k2_vy = compute_acceleration(
            velocity_x_2,
            velocity_y_2,
            wind_speed,
            position_y + (DT / 2) * velocity_y,
            drag
        )

        # =================================================
        # RK4 STAGE 3
        # =================================================

        velocity_x_3 = velocity_x + (DT / 2) * k2_vx
        velocity_y_3 = velocity_y + (DT / 2) * k2_vy

        k3_vx, k3_vy = compute_acceleration(
            velocity_x_3,
            velocity_y_3,
            wind_speed,
            position_y + (DT / 2) * velocity_y_2,
            drag
        )

        # =================================================
        # RK4 STAGE 4
        # =================================================

        velocity_x_4 = velocity_x + DT * k3_vx
        velocity_y_4 = velocity_y + DT * k3_vy

        k4_vx, k4_vy = compute_acceleration(
            velocity_x_4,
            velocity_y_4,
            wind_speed,
            position_y + DT * velocity_y_3,
            drag
        )

        # =================================================
        # UPDATE POSITION
        # =================================================

        position_x += (DT / 6) * (
            velocity_x +
            2 * velocity_x_2 +
            2 * velocity_x_3 +
            velocity_x_4
        )

        position_y += (DT / 6) * (
            velocity_y +
            2 * velocity_y_2 +
            2 * velocity_y_3 +
            velocity_y_4
        )

        # =================================================
        # UPDATE VELOCITY
        # =================================================

        velocity_x += (DT / 6) * (
            k1_vx +
            2 * k2_vx +
            2 * k3_vx +
            k4_vx
        )

        velocity_y += (DT / 6) * (
            k1_vy +
            2 * k2_vy +
            2 * k3_vy +
            k4_vy
        )

        # Store trajectory points
        x_positions.append(position_x)
        y_positions.append(position_y)

        # Safety guard
        if len(x_positions) > 100000 or position_x < -10:
            break

    # =====================================================
    # LANDING POINT INTERPOLATION
    # =====================================================
    # Same reasoning as in simulate_euler(): without this,
    # the returned range overshoots by up to one timestep,
    # capping the *empirical* convergence order at O(DT) no
    # matter how accurate the underlying integrator is.
    final_range = position_x

    if len(y_positions) >= 2 and y_positions[-1] < 0:
        y_prev = y_positions[-2]
        y_last = y_positions[-1]
        x_prev = x_positions[-2]
        x_last = x_positions[-1]

        frac = y_prev / (y_prev - y_last)
        landing_x = x_prev + frac * (x_last - x_prev)

        x_positions[-1] = landing_x
        y_positions[-1] = 0.0

        final_range = landing_x

    return x_positions, y_positions, final_range


# =========================================================
# OPTIMAL ANGLE CALCULATION
# =========================================================

def find_optimal_angle(
    simulation_function,
    initial_velocity: float,
    wind_speed: float,
    drag: bool = True
) -> tuple[float, list[float], list[float], float]:
    """
    Finds the launch angle that maximizes range.
    """

    def negative_range(angle_deg):
        _, _, projectile_range = simulation_function(
            initial_velocity,
            angle_deg,
            wind_speed,
            drag
        )
        return -projectile_range

    result = minimize_scalar(
        negative_range,
        bounds=(0, 90),
        method='bounded'
    )

    optimal_angle = result.x  # type: ignore[union-attr]  # OptimizeResult uses dynamic attrs
    optimal_x, optimal_y, optimal_range = simulation_function(
        initial_velocity,
        optimal_angle,
        wind_speed,
        drag
    )

    return (
        optimal_angle,
        optimal_x,
        optimal_y,
        optimal_range
    )


# =========================================================
# PLOTTING FUNCTION
# =========================================================

def plot_trajectories(
    user_x_drag,
    user_y_drag,
    user_x_no_drag,
    user_y_no_drag,
    optimal_x_drag,
    optimal_y_drag,
    optimal_x_no_drag,
    optimal_y_no_drag,
    user_angle,
    optimal_angle_drag,
    optimal_angle_no_drag,
    initial_velocity,
    wind_speed
):
    """
    Plots all projectile trajectories.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(
        user_x_drag,
        user_y_drag,
        label=f"User Angle ({user_angle:.2f}°) w/ Drag",
        linewidth=2,
        color='blue'
    )

    plt.plot(
        user_x_no_drag,
        user_y_no_drag,
        label=f"User Angle ({user_angle:.2f}°) w/o Drag",
        linewidth=2,
        color='red'
    )

    plt.plot(
        optimal_x_drag,
        optimal_y_drag,
        linestyle='--',
        label=f"Optimal ({optimal_angle_drag:.2f}°) w/ Drag",
        color='green'
    )

    plt.plot(
        optimal_x_no_drag,
        optimal_y_no_drag,
        linestyle='--',
        label=f"Optimal ({optimal_angle_no_drag:.2f}°) w/o Drag",
        color='yellow'
    )

    plt.axhline(lw=1, color='black')

    plt.title(
        f"Projectile Motion "
        f"(v₀ = {initial_velocity} m/s, "
        f"wind = {wind_speed} m/s)"
    )

    plt.xlabel("Distance (m)")
    plt.ylabel("Height (m)")

    plt.grid(True)
    plt.legend()

    plt.show()


# =========================================================
# MAIN PROGRAM
# =========================================================

def main():
    """
    Main program execution.
    """

    print("\nProjectile Motion Simulator")
    print("-----------------------------")
    print("1. Euler Method")
    print("2. RK4 Method")

    method_choice = input(
        "\nChoose numerical method (1 or 2): "
    )

    if method_choice == "1":
        simulation_function = simulate_euler
        method_name = "Euler Method"

    elif method_choice == "2":
        simulation_function = simulate_rk4
        method_name = "RK4 Method"

    else:
        print("Invalid choice.")
        return

    try:
        initial_velocity = float(
            input("\nEnter Initial Velocity (m/s): ")
        )

        launch_angle = float(
            input("Enter Launch Angle (degrees): ")
        )

        wind_speed = float(
            input(
                "Enter Wind Speed "
                "(positive = headwind, "
                "negative = tailwind): "
            )
        )

    except ValueError:
        print("Invalid input. Please enter numbers.")
        return

    print(f"\nUsing: {method_name}")

    # =====================================================
    # USER TRAJECTORIES
    # =====================================================

    user_x_drag, user_y_drag, user_range_drag = simulation_function(
        initial_velocity,
        launch_angle,
        wind_speed,
        drag=True
    )

    user_x_no_drag, user_y_no_drag, user_range_no_drag = simulation_function(
        initial_velocity,
        launch_angle,
        wind_speed,
        drag=False
    )

    # =====================================================
    # OPTIMAL ANGLES
    # =====================================================

    optimal_angle_drag, optimal_x_drag, optimal_y_drag, optimal_range_drag = find_optimal_angle(
        simulation_function,
        initial_velocity,
        wind_speed,
        drag=True
    )

    optimal_angle_no_drag, optimal_x_no_drag, optimal_y_no_drag, optimal_range_no_drag = find_optimal_angle(
        simulation_function,
        initial_velocity,
        wind_speed,
        drag=False
    )

    # =====================================================
    # RESULTS
    # =====================================================

    print("\n--- Results ---")

    print(
        f"[With Drag] "
        f"User {launch_angle}° → "
        f"{user_range_drag:.2f} m | "
        f"Optimal {optimal_angle_drag:.2f}° → "
        f"{optimal_range_drag:.2f} m"
    )

    print(
        f"[Without Drag] "
        f"User {launch_angle}° → "
        f"{user_range_no_drag:.2f} m | "
        f"Optimal {optimal_angle_no_drag:.2f}° → "
        f"{optimal_range_no_drag:.2f} m"
    )

    # =====================================================
    # PLOT TRAJECTORIES
    # =====================================================

    plot_trajectories(
        user_x_drag,
        user_y_drag,
        user_x_no_drag,
        user_y_no_drag,
        optimal_x_drag,
        optimal_y_drag,
        optimal_x_no_drag,
        optimal_y_no_drag,
        launch_angle,
        optimal_angle_drag,
        optimal_angle_no_drag,
        initial_velocity,
        wind_speed
    )


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()