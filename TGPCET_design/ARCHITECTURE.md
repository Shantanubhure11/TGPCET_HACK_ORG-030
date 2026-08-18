# Technical Architecture Document
## AI-Powered Predictive Supply Chain Digital Twin

**Version:** 1.0  
**Date:** August 2026  
**Project:** TGPCET Hackathon 2026  
**Repository:** https://github.com/Shantanubhure11/TGPCET_HACK_ORG-030.git

---

## 1. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                               │
│  Sales DB | Promotions | Prices | IoT Sensors | RFID | Suppliers   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   DATA INGESTION LAYER       │
            │  MQTT | REST API | Batch     │
            └──────────────┬───────────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │   PostgreSQL Database        │
            │  Sales | Inventory | Supplier│
            │  PO | GRN | IoT Telemetry   │
            └────────┬───────────┬─────────┘
                     │           │
        ┌────────────┘           └─────────────┐
        ▼                                       ▼
┌──────────────────────┐            ┌──────────────────────┐
│  AI/ML FORECASTING   │            │   ERP CORE ENGINE    │
│                      │            │                      │
│ Feature Engineering  │            │ Inventory Ledger     │
│ LightGBM Quantile    │            │ Purchase Orders      │
│ P10/P50/P90          │            │ GRN / Stock Mgmt     │
│ Model Registry       │            │ Sales Orders         │
└──────────┬───────────┘            └──────────┬───────────┘
           │                                    │
           └──────────────┬─────────────────────┘
                          ▼
         ┌────────────────────────────────────┐
         │  SUPPLY CHAIN DIGITAL TWIN        │
         │  (SimPy Discrete-Event Sim)        │
         │                                    │
         │ Demand Variability                 │
         │ Lead-Time Variability              │
         │ Warehouse Operations               │
         │ Supplier Behavior                  │
         └────────────────┬───────────────────┘
                          ▼
         ┌────────────────────────────────────┐
         │  INVENTORY OPTIMIZATION            │
         │                                    │
         │ Dynamic Safety Stock               │
         │ Dynamic ROP Calculation            │
         │ Stock-out Probability              │
         │ Overstock Detection                │
         │ PO Recommendation Engine           │
         └────────────────┬───────────────────┘
                          ▼
        ┌─────────────────────────────────────┐
        │   DECISION & ALERT ENGINES          │
        │                                     │
        │ PO Recommendations                  │
        │ Stock-out Alerts                    │
        │ Overstock Warnings                  │
        │ IoT Discrepancy Flags               │
        └─────────────────┬───────────────────┘
                          ▼
        ┌──────────────────────────────────────┐
        │   STREAMLIT INTERACTIVE DASHBOARD   │
        │                                      │
        │ Page 1: Executive Overview           │
        │ Page 2: Demand Forecast              │
        │ Page 3: Inventory Health             │
        │ Page 4: Supply Chain Simulation      │
        │ Page 5: What-If Scenarios            │
        │ Page 6: Procurement Recommendations │
        └──────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Layered Design Pattern

```
┌────────────────────────────────────────────────┐
│           Presentation Layer                   │
│   Streamlit Dashboard (Frontend - Shantanu)    │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│         API Layer (Business Logic)              │
│  FastAPI Backend (Sanika & Khushi)             │
│                                                 │
│  Routes:                                        │
│  /api/forecast/*         (Demand forecasting)   │
│  /api/inventory/*        (Inventory management) │
│  /api/suppliers/*        (Supplier data)        │
│  /api/purchases/*        (PO management)        │
│  /api/simulation/*       (Digital twin)         │
│  /api/alerts/*           (Alert engine)         │
│  /api/iot/*              (Telemetry processing) │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│       Service Layer (Domain Logic)              │
│                                                 │
│  ML Services:                                   │
│  - demand_forecasting_service.py                │
│  - model_registry.py                            │
│                                                 │
│  Inventory Services:                            │
│  - safety_stock_service.py                      │
│  - reorder_point_service.py                     │
│  - risk_engine.py                               │
│                                                 │
│  Supply Chain Services:                         │
│  - digital_twin_service.py                      │
│  - monte_carlo_service.py                       │
│  - scenario_service.py                          │
│                                                 │
│  ERP Services:                                  │
│  - inventory_ledger_service.py                  │
│  - purchase_order_service.py                    │
│                                                 │
│  IoT Services:                                  │
│  - mqtt_listener.py                             │
│  - telemetry_processor.py                       │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│      Data Access Layer (Database ORM)           │
│  SQLAlchemy Models & Repository Pattern         │
│                                                 │
│  - models.py (Entity definitions)               │
│  - database.py (Connection & sessions)          │
│  - repositories/ (CRUD operations)              │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│         Database Layer                          │
│  PostgreSQL (Production) / SQLite (Dev)        │
└─────────────────────────────────────────────────┘

External Systems (Async):
- MQTT Broker (Telemetry ingestion)
- Joblib Model Store (Serialized models)
```

---

## 3. Database Schema

### 3.1 ER Diagram (Conceptual)

