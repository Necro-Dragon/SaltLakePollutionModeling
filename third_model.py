'''
Third model iteration (TBD)
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, solve_bvp
from scipy.optimize import minimize
from data_loading_utils import load_windspeed_and_pm10, load_surface_area, get_windspeed_pm10_sa
from datetime import datetime
import calendar

def solve(wind_data, max_wind_data, historic_pm10_data, surface_area_data, healthy_lake_surface_area, start_date):
    # P'(t) = c(\alpha)S(t) - kP(t))S(t) + f(t)
    t0 = 0
    tf = min(len(wind_data), len(historic_pm10_data)) - 1

    a = 20
    s = lambda t: wind_data[int(round(t))]

    density_of_arsenic_in_lake =  5.73
    mass_of_arsenic = 74.92
    concentration = 2/100

    def f(t):
        max_wind_speed_t = max_wind_data[t]
        if max_wind_speed_t >= 18:
            exposed_surface_area = healthy_lake_surface_area - surface_area_data[t]
            return (concentration*density_of_arsenic_in_lake*exposed_surface_area*max_wind_speed_t)/mass_of_arsenic
        else:
            return 0


    def solve_pollutant_model(c, k):
        def ode(t, p, c, k):
            return np.array([(k*a - c*p[0])*s(t) + f(t)])

        y0 = np.array([historic_pm10_data[0]])

        # solve the system (evaluate at each data point)
        n_points = tf + 1  # from 0 to tf inclusive
        sol = solve_ivp(ode, (t0, tf), y0, t_eval=np.linspace(t0, tf, n_points), args=(c, k), method='RK45')
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

    result = minimize(calculate_error, [0.1, 0.1], bounds=[(0, None)])
    best_c = result.x[0]
    best_k = result.x[1]

    print(f"Found minimal error with c = {best_c}")
    print(f"Found minimal error with k = {best_k}")

    sol = solve_pollutant_model(best_c, best_k)
    plt.figure(figsize=(7, 4))
    plt.plot(sol.t, historic_pm10_data, label="Data")
    plt.plot(sol.t, sol.y[0], label="Pollutant Prediction")
    plt.title("Modeling Pollutant (PM10) over time")
    plt.ylabel("ppm")
    plt.xlabel(f"Days since {start_date}")
    plt.legend()

    return best_c, best_k

wind_data, pm10_recordings, surface_area_data = get_windspeed_pm10_sa("1999-01-01", "2025-12-31")

solve(wind_speeds)