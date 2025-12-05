'''
Third Model

We are exploring the pollution added by the lake as a quadratic relation with wind
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, solve_bvp
from scipy.optimize import minimize
from data_loading_utils import get_all

def solve(wind_data, max_wind_data, historic_pm10_data, surface_area_data, healthy_lake_surface_area, start_date):
    # P'(t) = c(\alpha)S(t) - dP(t))S(t) + f(t)
    t0 = 0
    tf = min(len(wind_data), len(historic_pm10_data)) - 1

    eta = 20
    s = lambda t: wind_data[int(round(t))]

    atomic_density_of_arsenic =  5.73
    mass_of_arsenic = 74.92159
    concentration = 0.18 * 1e-6

    def f(t):
        max_wind_speed_t = max_wind_data[int(round(t))]
        if max_wind_speed_t >= 18:
            exposed_surface_area = healthy_lake_surface_area - surface_area_data[int(round(t))]
            return ((concentration*atomic_density_of_arsenic*exposed_surface_area)/mass_of_arsenic)*max_wind_speed_t**2
        else:
            return 0


    def solve_pollutant_model(alpha, beta, kappa):
        def ode(t, p, alpha, beta, kappa):
            return np.array([alpha*eta*s(t) - beta*p[0]*s(t) - kappa*p[0] + f(t)])

        y0 = np.array([historic_pm10_data[0]])

        # solve the system (evaluate at each data point)
        n_points = tf + 1  # from 0 to tf inclusive
        sol = solve_ivp(ode, (t0, tf), y0, t_eval=np.linspace(t0, tf, n_points), args=(alpha, beta, kappa), method='RK45')
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

    result = minimize(calculate_error, [0.1, 0.1, 0.1], bounds=[(0, None)])
    best_alpha = result.x[0]
    best_beta = result.x[1]
    best_kappa = result.x[2]

    print(f"Found minimal error with alpha = {best_alpha}")
    print(f"Found minimal error with beta = {best_beta}")
    print(f"Found minimal error with kappa = {best_kappa}")

    sol = solve_pollutant_model(best_alpha, best_beta, best_kappa)
    plt.figure(figsize=(7, 4))
    plt.plot(sol.t, historic_pm10_data, label="Data")
    plt.plot(sol.t, sol.y[0], label="Pollutant Prediction")
    plt.title("Modeling Pollutant (PM10) over time")
    plt.ylabel("ppm")
    plt.xlabel(f"Days since {start_date}")
    plt.legend()
    plt.show()

    return best_alpha, best_beta, best_kappa

wind_data, max_wind_data, pm10_recordings, surface_area_data = get_all("2024-01-01", "2024-12-31")

solve(wind_data, max_wind_data, pm10_recordings, surface_area_data, 31804934478, "Jan 1. 2024")