```
┌─────────────────────┐       ┌──────────────────┐
│   ITEMS (SKU)       │       │   SUPPLIERS      │
├─────────────────────┤       ├──────────────────┤
│ sku_id (PK)         │───┐   │ supplier_id (PK) │
│ name                │   │   │ name             │
│ category            │   │   │ avg_lead_time    │
│ unit                │   │   │ lead_time_std    │
│ unit_cost           │   │   │ reliability_pct  │
│ selling_price       │   │   │ moq              │
│ supplier_id (FK)    │───┼──→│ created_at       │
│ created_at          │   │   │ updated_at       │
│ updated_at          │   │   └──────────────────┘
└─────────────────────┘   │
                          │
┌──────────────────────┐  │   ┌──────────────────┐
│  WAREHOUSES          │  │   │  INVENTORY       │
├──────────────────────┤  │   ├──────────────────┤
│ warehouse_id (PK)    │  │   │ inventory_id (PK)│
│ name                 │  │   │ sku_id (FK)      │
│ location             │  │   │ warehouse_id(FK) │
│ capacity             │  │   │ physical_stock   │
│ created_at           │  │   │ allocated_stock  │
│ updated_at           │  │   │ available_stock  │
└──────────────────────┘  │   │ safety_stock     │
                          │   │ rop              │
                          │   │ last_counted_at  │
                          │   │ created_at       │
                          │   │ updated_at       │
                          │   └──────────────────┘
                          │
        ┌─────────────────┴────────────────┐
        │                                  │
┌───────▼──────────────────┐   ┌──────────▼────────────┐
│  PURCHASE_ORDERS         │   │  GOODS_RECEIVED_NOTES│
├──────────────────────────┤   ├──────────────────────┤
│ po_id (PK)               │   │ grn_id (PK)          │
│ po_number (UNIQUE)       │   │ po_id (FK)           │
│ supplier_id (FK)         │   │ received_qty         │
│ sku_id (FK)              │   │ received_date        │
│ order_qty                │───┼→ discrepancy_qty    │
│ order_date               │   │ notes                │
│ expected_delivery        │   │ created_at           │
│ actual_delivery          │   │ updated_at           │
│ status                   │   └──────────────────────┘
│ (PENDING/DELIVERED)      │
│ created_at               │
│ updated_at               │
└──────────────────────────┘

┌──────────────────────────┐   ┌──────────────────────┐
│  SALES_ORDERS            │   │  INVENTORY_LEDGER    │
├──────────────────────────┤   ├──────────────────────┤
│ sales_order_id (PK)      │   │ ledger_id (PK)       │
│ sku_id (FK)              │   │ sku_id (FK)          │
│ warehouse_id (FK)        │   │ warehouse_id (FK)    │
│ order_qty                │   │ transaction_type     │
│ order_date               │   │ (PO/GRN/SALES/IoT)   │
│ created_at               │   │ reference_id         │
│ updated_at               │   │ qty_change           │
└──────────────────────────┘   │ previous_balance     │
                                │ new_balance          │
                                │ timestamp            │
                                │ user_id              │
                                │ notes                │
                                └──────────────────────┘

┌────────────────────────────────────────┐
│  SENSOR_LOGS (IoT Telemetry)           │
├────────────────────────────────────────┤
│ log_id (PK)                            │
│ sensor_id                              │
│ sku_id (FK)                            │
│ measured_weight_grams                  │
│ unit_weight_grams                      │
│ calculated_quantity                    │
│ erp_quantity (at time of measurement)  │
│ discrepancy_qty                        │
│ discrepancy_pct                        │
│ alert_flag                             │
│ timestamp                              │
│ location                               │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  DEMAND_FORECAST (Model Output Cache)  │
├────────────────────────────────────────┤
│ forecast_id (PK)                       │
│ sku_id (FK)                            │
│ forecast_date                          │
│ forecast_horizon (7/14/30/60/90)       │
│ p10_demand                             │
│ p50_demand                             │
│ p90_demand                             │
│ model_version                          │
│ wape_score                             │
│ created_at                             │
└────────────────────────────────────────┘
```

### 3.2 Key Tables Details

#### ITEMS
```sql
CREATE TABLE items (
    sku_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    unit VARCHAR(20),
    unit_cost DECIMAL(12,2),
    selling_price DECIMAL(12,2),
    supplier_id VARCHAR(20),
    moq INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
```

#### INVENTORY
```sql
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    sku_id VARCHAR(20) NOT NULL,
    warehouse_id VARCHAR(20) NOT NULL,
    physical_stock DECIMAL(10,2) DEFAULT 0,
    allocated_stock DECIMAL(10,2) DEFAULT 0,
    available_stock DECIMAL(10,2) GENERATED ALWAYS AS (physical_stock - allocated_stock),
    safety_stock DECIMAL(10,2) DEFAULT 0,
    rop DECIMAL(10,2) DEFAULT 0,
    last_counted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sku_id, warehouse_id),
    FOREIGN KEY (sku_id) REFERENCES items(sku_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    INDEX idx_sku_warehouse (sku_id, warehouse_id),
    INDEX idx_available_stock (available_stock)
);
```

#### INVENTORY_LEDGER (Immutable Audit Trail)
```sql
CREATE TABLE inventory_ledger (
    ledger_id SERIAL PRIMARY KEY,
    sku_id VARCHAR(20) NOT NULL,
    warehouse_id VARCHAR(20),
    transaction_type ENUM('PO', 'GRN', 'SALES', 'IoT_ADJUSTMENT', 'MANUAL'),
    reference_id VARCHAR(50),
    qty_change DECIMAL(10,2) NOT NULL,
    previous_balance DECIMAL(10,2),
    new_balance DECIMAL(10,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(50),
    notes TEXT,
    FOREIGN KEY (sku_id) REFERENCES items(sku_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    INDEX idx_sku_timestamp (sku_id, timestamp),
    INDEX idx_transaction_type (transaction_type, timestamp)
);
```

