import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, solve_bvp
from scipy.optimize import minimize
from load_cleaned import load_windspeed_and_pm10
from datetime import datetime

def solve(wind_data, historic_pm10_data, start_date):
    # P'(t) = c(\alpha - P(t))S(t) + f(t)
    t0 = 0
    tf = min(len(wind_data), len(historic_pm10_data)) - 1

    a = 60
    s = lambda t: wind_data[int(round(t))]
    f = lambda t: 37.0 if wind_data[int(round(t))] >= 18 else 0.0

    def solve_pollutant_model(c):
        def ode(t, p, c):
            return np.array([c*(a - p[0])*s(t) + f(t)])

        y0 = np.array([historic_pm10_data[0]])

        # solve the system (evaluate at each data point)
        n_points = tf + 1  # from 0 to tf inclusive
        sol = solve_ivp(ode, (t0, tf), y0, t_eval=np.linspace(t0, tf, n_points), args=(c,), method='RK45')
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

    result = minimize(calculate_error, [0.1], bounds=[(0, None)])
    best_c = result.x[0]

    print(f"Found minimal error with c = {best_c}")

    sol = solve_pollutant_model(best_c)
    plt.figure(figsize=(7, 4))
    plt.plot(sol.t, historic_pm10_data, label="Data")
    plt.plot(sol.t, sol.y[0], label="Pollutant Prediction")
    plt.title("Modeling Pollutant (PM10) over time")
    plt.ylabel("ppm")
    plt.xlabel(f"Days since {start_date}")
    plt.legend()

    return best_c



wind_speeds, pm10_recordings = load_windspeed_and_pm10("2023-01-01", "2023-12-31")
solve(wind_speeds, pm10_recordings, "Jan. 1st 2023")
plt.show()