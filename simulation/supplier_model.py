"""
Supplier Model.
Provides lead-time distributions and reliability sampling.
"""
import numpy as np

def sample_lead_time(mean_lt: float, std_lt: float, rng = None) -> float:
    """
    Sample lead time from a Log-Normal distribution.
    
    If standard deviation is 0, returns the mean exactly.
    """
    if rng is None:
        rng = np.random.default_rng()

    if std_lt <= 0:
        return float(mean_lt)

    # LogNormal parameters matching the desired mean and std dev
    mu = np.log(mean_lt ** 2 / np.sqrt(std_lt ** 2 + mean_lt ** 2))
    sigma = np.sqrt(np.log(1 + (std_lt / mean_lt) ** 2))

    sampled = rng.lognormal(mu, sigma)
    # Ensure it's at least 0.1 days
    return max(0.1, float(sampled))

def sample_supplier_delivery(
    mean_lt: float, 
    std_lt: float, 
    reliability_pct: float,
    moq: int,
    capacity: int,
    order_qty: int,
    rng = None
) -> dict:
    """
    Simulates a supplier order execution.
    Accounts for:
    - Lead time stochasticity (LogNormal)
    - Late delivery or shipment failure based on reliability_pct
    - Capacity restrictions
    """
    if rng is None:
        rng = np.random.default_rng()

    # Check capacity limit
    final_order_qty = min(order_qty, capacity)
    
    # Sample basic lead time
    lt = sample_lead_time(mean_lt, std_lt, rng)

    # Roll for reliability (delay or failure)
    reliability_roll = rng.uniform(0, 100)
    is_delayed = reliability_roll > reliability_pct
    
    if is_delayed:
        # Delayed delivery: adds an extra penalty of 50% to 150% of the mean lead time
        delay_penalty = rng.uniform(0.5, 1.5) * mean_lt
        lt += delay_penalty

    return {
        "lead_time": lt,
        "is_delayed": is_delayed,
        "quantity_delivered": final_order_qty
    }