#### PURCHASE_ORDERS
```sql
CREATE TABLE purchase_orders (
    po_id SERIAL PRIMARY KEY,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id VARCHAR(20) NOT NULL,
    sku_id VARCHAR(20) NOT NULL,
    order_qty DECIMAL(10,2) NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery DATE,
    actual_delivery DATE,
    status ENUM('PENDING', 'CONFIRMED', 'DELIVERED', 'CANCELLED') DEFAULT 'PENDING',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (sku_id) REFERENCES items(sku_id),
    INDEX idx_supplier (supplier_id),
    INDEX idx_status (status),
    INDEX idx_expected_delivery (expected_delivery)
);
```

#### SENSOR_LOGS (IoT)
```sql
CREATE TABLE sensor_logs (
    log_id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    sku_id VARCHAR(20),
    measured_weight_grams DECIMAL(10,2),
    unit_weight_grams DECIMAL(10,2),
    calculated_quantity DECIMAL(10,2),
    erp_quantity_at_time DECIMAL(10,2),
    discrepancy_qty DECIMAL(10,2),
    discrepancy_pct DECIMAL(5,2),
    alert_flag BOOLEAN DEFAULT FALSE,
    alert_level ENUM('INFO', 'WARNING', 'CRITICAL'),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(100),
    FOREIGN KEY (sku_id) REFERENCES items(sku_id),
    INDEX idx_sensor_timestamp (sensor_id, timestamp),
    INDEX idx_alert_flag (alert_flag, timestamp),
    INDEX idx_discrepancy_pct (discrepancy_pct)
);
```

---

## 4. API Specification

### 4.1 FastAPI Routes (Sanika & Khushi)

#### Forecast Endpoints
```python
# GET /api/forecast/demand?sku_id=SKU-9902&horizon=30&days_back=365
# Returns: {
#   "sku_id": "SKU-9902",
#   "forecast_date": "2026-08-18",
#   "horizon": 30,
#   "forecast": [
#     {"date": "2026-08-19", "p10": 100, "p50": 120, "p90": 150, "actual": null},
#     ...
#   ],
#   "model_metrics": {"wape": 0.18, "rmse": 15.2}
# }

# POST /api/forecast/retrain
# Body: {"sku_ids": ["SKU-9902", "SKU-1234"], "lookback_days": 365}
# Returns: Training job status

# GET /api/forecast/status?job_id=job-12345
# Returns: Job progress and model performance
```

#### Inventory Endpoints
```python
# GET /api/inventory/current?sku_id=SKU-9902&warehouse_id=WH-01
# Returns: {
#   "sku_id": "SKU-9902",
#   "warehouse_id": "WH-01",
#   "physical_stock": 120,
#   "allocated_stock": 50,
#   "available_stock": 70,
#   "safety_stock": 100,
#   "rop": 200,
#   "days_of_inventory": 8.5,
#   "stock_status": "YELLOW",  # GREEN/YELLOW/RED
#   "updated_at": "2026-08-18T10:30:00Z"
# }

# GET /api/inventory/ledger?sku_id=SKU-9902&limit=100&offset=0
# Returns: Paginated inventory transaction history

# POST /api/inventory/adjust
# Body: {
#   "sku_id": "SKU-9902",
#   "warehouse_id": "WH-01",
#   "qty_change": -10,
#   "reason": "Physical count discrepancy",
#   "user_id": "alice@company.com"
# }
```

#### Supplier Endpoints
```python
# GET /api/suppliers?limit=50&offset=0
# Returns: List of suppliers with performance metrics

# GET /api/suppliers/{supplier_id}/performance
# Returns: {
#   "supplier_id": "SUP-004",
#   "name": "Rapid Supply Co.",
#   "on_time_delivery_pct": 92.5,
#   "avg_lead_time_days": 3.2,
#   "lead_time_std": 0.8,
#   "last_30_days_orders": 12,
#   "moq": 100
# }
```

#### Purchase Order Endpoints
```python
# GET /api/purchases/recommendations?service_level=95
# Returns: [
#   {
#     "recommendation_id": "rec-12345",
#     "sku_id": "SKU-9902",
#     "supplier_id": "SUP-004",
#     "recommended_qty": 500,
#     "current_stock": 120,
#     "rop": 200,
#     "stockout_probability": 0.82,
#     "projected_stockout_date": "2026-08-25",
#     "reason": "Projected inventory falls below ROP",
#     "urgency": "HIGH",
#     "estimated_cost": 2500.00
#   }
# ]

# POST /api/purchases/create
# Body: {"sku_id", "supplier_id", "qty", "user_id"}
# Returns: {"po_number", "po_id", "status"}

# GET /api/purchases/po/{po_id}
# GET /api/purchases/pending
```

