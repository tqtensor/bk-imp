import asyncio

import numpy as np
from fastapi import APIRouter, status
from gekko import GEKKO
from jobs.inference import run as run_inference
from pydantic import BaseModel

router = APIRouter()


class ConvincingFactor(BaseModel):
    lower_bound: float = 0.55
    upper_bound: float = 0.95
    gamma: int = 100


def _expected_total_profit(x, gamma, alpha, P):
    # beta: vector of probabilities customer will accept the offer
    beta = 1 - np.exp(-gamma * (x))
    return np.sum(P * (1 - alpha)) + np.sum(beta * (alpha * P - x))


@router.post(
    path="/optimizations",
    status_code=status.HTTP_200_OK,
)
async def run(
    budget: float,
    convincing_factor: ConvincingFactor,
) -> tuple:
    """
    Runs the optimization model to determine the optimal allocation of a budget
    to minimize customer churn.

    :param float budget: The percentage of the total customer spend to allocate
    to the campaign.
    :param dict convincing_factor: A dictionary containing the upper and lower
    bounds for the churn probability, and the gamma value for customers outside
    these bounds.

    :return: A tuple containing the expected total profit with the optimal
    campaign, the expected total profit with no campaign, and the expected
    total profit with a uniform campaign.
    """
    # Predict churn probability
    test_dataset = await asyncio.gather(run_inference("./jobs/data/test.csv"))
    test_dataset = test_dataset[0]

    # Formulate the optimization problem
    # P: vector of the total customer spend
    P = test_dataset["Total Customer Spend"].values

    # alpha: vector of churn probabilities
    alpha = test_dataset["Churn Probability"].values

    # C: budget
    C = budget * P.sum()

    # N: number of customers
    N = len(P)

    # gamma: convincing factor for each customer
    gamma = np.ones(N)
    indices_gamma_eq_zero = np.union1d(
        np.where(alpha > convincing_factor.upper_bound)[0],
        np.where(alpha < convincing_factor.lower_bound)[0],
    )
    gamma[indices_gamma_eq_zero] = convincing_factor.gamma

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
<<<<<<< HEAD
    try:
        m.solve()
    except Exception as e:
        print(e)
        return (
            "Optimization failed. Please try again.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
=======
    m.solve()
>>>>>>> 388421f (feat: add docker deployment)

    # Gekko returns an array of arrays so transforming to array
    x = np.array([a[0] for a in x])

    # Evaluate the expected total profit
    expected_total_profit_no_campaign = _expected_total_profit(
        0, gamma, alpha, P
    )
    expected_total_profit_optimal = _expected_total_profit(x, gamma, alpha, P)
    expected_total_profit_uniform_campaign = _expected_total_profit(
        (C / N) * np.ones(N), gamma, alpha, P
    )
    return (
        expected_total_profit_optimal,
        expected_total_profit_no_campaign,
        expected_total_profit_uniform_campaign,
    )
