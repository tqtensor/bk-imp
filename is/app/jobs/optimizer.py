import numpy as np
import pandas as pd
from gekko import GEKKO
from xgboost import XGBClassifier


def expected_total_profit(x, gamma, alpha, P):
    # beta: vector of probabilities customer will accept the offer
    beta = 1 - np.exp(-gamma * (x))
    return np.sum(P * (1 - alpha)) + np.sum(beta * (alpha * P - x))


def run(
    budget: int,
    convincing_factor: dict,
):
    # Load test dataset
    test_dataset = pd.read_csv("./jobs/data/test.csv")

    # Load model
    model = XGBClassifier()
    model.load_model("./jobs/model/xgb_model.json")

    # Predict churn probability
    test_dataset["Churn Probability"] = model.predict_proba(
        test_dataset.drop(columns=["Total Customer Spend", "Churn?_True."])
    )[:, 1]

    # Formulate the optimization problem
    # P: vector of the total customer spend
    P = test_dataset["Total Customer Spend"].values

    # alpha: vector of churn probabilities
    alpha = test_dataset["Churn Probability"].values

    # C: budget
    C = budget

    # N: number of customers
    N = len(P)

    # gamma: convincing factor for each customer
    gamma = np.ones(N)
    indices_gamma_eq_zero = np.union1d(
        np.where(alpha > convincing_factor["upper_bound"])[0],
        np.where(alpha < convincing_factor["lower_bound"])[0],
    )
    gamma[indices_gamma_eq_zero] = convincing_factor["gamma"]

    # Create GEKKO model
    m = GEKKO(remote=False)
    m.options.SOLVER = 3  # IPOPT Solver
    m.options.IMODE = 3

    # Create array
    x = m.Array(m.Var, N)
    for i in range(N):
        x[i].value = C / N
        x[i].lower = 0
        x[i].upper = 10000000

    # Create parameter
    budget = m.Param(value=C)
    ival_eq = [m.Intermediate(x[i]) for i in range(N)]

    m.Equation(sum(ival_eq) == budget)

    beta = [1 - m.exp(-gamma[i] * x[i]) for i in range(N)]
    ival = [
        m.Intermediate(beta[i] * (alpha[i] * P[i] - x[i])) for i in range(N)
    ]
    m.Obj(-sum(ival))

    # Minimize objective
    m.solve()
    print(x)

    # Gekko returns an array of arrays so transforming to array
    x = np.array([a[0] for a in x])
    print(
        "Total spend is",
        "${:,.2f}".format(np.sum(x)),
        "compared to our budget of",
        "${:,.2f}".format(C),
    )
    print(
        "Total customer spend is",
        "${:,.2f}".format(test_dataset["Total Customer Spend"].sum()),
        "for",
        len(test_dataset),
        "customers.",
    )

    # Evaluate the expected total profit
    expected_total_profit_no_campaign = expected_total_profit(
        0, gamma, alpha, P
    )
    expected_total_profit_optimal = expected_total_profit(x, gamma, alpha, P)
    expected_total_profit_uniform_campaign = expected_total_profit(
        (C / N) * np.ones(N), gamma, alpha, P
    )
    print(
        "Expected total profit compared to no campaign:  %.0f%%"
        % (
            100
            * (
                expected_total_profit_optimal
                - expected_total_profit_no_campaign
            )
            / expected_total_profit_no_campaign
        )
    )
    print(
        "Expected total profit compared to uniform discount allocation:  %.0f%%"
        % (
            100
            * (
                expected_total_profit_optimal
                - expected_total_profit_uniform_campaign
            )
            / expected_total_profit_uniform_campaign
        )
    )


if __name__ == "__main__":
    run(
        budget=100,
        convincing_factor={
            "lower_bound": 0.55,
            "upper_bound": 0.95,
            "gamma": 100,
        },
    )