#### Simulation Endpoints
```python
# POST /api/simulation/run
# Body: {
#   "scenario_name": "baseline",
#   "sku_id": "SKU-9902",
#   "lead_time_mean": 3,
#   "lead_time_std": 0.5,
#   "demand_multiplier": 1.0,
#   "supplier_reliability_pct": 95,
#   "service_level": 95,
#   "num_runs": 100,
#   "horizon_days": 30
# }
# Returns: {
#   "simulation_id": "sim-12345",
#   "status": "RUNNING",
#   "job_id": "job-67890"
# }

# GET /api/simulation/results/{simulation_id}
# Returns: {
#   "simulation_id": "sim-12345",
#   "status": "COMPLETED",
#   "results": {
#     "avg_inventory": 250,
#     "max_inventory": 800,
#     "min_inventory": 0,
#     "stockout_events": 8,
#     "stockout_probability": 0.08,
#     "holding_cost": 15000,
#     "shortage_cost": 2000,
#     "total_cost": 17000,
#     "service_level_achieved": 0.92
#   }
# }

# POST /api/simulation/compare
# Body: {
#   "baseline_scenario_id": "sim-12345",
#   "modified_scenario_id": "sim-67890",
#   "parameters_changed": ["lead_time_mean", "demand_multiplier"]
# }
# Returns: Side-by-side comparison
```

#### Alert Endpoints
```python
# GET /api/alerts/active?alert_type=STOCKOUT
# Returns: List of active alerts with severity

# GET /api/alerts/iot-discrepancies?limit=50
# Returns: Recent IoT vs ERP discrepancies

# POST /api/alerts/acknowledge
# Body: {"alert_id": "alert-12345", "user_id": "alice@company.com", "notes": "Physical count scheduled"}
```

---

## 5. ML/AI Pipeline (Khushi Leads)

### 5.1 Data Flow

```
Raw Sales Data (PostgreSQL)
    ↓
Data Loader (data_loader.py)
    ↓
Feature Engineering (feature_engineering.py)
    │
    ├─ Temporal Features (DOW, Month, Quarter, Holiday)
    ├─ Lag Features (1, 7, 14, 30 days)
    ├─ Rolling Aggregates (mean/std 7, 14, 30 days)
    ├─ Commercial Features (Price, Discount, Promotion)
    └─ Inventory Features (Stock-out vs Zero-Demand)
    ↓
Training Data
    ↓
Model Training (train_forecaster.py)
    │
    ├─ Train/Validation Split (80/20)
    ├─ LightGBM Quantile Regression
    │  ├─ Quantile: 0.1 (P10)
    │  ├─ Quantile: 0.5 (P50)
    │  └─ Quantile: 0.9 (P90)
    └─ Cross-validation
    ↓
Model Evaluation (evaluate.py)
    │
    ├─ WAPE (Weighted Absolute Percentage Error)
    ├─ RMSE (Root Mean Squared Error)
    ├─ Pinball Loss (Quantile-specific)
    └─ By-SKU Performance Report
    ↓
Model Registry (model_registry.py)
    │
    └─ Serialize with Joblib
       └─ Store: models/lightgbm_quantile_{sku}_{timestamp}.pkl
    ↓
Prediction (predict.py)
    │
    ├─ Load Model
    ├─ Prepare Features
    ├─ Generate P10, P50, P90
    └─ Cache Results (forecast table)
    ↓
API Endpoint (/api/forecast/*)
    ↓
Dashboard Visualization
```

### 5.2 LightGBM Quantile Regression Configuration

```python
# Hyperparameters
params = {
    'objective': 'quantile',
    'metric': 'quantile',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1,
    'seed': 42,
    'n_jobs': -1
}

# Train 3 models (one per quantile)
quantiles = [0.1, 0.5, 0.9]  # P10, P50, P90
models = {}

for q in quantiles:
    params['alpha'] = q
    models[q] = lgb.train(
        params,
        train_data,
        num_boost_round=1000,
        valid_sets=[valid_data],
        early_stopping_rounds=50
    )
```

### 5.3 Feature Engineering Example

```python
def engineer_features(df_sales):
    """
    Input: Sales DataFrame with columns
    [date, sku_id, quantity, price, discount, promotion, stock_available]
    
    Output: Features ready for LightGBM
    """
    
    # Temporal Features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_holiday'] = df['date'].isin(holiday_dates).astype(int)
    
    # Lag Features
    for lag in [1, 7, 14, 30]:
        df[f'lag_{lag}'] = df.groupby('sku_id')['quantity'].shift(lag)
    
    # Rolling Aggregates
    for window in [7, 14, 30]:
        df[f'rolling_mean_{window}'] = df.groupby('sku_id')['quantity'].rolling(window).mean().reset_index(drop=True)
        df[f'rolling_std_{window}'] = df.groupby('sku_id')['quantity'].rolling(window).std().reset_index(drop=True)
    
    # Commercial Features
    df['discount_pct'] = (df['discount'] / df['price'] * 100).fillna(0)
    df['is_promotion'] = df['promotion'].astype(int)
    
    # Inventory Features
    df['stock_available'] = df['stock_available'].fillna(0)
    df['is_zero_demand'] = (df['quantity'] == 0).astype(int)
    df['is_stockout'] = ((df['quantity'] > 0) & (df['stock_available'] == 0)).astype(int)
    
    return df
```

---

## 6. Inventory Optimization Engine (Khushi)

### 6.1 Dynamic ROP Calculation

