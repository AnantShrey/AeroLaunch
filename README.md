# ▶ Interactive Dashboard (Google Colab)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](YOUR_NOTEBOOK_LINK_HERE)

---

# AeroLaunch — Advanced Projectile Motion Simulator

AeroLaunch is a computational physics simulator that models projectile motion under realistic atmospheric conditions.

Unlike ideal textbook projectile equations, AeroLaunch includes:

* Air resistance (drag force)
* Wind effects
* Atmospheric density variation
* Numerical integration methods
* Optimal launch-angle calculation
* Interactive dashboard visualizations

The simulator compares the performance of:

1. Euler Method
2. Fourth-Order Runge-Kutta (RK4) Method

---

# Features

## Physics Features

* Gravity simulation
* Aerodynamic drag
* Headwind/tailwind support
* Altitude-dependent air density
* Optimal trajectory calculation

## Numerical Methods

### Euler Method

Simple first-order numerical integration.

### RK4 Method

Higher-accuracy fourth-order numerical integration.

## Interactive Dashboard

The Jupyter Notebook includes:

* Interactive sliders
* Real-time graph updates
* Numerical method selection
* Wind control
* Launch angle optimization

---

# Mathematical Model

Projectile motion is governed by:

## Gravity

a_y=-g

where:

* ( g = 9.81 , \text{m/s}^2 )

---

## Drag Force

F_d=\frac{1}{2}\rho v_{rel}^2 C_d A

where:

* ( \rho ) = Air density
* ( v_{rel} ) = Relative velocity
* ( C_d ) = Drag coefficient
* ( A ) = Cross-sectional area

---

## Relative Velocity

v_{rel}=\sqrt{(v_x+v_{wind})^2+v_y^2}

---

## Atmospheric Density Variation

The RK4 simulation models atmospheric density using:

\rho(y)=\rho_0 e^{-\frac{MMgy}{RT}}

This makes the simulation more realistic at higher altitudes.

---

# Numerical Methods

## Euler Method

Euler integration updates velocity and position using:

v_{new}=v_{old}+a\Delta t

It is computationally simple but less accurate.

---

## RK4 Method

The Fourth-Order Runge-Kutta method estimates multiple intermediate slopes to improve numerical accuracy.

RK4 generally produces:

* smoother trajectories
* better energy behavior
* improved accuracy for long simulations

---

# Installation

## Requirements

Install Python packages:

```bash
pip install numpy matplotlib scipy ipywidgets
```

---

# Running Locally

## Python Script

```bash
python main.py
```

The program will:

1. Ask for simulation parameters
2. Ask for numerical method selection
3. Display trajectory plots
4. Compute optimal launch angle

---

# Running the Interactive Dashboard

Open:

```plaintext
AeroLaunch_with_Interactive_Dashboard.ipynb
```

Run all notebook cells.

The dashboard allows real-time parameter adjustment using sliders.

---

# Interactive Dashboard Controls

| Control          | Description         |
| ---------------- | ------------------- |
| Initial Velocity | Launch speed        |
| Launch Angle     | Angle of projection |
| Wind Speed       | Headwind/tailwind   |
| Numerical Method | Euler or RK4        |
| Drag Toggle      | Enable/disable drag |

---

# Project Structure

```plaintext
AeroLaunch/
│
├── main.py
├── AeroLaunch_with_Interactive_Dashboard.ipynb
├── README.md
├── graph_output.png
└── requirements.txt
```

---

# Future Improvements

Potential future upgrades include:

* Magnus effect (spin)
* Variable launch height
* 3D projectile motion
* Real-time animation
* Multiple projectile types
* GPU acceleration

---

# Educational Value

This project demonstrates concepts from:

* Physics
* Numerical Methods
* Computational Simulation
* Optimization
* Data Visualization
* Scientific Computing

---

# Author

Anant Shrey
