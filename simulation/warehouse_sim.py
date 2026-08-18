"""
SimPy Discrete-Event Simulation for Warehouse and Supply Chain digital twin.
Models: Customer Demand, Reorder Checks, Purchase Orders, Supplier Delays, Replenishment, and Costs.
"""
import simpy
import numpy as np
from simulation.supplier_model import sample_lead_time

class SupplyChainSimulation:
    """
    Stochastic Discrete-Event Simulation of a warehouse replenishment loop.
    """
    def __init__(self, env: simpy.Environment, config: dict, seed: int = 42):
        self.env = env
        self.config = config
        self.rng = np.random.default_rng(seed)

        # Configurable Parameters (with fallbacks)
        self.initial_inventory = float(config.get("initial_inventory", 100.0))
        self.rop = float(config.get("rop", 50.0))
        self.safety_stock = float(config.get("safety_stock", 20.0))
        self.recommended_qty = int(config.get("recommended_qty", 100))
        
        # Demand distribution (P10/P50/P90)
        self.p10_demand = float(config.get("p10_demand", 8.0))
        self.p50_demand = float(config.get("p50_demand", 12.0))
        self.p90_demand = float(config.get("p90_demand", 16.0))
        
        # Supplier lead time parameters
        self.mean_lead_time = float(config.get("mean_lead_time", 3.0))
        self.lead_time_std = float(config.get("lead_time_std", 0.5))
        self.supplier_reliability = float(config.get("supplier_reliability", 0.95)) # 0.0 to 1.0
        
        # Costs
        self.holding_cost_per_unit_day = float(config.get("holding_cost_per_unit_day", 0.05))
        self.shortage_cost_per_unit_day = float(config.get("shortage_cost_per_unit_day", 1.0))
        self.order_cost = float(config.get("order_cost", 50.0))

        # State tracking variables
        self.inventory = self.initial_inventory
        self.in_transit = 0.0
        self.inventory_history = [{"time": 0.0, "inventory": self.inventory}]
        self.stockout_events = []
        self.po_history = []
        self.cost_tracker = {"holding": 0.0, "shortage": 0.0, "ordering": 0.0}

    def customer_demand(self):
        """Generate customer demand daily and consume stock."""
        while True:
            # Sample demand using normal distribution fitted on quantiles
            std_demand = (self.p90_demand - self.p10_demand) / 4.0
            std_demand = max(0.1, std_demand)
            
            daily_demand = self.rng.normal(self.p50_demand, std_demand)
            daily_demand = max(0.0, daily_demand)

            # Try to fulfill demand
            if self.inventory >= daily_demand:
                self.inventory -= daily_demand
            else:
                # Stockout occurred
                shortage = daily_demand - self.inventory
                self.stockout_events.append({
                    "time": self.env.now,
                    "demand": daily_demand,
                    "available": self.inventory,
                    "shortage": shortage
                })
                self.inventory = 0.0
                self.cost_tracker["shortage"] += shortage * self.shortage_cost_per_unit_day

            # Log history
            self.inventory_history.append({
                "time": self.env.now,
                "inventory": self.inventory
            })

            # Wait 1 day (time unit is days)
            yield self.env.timeout(1)

    def inventory_manager(self):
        """Monitor inventory levels and trigger purchase orders."""
        while True:
            # Check net inventory (inventory + in_transit) to avoid placing redundant orders
            if (self.inventory + self.in_transit) < self.rop:
                # Order size
                order_qty = self.recommended_qty
                # Place order asynchronously (does not block inventory manager loop)
                self.env.process(self.place_order(order_qty))
            
            yield self.env.timeout(1)  # Check daily

    def place_order(self, order_qty: int):
        """Simulate the replenishment pipeline."""
        order_time = self.env.now
        self.in_transit += order_qty
        self.cost_tracker["ordering"] += self.order_cost

        # Sample stochastic lead time
        lead_time = sample_lead_time(self.mean_lead_time, self.lead_time_std, self.rng)
        
        # Model supplier reliability delay
        reliability_roll = self.rng.uniform(0.0, 1.0)
        is_delayed = reliability_roll > self.supplier_reliability
        if is_delayed:
            lead_time += self.rng.uniform(0.5, 1.5) * self.mean_lead_time

        # Wait for delivery lead time
        yield self.env.timeout(lead_time)

        # Replenish stock
        self.inventory += order_qty
        self.in_transit -= order_qty
        
        self.po_history.append({
            "order_time": order_time,
            "delivery_time": self.env.now,
            "order_qty": order_qty,
            "lead_time": lead_time,
            "is_delayed": is_delayed
        })

        self.inventory_history.append({
            "time": self.env.now,
            "inventory": self.inventory
        })

    def run(self, horizon_days: int):
        """Execute the processes in SimPy."""
        # Calculate holding costs per day
        def holding_cost_recorder():
            while True:
                self.cost_tracker["holding"] += self.inventory * self.holding_cost_per_unit_day
                yield self.env.timeout(1)

        self.env.process(self.customer_demand())
        self.env.process(self.inventory_manager())
        self.env.process(holding_cost_recorder())
        
        self.env.run(until=horizon_days)
        return self.get_results(horizon_days)

    def get_results(self, horizon_days: int) -> dict:
        """Aggregate performance metrics from simulation run."""
        inv_levels = [h["inventory"] for h in self.inventory_history]
        avg_inv = np.mean(inv_levels) if inv_levels else 0.0
        max_inv = max(inv_levels) if inv_levels else 0.0
        min_inv = min(inv_levels) if inv_levels else 0.0

        total_cost = sum(self.cost_tracker.values())
        
        # Service level achieved: fraction of days without stockouts
        stockout_days = len(self.stockout_events)
        service_level_achieved = max(0.0, 1.0 - (stockout_days / horizon_days))

        return {
            "avg_inventory": round(float(avg_inv), 2),
            "max_inventory": round(float(max_inv), 2),
            "min_inventory": round(float(min_inv), 2),
            "stockout_events": len(self.stockout_events),
            "stockout_probability": round(stockout_days / horizon_days, 4),
            "service_level_achieved": round(float(service_level_achieved), 4),
            "total_cost": round(float(total_cost), 2),
            "holding_cost": round(self.cost_tracker["holding"], 2),
            "shortage_cost": round(self.cost_tracker["shortage"], 2),
            "ordering_cost": round(self.cost_tracker["ordering"], 2),
            "po_history": self.po_history,
            "inventory_history": self.inventory_history
        }