```python
def calculate_rop(
    mean_demand,           # d̄ (avg daily demand from forecast)
    mean_lead_time,        # L (supplier lead time)
    demand_std,            # σd (std dev of demand)
    lead_time_std,         # σL (std dev of lead time)
    service_level=0.95     # Z-factor lookup table
):
    """
    ROP = d̄L + Z√(Lσd² + d̄²σL²)
    """
    # Z-factor lookup
    z_factors = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
    z = z_factors.get(service_level, 1.65)
    
    # Lead-time demand
    ltd = mean_demand * mean_lead_time
    
    # Safety stock
    ss = z * np.sqrt(
        mean_lead_time * (demand_std ** 2) + 
        (mean_demand ** 2) * (lead_time_std ** 2)
    )
    
    # Reorder point
    rop = ltd + ss
    
    return {
        'rop': rop,
        'safety_stock': ss,
        'lead_time_demand': ltd,
        'z_factor': z,
        'service_level': service_level
    }
```

### 6.2 Stock-out Probability (Monte Carlo)

```python
def calculate_stockout_probability(
    initial_inventory,
    forecast_demand_distribution,  # P10, P50, P90 from model
    lead_time_distribution,        # Mean, Std
    num_simulations=1000
):
    """
    Run Monte Carlo simulation to estimate P(Stockout)
    """
    stockout_count = 0
    
    for _ in range(num_simulations):
        # Sample demand over lead time
        demand_samples = np.random.normal(
            forecast_demand_distribution['p50'],
            (forecast_demand_distribution['p90'] - forecast_demand_distribution['p10']) / 4
        )
        lead_time_demand = demand_samples.sum()
        
        # Check if stock will deplete
        if initial_inventory < lead_time_demand:
            stockout_count += 1
    
    p_stockout = stockout_count / num_simulations
    
    # Risk classification
    if p_stockout < 0.05:
        risk_level = 'LOW'
    elif p_stockout < 0.15:
        risk_level = 'MEDIUM'
    elif p_stockout < 0.30:
        risk_level = 'HIGH'
    else:
        risk_level = 'CRITICAL'
    
    return {
        'stockout_probability': p_stockout,
        'risk_level': risk_level,
        'simulations': num_simulations
    }
```

### 6.3 PO Recommendation Algorithm

```python
def recommend_purchase_order(
    sku_id,
    current_stock,
    allocated_stock,
    incoming_stock,
    forecast,
    rop,
    supplier_moq,
    supplier_capacity,
    lead_time,
    service_level
):
    """
    Explainable PO recommendation
    """
    available = current_stock + incoming_stock - allocated_stock
    
    # Decision logic
    if available < rop:
        # Need to reorder
        
        # Calculate demand over lead time
        lead_time_demand = forecast['p50'] * lead_time
        
        # Target inventory: ROP + 1 lead-time demand (safety buffer)
        target_inventory = rop + lead_time_demand
        
        # Recommended quantity
        recommended_qty = max(target_inventory - available, 0)
        
        # Respect supplier constraints
        if recommended_qty > 0:
            # Round up to supplier MOQ
            recommended_qty = np.ceil(recommended_qty / supplier_moq) * supplier_moq
            
            # Cap at supplier capacity
            recommended_qty = min(recommended_qty, supplier_capacity)
        
        urgency = 'CRITICAL' if available < (rop * 0.5) else 'HIGH'
        
        return {
            'should_order': True,
            'sku_id': sku_id,
            'recommended_qty': int(recommended_qty),
            'current_stock': current_stock,
            'incoming_stock': incoming_stock,
            'available_stock': available,
            'rop': rop,
            'lead_time_demand': lead_time_demand,
            'target_inventory': target_inventory,
            'supplier_moq': supplier_moq,
            'urgency': urgency,
            'stockout_risk': calculate_stockout_probability(available, forecast, lead_time)['stockout_probability'],
            'projected_stockout_date': calculate_stockout_date(available, forecast),
            'reason': f'Current stock ({available}) falls below ROP ({rop})'
        }
    else:
        return {
            'should_order': False,
            'sku_id': sku_id,
            'current_stock': current_stock,
            'available_stock': available,
            'rop': rop,
            'reason': 'Current stock is above ROP; no order needed'
        }
```

---

## 7. SimPy Digital Twin (Khushi)

### 7.1 Simulation Model Architecture

