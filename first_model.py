'''
First Model
This model tries to capture the base inflow and outflow of PM10 from the state

'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, solve_bvp
from scipy.optimize import minimize
from data_loading_utils import get_all

def solve(wind_data, max_wind_data, historic_pm10_data, start_date):
    # P'(t) = (\alpha)(\eta)S(t) - (\beta)P(t)S(t) - (\kapa)P(t) + f(t)
    t0 = 0
    tf = min(len(wind_data), len(historic_pm10_data)) - 1

    eta = 21
    s = lambda t: wind_data[int(round(t))]
    f = lambda t: 37.0 if max_wind_data[int(round(t))] >= 18 else 0.0

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

    return best_alpha, best_beta, best_kappa

wind_data, max_wind_data, pm10_recordings, _ = get_all("2024-01-01", "2024-12-31")
best_alpha, best_beta, best_kappa = solve(wind_data, max_wind_data, pm10_recordings, "Jan. 1st 2024")

plt.show()