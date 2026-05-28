# Projectile Motion with Air Resistance

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/YOUR_REPO/blob/main/projectile_motion.ipynb)

> **Replace** `YOUR_USERNAME` and `YOUR_REPO` in the badge URL above with your actual GitHub username and repository name.

---

## Overview

A numerical simulation of projectile motion that models the effect of **aerodynamic drag** and **altitude-varying air density** on a spherical projectile. Two integration methods are implemented and compared:

| Method | File | Accuracy | Notes |
|---|---|---|---|
| Euler (1st-order) | `main_euler.py` | Lower | Faster, accumulates error over time |
| Runge-Kutta 4 (RK4) | `main_rk4.py` | Higher | Industry-standard, 4-stage per step |

Both methods support wind, drag toggling, and automatic optimal-angle finding.

---

## Physics Model

### Drag Force

$$F_d = \frac{1}{2} \rho \, v_{rel}^2 \, C_d \, A$$

where $v_{rel}$ is the velocity of the projectile **relative to the wind**.

### Altitude-Dependent Air Density (RK4 only)

The RK4 model uses the **barometric formula** to vary air density with height:

$$\rho(y) = \rho_0 \, \exp\!\left(\frac{-M \cdot g \cdot y}{R \cdot T}\right)$$

The Euler model uses a constant $\rho = \rho_0$ (sea-level density).

### Equations of Motion

$$a_x = -\frac{F_d}{m} \cdot \hat{v}_{rel,x}, \qquad a_y = -g - \frac{F_d}{m} \cdot \hat{v}_{rel,y}$$

---

## Features

- **Drag on/off** — compare ideal vs real trajectories side by side
- **Wind support** — headwind (positive) and tailwind (negative)
- **Optimal angle finder** — brute-force (Euler) and `scipy.optimize` (RK4)
- **Altitude-varying density** — physically accurate at higher trajectories (RK4)
- **Interactive Colab dashboard** — sliders for all parameters, live plots

---

## Project Structure

```
.
├── constants.py          # Shared physical constants
├── main_euler.py         # Euler method simulation + optimizer
├── main_rk4.py           # RK4 simulation + scipy optimizer
├── projectile_motion.ipynb  # Interactive Colab notebook
└── README.md
```

---

## Physical Parameters (constants.py)

| Constant | Symbol | Value | Unit |
|---|---|---|---|
| Gravitational acceleration | $g$ | 9.81 | m/s² |
| Sea-level air density | $\rho_0$ | 1.225 | kg/m³ |
| Drag coefficient (sphere) | $C_d$ | 0.47 | — |
| Projectile radius | $r$ | 0.05 | m |
| Projectile mass | $m$ | 0.5 | kg |
| Time step | $\Delta t$ | 0.001 | s |
| Molar mass of air | $M$ | 0.029 | kg/mol |
| Universal gas constant | $R$ | 8.314 | J/mol·K |
| Standard sea-level temperature | $T$ | 288.15 | K |

---

## Running Locally

**Requirements:**
```
numpy
matplotlib
scipy
```

Install with:
```bash
pip install numpy matplotlib scipy
```

**Run Euler simulation:**
```bash
python -m projectile.main_euler
```

**Run RK4 simulation:**
```bash
python -m projectile.main_rk4
```

> Both scripts prompt for initial velocity, launch angle, and wind speed in the terminal.

---

## Sample Output

```
Enter Initial Velocity (m/s): 50
Enter Launch Angle (degrees): 40
Enter Wind Speed (m/s, positive for headwind, negative for tailwind): 5

---Results---
[With Drag]
User angle: 40.0   | Range: 142.73 m
Optimal angle: 38.5 | Range: 144.91 m
[Without Drag]
User angle: 40.0   | Range: 254.81 m
Optimal angle: 45.0 | Range: 255.10 m
```

---

## Key Observations

- Drag significantly **reduces range** and **lowers the optimal launch angle** below 45°
- Headwind reduces range further and pushes the optimal angle even lower
- Tailwind increases range and raises the optimal angle slightly
- RK4 with altitude-varying density gives a slightly shorter range at high $v_0$ due to thinner air at peak height reducing drag — a physically accurate effect

---

## Acknowledgements

- Physics formulation inspired by the **Feynman Lectures on Physics**
- Numerical methods reference: *Numerical Analysis* — Burden & Faires
- Part of a high-school research paper on air resistance effects in projectile motion