```python
import simpy

class SupplyChainSimulation:
    """
    Discrete-Event Simulation using SimPy
    Models: Demand → Inventory Consumption → Reorder Trigger → 
            Purchase Order → Supplier Processing → Transportation → 
            Goods Receipt → Replenishment
    """
    
    def __init__(self, env, config):
        self.env = env
        self.config = config  # Lead time, demand, supplier params
        
        # State tracking
        self.inventory_history = []
        self.stockout_events = []
        self.po_history = []
        self.cost_tracker = {'holding': 0, 'shortage': 0, 'ordering': 0}
    
    def customer_demand(self):
        """Generate customer demand events"""
        while True:
            # Sample daily demand from forecast distribution
            daily_demand = np.random.normal(
                self.config['p50_demand'],
                (self.config['p90_demand'] - self.config['p10_demand']) / 4
            )
            daily_demand = max(0, daily_demand)
            
            # Try to fulfill
            if self.inventory >= daily_demand:
                self.inventory -= daily_demand
            else:
                # Stockout
                self.stockout_events.append({
                    'time': self.env.now,
                    'demand': daily_demand,
                    'available': self.inventory
                })
                self.inventory = 0
                self.cost_tracker['shortage'] += (daily_demand - self.inventory) * self.config['shortage_cost']
            
            self.inventory_history.append({
                'time': self.env.now,
                'inventory': self.inventory
            })
            
            yield self.env.timeout(1)  # 1-day timestep
    
    def inventory_manager(self):
        """Monitor inventory and trigger reorders"""
        while True:
            if self.inventory < self.config['rop']:
                # Trigger purchase order
                yield self.env.process(self.place_order())
            
            yield self.env.timeout(1)  # Check daily
    
    def place_order(self):
        """Simulate purchase order and delivery"""
        # Lead time with stochasticity
        lead_time = np.random.lognormal(
            np.log(self.config['mean_lead_time']),
            self.config['lead_time_std']
        )
        
        order_qty = self.config['recommended_qty']
        order_time = self.env.now
        
        # Simulate supplier processing + transportation
        yield self.env.timeout(lead_time)
        
        # Goods receipt
        self.inventory += order_qty
        self.po_history.append({
            'order_time': order_time,
            'delivery_time': self.env.now,
            'order_qty': order_qty,
            'lead_time': lead_time
        })
        
        # Holding cost
        self.cost_tracker['holding'] += self.inventory * self.config['holding_cost_per_unit']
        self.cost_tracker['ordering'] += self.config['order_cost']
    
    def run(self):
        """Execute simulation"""
        self.env.process(self.customer_demand())
        self.env.process(self.inventory_manager())
        
        self.env.run(until=self.config['horizon_days'])
        
        return self.get_results()
    
    def get_results(self):
        """Aggregate simulation results"""
        return {
            'avg_inventory': np.mean([h['inventory'] for h in self.inventory_history]),
            'max_inventory': max([h['inventory'] for h in self.inventory_history]),
            'min_inventory': min([h['inventory'] for h in self.inventory_history]),
            'stockout_events': len(self.stockout_events),
            'stockout_probability': len(self.stockout_events) / self.config['horizon_days'],
            'total_cost': sum(self.cost_tracker.values()),
            **self.cost_tracker
        }
```

---

## 8. IoT Integration (Khushi)

### 8.1 MQTT Architecture

```
ESP32 / Raspberry Pi Sensors
         ↓
     MQTT Broker (Mosquitto)
         │
         ├─ Topic: sensors/warehouse/shelf/{shelf_id}
         │
         └─ Payload: {
              "sensor_id": "SHELF-B04",
              "sku_id": "SKU-9902",
              "weight_grams": 4500,
              "unit_weight_grams": 150,
              "detected_quantity": 30,
              "timestamp": "2026-08-18T09:30:00Z"
            }
         ↓
MQTT Listener (mqtt_listener.py)
         ↓
Validation & Processing (telemetry_processor.py)
         │
         ├─ Parse payload
         ├─ Validate schema
         ├─ Calculate discrepancy: Δ = |IoT - ERP|
         └─ Trigger alerts if Δ > threshold
         ↓
PostgreSQL (sensor_logs table)
         ↓
Dashboard & Alert Engine
```

### 8.2 Discrepancy Detection

```python
def process_iot_telemetry(payload):
    """
    Receive MQTT telemetry, detect discrepancies
    """
    sensor_id = payload['sensor_id']
    sku_id = payload['sku_id']
    measured_weight = payload['weight_grams']
    unit_weight = payload['unit_weight_grams']
    timestamp = payload['timestamp']
    
    # Calculate detected quantity
    detected_qty = measured_weight / unit_weight
    
    # Fetch current ERP inventory
    erp_qty = get_erp_inventory(sku_id)
    
    # Calculate discrepancy
    discrepancy = abs(detected_qty - erp_qty)
    discrepancy_pct = (discrepancy / erp_qty * 100) if erp_qty > 0 else 0
    
    # Alert threshold (configurable)
    ALERT_THRESHOLD_PCT = 10  # Alert if diff > 10%
    
    alert_flag = False
    alert_level = 'INFO'
    
    if discrepancy_pct > ALERT_THRESHOLD_PCT:
        alert_flag = True
        alert_level = 'CRITICAL' if discrepancy_pct > 25 else 'WARNING'
    
    # Log to database
    log_entry = {
        'sensor_id': sensor_id,
        'sku_id': sku_id,
        'measured_weight_grams': measured_weight,
        'unit_weight_grams': unit_weight,
        'calculated_quantity': detected_qty,
        'erp_quantity_at_time': erp_qty,
        'discrepancy_qty': discrepancy,
        'discrepancy_pct': discrepancy_pct,
        'alert_flag': alert_flag,
        'alert_level': alert_level,
        'timestamp': timestamp,
        'location': payload.get('location', 'unknown')
    }
    
    db.sensor_logs.insert(log_entry)
    
    # If alert, create alert record
    if alert_flag:
        create_alert({
            'type': 'IoT_DISCREPANCY',
            'severity': alert_level,
            'sku_id': sku_id,
            'sensor_id': sensor_id,
            'message': f'Discrepancy detected: {discrepancy_pct:.1f}% (IoT: {detected_qty}, ERP: {erp_qty})',
            'timestamp': timestamp
        })
    
    return log_entry
```

---

## 9. Technology Stack

### 9.1 Languages & Runtimes
- Python 3.10+
- Bash (for scripts)

### 9.2 Data Science / ML
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: Data preprocessing, metrics
- **lightgbm**: Quantile regression (primary model)
- **joblib**: Model serialization

### 9.3 Backend
- **FastAPI**: REST API framework
- **SQLAlchemy**: ORM
- **pydantic**: Data validation
- **alembic**: Database migrations

