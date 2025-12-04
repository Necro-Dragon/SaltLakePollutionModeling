'''
Third Model

We are exploring the pollution added by the lake as a quadratic relation with wind
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, solve_bvp
from scipy.optimize import minimize
from data_loading_utils import get_all
from datetime import datetime
import calendar

def solve(wind_data, max_wind_data, historic_pm10_data, surface_area_data, healthy_lake_surface_area, start_date):
    # P'(t) = c(\alpha)S(t) - dP(t))S(t) + f(t)
    t0 = 0
    tf = min(len(wind_data), len(historic_pm10_data)) - 1

    a = 20
    s = lambda t: wind_data[int(round(t))]

    density_of_arsenic_in_lake =  5.73
    mass_of_arsenic = 74.92
    concentration = 0.18 * 1e-6

    def f(t):
        max_wind_speed_t = max_wind_data[int(round(t))]
        if max_wind_speed_t >= 18:
            exposed_surface_area = healthy_lake_surface_area - surface_area_data[int(round(t))]
            return ((concentration*density_of_arsenic_in_lake*exposed_surface_area)/mass_of_arsenic)*max_wind_speed_t**2
        else:
            return 0


    def solve_pollutant_model(c, d, kapa):
        def ode(t, p, c, d, kapa):
            return np.array([(d*a - c*p[0])*s(t) + f(t) - kapa])

        y0 = np.array([historic_pm10_data[0]])

        # solve the system (evaluate at each data point)
        n_points = tf + 1  # from 0 to tf inclusive
        sol = solve_ivp(ode, (t0, tf), y0, t_eval=np.linspace(t0, tf, n_points), args=(c, d, kapa), method='RK45')
        if not sol.success:
            print(f"Warning: solve_ivp failed with message: {sol.message}")
        return sol

    def calculate_error(params):
        # Unpack the parameters
        sol = solve_pollutant_model(*params)

        # Find the difference between out and the data
        diff = sol.y[0] - historic_pm10_data[:len(sol.y[0])]

        # Calculate the error
        return np.linalg.norm(diff)

    result = minimize(calculate_error, [0.1, 0.1, 15], bounds=[(0, None)])
    best_c = result.x[0]
    best_d = result.x[1]
    best_kapa = result.x[2]

    print(f"Found minimal error with c = {best_c}")
    print(f"Found minimal error with d = {best_d}")
    print(f"Found minimal error with kapa = {best_kapa}")

    sol = solve_pollutant_model(best_c, best_d, best_kapa)
    plt.figure(figsize=(7, 4))
    plt.plot(sol.t, historic_pm10_data, label="Data")
    plt.plot(sol.t, sol.y[0], label="Pollutant Prediction")
    plt.title("Modeling Pollutant (PM10) over time")
    plt.ylabel("ppm")
    plt.xlabel(f"Days since {start_date}")
    plt.legend()
    plt.show()

    return best_c, best_d, best_kapa

wind_data, max_wind_data, pm10_recordings, surface_area_data = get_all("2024-01-01", "2024-12-31")

solve(wind_data, max_wind_data, pm10_recordings, surface_area_data, np.max(surface_area_data), "Jan 1. 2024")