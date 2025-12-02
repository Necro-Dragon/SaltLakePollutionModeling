import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp, solve_bvp
from scipy.optimize import minimize

def solve(wind_data, historic_pm10_data):
    # P'(t) = c(\alpha + P(t))S(t) + f(t)
    t0 = 0
    tf = len(wind_data) - 1

    a = 60
    s = lambda t: wind_data[t]
    f = lambda t: 37.0 if wind_data[t] >= 18 else 0.0

    def solve_pollutant_model(c):
        def ode(t, p, c):
            return np.array([c*(a + p[0])*s(t) + f(t)])

        y0 = np.array([0])

        # solve the system
        return solve_ivp(ode, (t0, tf), y0, t_eval=np.linspace(t0, tf, 68), args=(c))

    def calculate_error(params):
        # Unpack the parameters
        sol = solve_pollutant_model(*params)

        # Find the difference between out and the data
        diff = sol.y[0] - historic_pm10_data

        # Calculate the error
        return np.linalg.norm(diff)

    result = minimize(calculate_error, (0.1))
    best_c = result.x[0]

    print(f"Found minimal error with c = {best_c}")

    sol = solve_pollutant_model(best_c)

    plt.figure(figsize=(7, 4))
    plt.plot(sol.t, historic_pm10_data, label="Data")
    plt.plot(sol.t, sol.y[0], label="Pollutant Prediction")
    plt.title("Modeling Pollutant (PM10) over time")
    plt.ylabel("ppm")
    plt.xlabel("Days since ")
    plt.legend()
    plt.show()

    return best_c


solve(wind_data, historic_pm10_data)