### 9.4 Database
- **PostgreSQL** (production)
- **SQLite** (local development fallback)
- **psycopg2-binary**: PostgreSQL driver

### 9.5 Simulation
- **simpy**: Discrete-event simulation

### 9.6 IoT
- **paho-mqtt**: MQTT client library
- **mosquitto** (broker, external)

### 9.7 Dashboard
- **streamlit**: Interactive web UI
- **plotly**: Advanced charting

### 9.8 Testing & Utilities
- **pytest**: Unit testing
- **pytest-cov**: Code coverage
- **python-dotenv**: Environment management
- **requests**: HTTP client

### 9.9 Infrastructure (Docker)
- **Docker**: Containerization
- **docker-compose**: Multi-container orchestration

---

## 10. Project Directory Structure

```
project_root/
│
├── data/
│   ├── raw/
│   │   └── sales_history.csv
│   │   └── supplier_data.csv
│   ├── processed/
│   │   └── features_engineered.pkl
│   └── sample/
│       └── demo_data.sql
│
├── ml_engine/
│   ├── __init__.py
│   ├── data_loader.py           # Load sales data from DB
│   ├── feature_engineering.py   # Generate features (temporal, lag, rolling)
│   ├── train_forecaster.py      # LightGBM training pipeline
│   ├── predict.py               # Generate P10/P50/P90 forecasts
│   ├── evaluate.py              # WAPE, RMSE, Pinball Loss
│   └── model_registry.py        # Joblib model serialization
│
├── inventory_engine/
│   ├── __init__.py
│   ├── safety_stock.py          # Dynamic SS calculation
│   ├── reorder_point.py         # Dynamic ROP calculation
│   ├── risk_engine.py           # Stock-out probability + classification
│   ├── overstock_detector.py    # Overstock rules
│   └── procurement.py           # PO recommendation engine
│
├── simulation/
│   ├── __init__.py
│   ├── warehouse_sim.py         # SimPy environment setup
│   ├── supplier_model.py        # Lead-time distributions
│   ├── scenarios.py             # What-If scenario runner
│   └── monte_carlo.py           # Multi-run aggregation
│
├── erp_backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration (DB, MQTT, etc.)
│   ├── database.py              # SQLAlchemy setup
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── item.py              # SKU master
│   │   ├── supplier.py          # Supplier master
│   │   ├── inventory.py         # Current inventory
│   │   ├── purchase_order.py    # PO management
│   │   ├── goods_receipt.py     # GRN
│   │   ├── sales_order.py       # Sales transactions
│   │   ├── sensor_log.py        # IoT telemetry
│   │   ├── forecast_cache.py    # Forecast output cache
│   │   └── inventory_ledger.py  # Immutable audit trail
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── item.py              # Pydantic schemas
│   │   ├── inventory.py
│   │   ├── purchase_order.py
│   │   └── ... (other schemas)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── demand_forecasting_service.py
│   │   ├── inventory_service.py
│   │   ├── procurement_service.py
│   │   ├── simulation_service.py
│   │   ├── alert_service.py
│   │   └── telemetry_service.py
│   │
│   └── routers/
│       ├── __init__.py
│       ├── forecast.py          # /api/forecast/* endpoints
│       ├── inventory.py         # /api/inventory/* endpoints
│       ├── suppliers.py         # /api/suppliers/* endpoints
│       ├── purchases.py         # /api/purchases/* endpoints
│       ├── simulation.py        # /api/simulation/* endpoints
│       ├── alerts.py            # /api/alerts/* endpoints
│       └── iot.py               # /api/iot/* endpoints
│
├── iot/
│   ├── __init__.py
│   ├── mqtt_listener.py         # MQTT subscriber
│   ├── mqtt_publisher.py        # MQTT test publisher (demo)
│   └── telemetry_processor.py   # Validation + discrepancy detection
│
├── dashboard/
│   ├── app.py                   # Main Streamlit app
│   ├── pages/
│   │   ├── 01_overview.py       # Executive Overview
│   │   ├── 02_forecast.py       # Demand Forecast
│   │   ├── 03_inventory.py      # Inventory Health
│   │   ├── 04_simulation.py     # Supply Chain Simulation
│   │   ├── 05_whatif.py         # What-If Scenarios
│   │   └── 06_procurement.py    # PO Recommendations
│   │
│   └── components/
│       ├── charts.py            # Reusable chart functions
│       ├── utils.py             # Dashboard utilities
│       └── styles.py            # CSS/formatting
│
├── tests/
│   ├── __init__.py
│   ├── test_ml_engine.py        # Forecast tests
│   ├── test_inventory_engine.py # ROP, SS, risk tests
│   ├── test_api.py              # FastAPI endpoint tests
│   ├── test_simulation.py       # SimPy scenario tests
│   └── test_integration.py      # End-to-end tests
│
├── notebooks/
│   ├── 01_eda.ipynb             # Exploratory data analysis
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_results_analysis.ipynb
│
├── configs/
│   ├── default.yaml             # Default configuration
│   ├── demo.yaml                # Hackathon demo config
│   └── development.yaml
│
├── scripts/
│   ├── setup_db.py              # Initialize PostgreSQL schema
│   ├── load_sample_data.py      # Populate demo data
│   ├── train_models.py          # Offline model training
│   └── mqtt_simulator.py        # Simulated MQTT telemetry
│
├── docker/
│   ├── Dockerfile.backend       # FastAPI container
│   ├── Dockerfile.dashboard     # Streamlit container
│   └── Dockerfile.broker        # MQTT broker container
│
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Local stack orchestration
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── README.md                    # Project overview (separate file)
└── ARCHITECTURE.md              # This file
```

---

## 11. Deployment Architecture

### 11.1 Local Development (Single Machine)

```
┌─────────────────────────────────────────────┐
│         Docker Compose (docker-compose.yml) │
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ PostgreSQL   │  │ Mosquitto    │        │
│  │ (Port 5432)  │  │ (Port 1883)  │        │
│  └──────────────┘  └──────────────┘        │
│         ↑                 ↑                 │
│         └─────────┬───────┘                 │
│                   │                         │
│  ┌────────────────▼──────────────────────┐ │
│  │  FastAPI Backend                      │ │
│  │  (Port 8000)                          │ │
│  │                                       │ │
│  │  - ML Services                        │ │
│  │  - Inventory Engine                   │ │
│  │  - Simulation Service                 │ │
│  │  - IoT Telemetry Handler              │ │
│  └───────────────┬────────────────────────┘ │
│                  │                          │
│  ┌───────────────▼───────────────────────┐ │
│  │  Streamlit Dashboard                  │ │
│  │  (Port 8501)                          │ │
│  │                                       │ │
│  │  - Executive Overview                 │ │
│  │  - Forecast Visualization             │ │
│  │  - Inventory Dashboard                │ │
│  │  - Simulation Runner                  │ │
│  │  - What-If Analyzer                   │ │
│  │  - PO Recommendations                 │ │
│  └───────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

### 11.2 Containerization (docker-compose.yml)

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: supply_chain_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: supply_chain_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql

  mosquitto:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./configs/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto_data:/mosquitto/data

  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://supply_chain_user:${DB_PASSWORD}@postgres:5432/supply_chain_db
      MQTT_BROKER: mosquitto
      MQTT_PORT: 1883
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - mosquitto
    volumes:
      - ./models:/app/models

  dashboard:
    build:
      context: .
      dockerfile: docker/Dockerfile.dashboard
    environment:
      BACKEND_URL: http://backend:8000
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  postgres_data:
  mosquitto_data:
```

---

## 12. Integration Points

### 12.1 Component Communication

```
Dashboard (Streamlit)
    ↓ HTTP (Streamlit Session)
FastAPI Backend
    ├─ SQL Queries
    │  ↓
    PostgreSQL
    │
    ├─ MQTT Subscribe
    │  ↓
    MQTT Broker (Mosquitto)
    │  ↑
    └─ Simulated Sensors / Real Sensors
    │
    ├─ Model Predictions
    │  ↓
    LightGBM Models (Joblib)
    │
    └─ Simulation
       ↓
    SimPy (In-Process)
```

---

## 13. Monitoring & Logging

### 13.1 Logging Strategy

```python
# All components log to console + file

import logging

logger = logging.getLogger(__name__)

# Example: Forecast training
logger.info(f"Starting model training for SKU-9902 with {len(df)} records")
logger.debug(f"Feature engineering complete: {feature_names}")
logger.error(f"Model training failed: {exception}")

# Log to: logs/app_{timestamp}.log
```

### 13.2 Key Metrics to Monitor

- Model prediction latency (< 5 seconds)
- Simulation completion time (< 30 seconds for 100 runs)
- IoT telemetry latency (< 5 minutes)
- API response time (< 200ms)
- Database query performance (< 1 second)

---

## 14. Security Considerations

**For Hackathon MVP:**

- No authentication (localhost only)
- No HTTPS (use HTTP locally)
- Environment variables for sensitive config (`.env`)
- Database credentials in `.env` (not in code)

**For Production (Future):**

- OAuth2 / JWT authentication
- HTTPS with TLS
- Input validation & sanitization
- Rate limiting
- CORS configuration
- Secrets management (Vault, AWS Secrets Manager)

---

## 15. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **Data Quality** | Poor forecast accuracy | Implement data validation; handle missing values |
| **Model Training Time** | Demo delays | Cache trained models; pre-train offline |
| **MQTT Connectivity** | Missing telemetry | Fallback to manual data entry; test MQTT locally |
| **Simulation Slowness** | Dashboard timeout | Limit simulations to 100 runs; async job queue |
| **Database Crashes** | Data loss | Use Docker volumes for persistence; backup schemas |
| **Team Coordination** | Integration issues | Clear API contracts; early integration testing |

---

## 16. Appendix: Key Formulas

### Dynamic ROP
```
ROP = d̄L + Z√(Lσd² + d̄²σL²)

where:
  d̄ = mean daily demand
  L = mean lead time (days)
  σd = std dev of demand
  σL = std dev of lead time
  Z = service-level factor (95% → Z ≈ 1.65)
```

### Safety Stock
```
SS = Z√(Lσd² + d̄²σL²)
```

### Stock-out Probability (Monte Carlo)
```
P_stockout = (# simulations with stockout) / (total simulations)
```

### WAPE (Weighted Absolute Percentage Error)
```
WAPE = Σ|y - ŷ| / Σy × 100%

where:
  y = actual demand
  ŷ = forecast (P50)
```

---

**Document Status:** APPROVED FOR IMPLEMENTATION  
**Next Step:** Proceed to PHASE 1 with database schema setup (Sanika) and sample data loading
