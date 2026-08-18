# AI-Powered Predictive Supply Chain Digital Twin

**TGPCET Hackathon 2026** | AI/ML Supply Chain Optimization Project

```
OBSERVE → PREDICT → SIMULATE → OPTIMIZE → DECIDE → ACT → LEARN
```

---

## 📋 Project Overview

This project builds an **intelligent, closed-loop supply chain management system** that combines:

✅ **AI Demand Forecasting** (LightGBM Quantile Regression)  
✅ **Stochastic Inventory Optimization** (Dynamic ROP, Safety Stock)  
✅ **Supply Chain Digital Twin** (SimPy Discrete-Event Simulation)  
✅ **Real-Time IoT Monitoring** (MQTT Telemetry + Discrepancy Detection)  
✅ **ERP Backend** (FastAPI + PostgreSQL)  
✅ **Interactive Dashboard** (Streamlit with 6 analytical pages)  
✅ **What-If Scenario Planning** (Monte Carlo Risk Analysis)  

**Result:** A hackathon-ready prototype that demonstrates proactive, data-driven inventory management with explainable AI decisions.

---

## 🎯 Quick Start

### Prerequisites

- **Python 3.10+**
- **PostgreSQL 13+** (or Docker)
- **Docker & Docker Compose** (recommended)
- **Git**

### Option 1: Docker Compose (Recommended for Hackathon)

```bash
# Clone repository
git clone https://github.com/Shantanubhure11/TGPCET_HACK_ORG-030.git
cd TGPCET_HACK_ORG-030

# Copy environment template
cp .env.example .env

# Build & start all services
docker-compose up -d

# Check service health
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f dashboard
```

**Services will be available at:**
- 🔵 **FastAPI Backend:** http://localhost:8000
- 📊 **Streamlit Dashboard:** http://localhost:8501
- 🗄️ **PostgreSQL:** localhost:5432
- 🔌 **MQTT Broker:** localhost:1883

### Option 2: Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/Shantanubhure11/TGPCET_HACK_ORG-030.git
cd TGPCET_HACK_ORG-030

# 2. Create Python virtual environment
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Initialize database
python scripts/setup_db.py

# 6. Load sample data
python scripts/load_sample_data.py

# 7. Train initial models
python ml_engine/train_forecaster.py

# 8. Start MQTT broker (in separate terminal)
mosquitto -c configs/mosquitto.conf

# 9. Start FastAPI backend (in separate terminal)
uvicorn erp_backend.main:app --reload --port 8000

# 10. Start Streamlit dashboard (in separate terminal)
streamlit run dashboard/app.py
```

**Access the system:**
- 🔵 Backend API: http://localhost:8000
- 📊 Dashboard: http://localhost:8501
- 📚 API Docs: http://localhost:8000/docs

---

## 👥 Team Roles & Responsibilities

### Shantanu (Frontend, Design, Testing, QA)

**Responsibilities:**
- [ ] Streamlit dashboard development (all 6 pages)
- [ ] UI/UX design and styling
- [ ] Visual component creation (charts, tables, forms)
- [ ] Integration testing (frontend ↔ backend)
- [ ] User acceptance testing (UAT)
- [ ] Demo preparation and presentation
- [ ] Documentation screenshots and guides

**Key Files to Work With:**
- `dashboard/app.py` (main entry point)
- `dashboard/pages/*.py` (individual page implementations)
- `dashboard/components/` (reusable UI components)
- Tests in `tests/test_integration.py`

**Deliverables for Hackathon:**
1. ✅ All 6 dashboard pages functional
2. ✅ Responsive design (works on desktop)
3. ✅ Clear data visualization
4. ✅ Intuitive user interactions (dropdowns, sliders, buttons)
5. ✅ End-to-end demo script (live walkthrough)

---

### Sanika (Backend, Database, ERP Core)

**Responsibilities:**
- [ ] PostgreSQL database schema design & implementation
- [ ] SQLAlchemy ORM models
- [ ] Database migration scripts (Alembic)
- [ ] CRUD operations & repositories
- [ ] FastAPI endpoint implementation (core routes)
- [ ] Data validation (Pydantic schemas)
- [ ] Database performance optimization
- [ ] Backup & data integrity

**Key Files to Work With:**
- `erp_backend/database.py` (connection setup)
- `erp_backend/models/` (SQLAlchemy entity definitions)
- `erp_backend/schemas/` (Pydantic validation schemas)
- `erp_backend/routers/` (API endpoint implementations)
- `scripts/setup_db.py` (database initialization)
- `scripts/load_sample_data.py` (demo data)

**Deliverables for Hackathon:**
1. ✅ PostgreSQL schema with 10+ tables
2. ✅ Inventory ledger (immutable audit trail)
3. ✅ Support for CRUD operations (Create, Read, Update, Delete)
4. ✅ Normalized relational design (no data duplication)
5. ✅ Sample data for 50+ SKUs, 5+ suppliers, 2+ warehouses
6. ✅ Database backups & disaster recovery plan

---

### Khushi (Backend, ML/AI, Simulation, Optimization)

**Responsibilities:**
- [ ] Data loading & feature engineering pipeline
- [ ] LightGBM model training (P10, P50, P90)
- [ ] Model evaluation metrics (WAPE, RMSE)
- [ ] Inventory optimization algorithms (ROP, SS)
- [ ] Risk engine (stock-out probability, overstock detection)
- [ ] SimPy supply-chain digital twin
- [ ] Monte Carlo simulation & scenario analysis
- [ ] PO recommendation engine
- [ ] IoT telemetry processing & discrepancy detection
- [ ] FastAPI service layer implementations

**Key Files to Work With:**
- `ml_engine/data_loader.py`
- `ml_engine/feature_engineering.py`
- `ml_engine/train_forecaster.py`
- `ml_engine/predict.py`
- `ml_engine/evaluate.py`
- `inventory_engine/safety_stock.py`
- `inventory_engine/reorder_point.py`
- `inventory_engine/risk_engine.py`
- `inventory_engine/procurement.py`
- `simulation/warehouse_sim.py`
- `simulation/monte_carlo.py`
- `iot/telemetry_processor.py`
- `erp_backend/services/` (service layer)

**Deliverables for Hackathon:**
1. ✅ Working demand forecast with P10/P50/P90 (WAPE < 20%)
2. ✅ Dynamic ROP & Safety Stock calculations
3. ✅ Stock-out probability engine (Monte Carlo 100+ runs)
4. ✅ SimPy digital twin simulation (< 30 seconds for 100 runs)
5. ✅ PO recommendation with explainable reasoning
6. ✅ IoT discrepancy detection (real-time alerts)
7. ✅ What-If scenario comparison

---

## 📂 Project Structure

```
TGPCET_HACK_ORG-030/
│
├── data/
│   ├── raw/                    # Raw input files
│   │   └── sales_history.csv
│   ├── processed/              # Preprocessed data
│   │   └── features_engineered.pkl
│   └── sample/                 # Demo data SQL
│       └── demo_data.sql
│
├── ml_engine/                  # Khushi: ML Pipeline
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── train_forecaster.py
│   ├── predict.py
│   ├── evaluate.py
│   └── model_registry.py
│
├── inventory_engine/           # Khushi: Optimization
│   ├── safety_stock.py
│   ├── reorder_point.py
│   ├── risk_engine.py
│   ├── overstock_detector.py
│   └── procurement.py
│
├── simulation/                 # Khushi: Digital Twin
│   ├── warehouse_sim.py
│   ├── supplier_model.py
│   ├── scenarios.py
│   └── monte_carlo.py
│
├── erp_backend/                # Sanika & Khushi
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/                 # Sanika: Database models
│   │   ├── item.py
│   │   ├── supplier.py
│   │   ├── inventory.py
│   │   ├── purchase_order.py
│   │   ├── goods_receipt.py
│   │   ├── sales_order.py
│   │   ├── sensor_log.py
│   │   ├── forecast_cache.py
│   │   └── inventory_ledger.py
│   ├── schemas/                # Sanika: Pydantic validation
│   │   ├── item.py
│   │   ├── inventory.py
│   │   ├── purchase_order.py
│   │   └── ...
│   ├── services/               # Khushi: Business logic
│   │   ├── demand_forecasting_service.py
│   │   ├── inventory_service.py
│   │   ├── procurement_service.py
│   │   ├── simulation_service.py
│   │   ├── alert_service.py
│   │   └── telemetry_service.py
│   └── routers/                # Sanika: API endpoints
│       ├── forecast.py
│       ├── inventory.py
│       ├── suppliers.py
│       ├── purchases.py
│       ├── simulation.py
│       ├── alerts.py
│       └── iot.py
│
├── iot/                        # Khushi: IoT Integration
│   ├── mqtt_listener.py
│   ├── mqtt_publisher.py
│   └── telemetry_processor.py
│
├── dashboard/                  # Shantanu: Frontend
│   ├── app.py
│   └── pages/
│       ├── 01_overview.py
│       ├── 02_forecast.py
│       ├── 03_inventory.py
│       ├── 04_simulation.py
│       ├── 05_whatif.py
│       └── 06_procurement.py
│
├── tests/                      # Shantanu & All
│   ├── test_ml_engine.py
│   ├── test_inventory_engine.py
│   ├── test_api.py
│   ├── test_simulation.py
│   └── test_integration.py
│
├── notebooks/                  # Analysis & experimentation
│   ├── 01_eda.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   └── 04_results_analysis.ipynb
│
├── configs/
│   ├── default.yaml
│   ├── demo.yaml
│   ├── mosquitto.conf
│   └── development.yaml
│
├── scripts/
│   ├── setup_db.py             # Sanika: Database initialization
│   ├── load_sample_data.py     # Sanika: Load demo data
│   ├── train_models.py         # Khushi: Model training
│   └── mqtt_simulator.py       # Khushi: Simulate IoT telemetry
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.dashboard
│   └── Dockerfile.broker
│
├── docs/
│   ├── PRD.md                  # Product requirements
│   ├── ARCHITECTURE.md         # Technical design (this file)
│   ├── API.md                  # API documentation (auto-generated)
│   └── DEMO.md                 # Demo script
│
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md                   # This file
└── LICENSE
```

---

## 🚀 Development Workflow

### Phase Timeline (7-Day Hackathon)

```
DAY 1-2  | Database Setup + Sample Data (Sanika)
         | → Create all tables, populate demo data

DAY 2-3  | Feature Engineering + Model Training (Khushi)
         | → Train LightGBM, validate forecast accuracy

DAY 3-4  | Backend API + Inventory Math (Sanika + Khushi)
         | → Implement FastAPI routes, ROP/SS calculations

DAY 4-5  | Simulation + Optimization (Khushi)
         | → SimPy digital twin, Monte Carlo, PO recommendations

DAY 5-6  | Dashboard Development (Shantanu)
         | → All 6 pages, interactive visualizations

DAY 6-7  | Integration + Testing + Demo Prep (All)
         | → End-to-end testing, fix bugs, prepare demo

DAY 7    | PRESENTATION DAY
         | → Live demo, Q&A with judges
```

### Git Workflow

```bash
# Everyone: Create a feature branch
git checkout -b feature/your-feature-name

# Commit frequently with clear messages
git add .
git commit -m "feat: Add ROP calculation to inventory service"

# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# → Request review from team members
# → Address feedback
# → Merge to main after approval

# Update local main
git checkout main
git pull origin main
```

**Branch Naming Convention:**
- `feature/feature-name` (new features)
- `bugfix/bug-description` (bug fixes)
- `docs/documentation-title` (documentation)
- `test/test-description` (tests)

---

## 🔌 API Quick Reference

### Health Check
```bash
curl http://localhost:8000/health
```

### Forecast Demand
```bash
curl http://localhost:8000/api/forecast/demand?sku_id=SKU-9902&horizon=30
```

### Get Inventory Status
```bash
curl http://localhost:8000/api/inventory/current?sku_id=SKU-9902&warehouse_id=WH-01
```

### Get PO Recommendations
```bash
curl http://localhost:8000/api/purchases/recommendations?service_level=95
```

### Run Simulation
```bash
curl -X POST http://localhost:8000/api/simulation/run \
  -H "Content-Type: application/json" \
  -d '{
    "sku_id": "SKU-9902",
    "lead_time_mean": 3,
    "lead_time_std": 0.5,
    "num_runs": 100,
    "horizon_days": 30
  }'
```

**Full API documentation:** http://localhost:8000/docs (auto-generated by FastAPI)

---

## 📊 Dashboard Pages

### Page 1: Executive Overview
**Owner:** Shantanu

Display KPIs:
- Total SKUs managed
- Inventory value
- Stock-out risk summary
- Overstock value
- Pending POs
- Supplier delays
- IoT discrepancies

### Page 2: Demand Forecast
**Owner:** Shantanu

Show:
- Historical demand chart
- P10/P50/P90 forecast bands
- Forecast horizon selector (7/14/30/60/90 days)
- SKU selector with dropdown
- Model accuracy (WAPE, RMSE)

### Page 3: Inventory Health
**Owner:** Shantanu

Display:
- SKU-by-SKU table with current stock, safety stock, ROP, DOI, stock-out probability
- Filter by warehouse, category, risk level
- Color-coded status (GREEN/YELLOW/RED)

### Page 4: Supply Chain Simulation
**Owner:** Shantanu

Interactive:
- Input sliders: lead time, variability, supplier reliability, service level
- Run button (shows progress)
- Output: Inventory curve, stock-out events, avg inventory, risk, cost

### Page 5: What-If Scenarios
**Owner:** Shantanu

Compare:
- Baseline vs. modified scenario
- Side-by-side metrics: ROP, safety stock, stock-out probability, cost
- Charts showing impact

### Page 6: Procurement Recommendations
**Owner:** Shantanu

Display:
- Recommended POs (SKU, supplier, quantity, urgency, reason)
- Sort/filter options
- Export buttons (JSON, CSV)

---

## 🧪 Testing Strategy

### Unit Tests (Each Owner)

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_ml_engine.py -v
```

**What to Test:**

**Khushi (ML & Inventory):**
- ✅ Feature engineering produces correct shapes
- ✅ Model training converges
- ✅ Forecast P10 < P50 < P90
- ✅ ROP calculation follows formula
- ✅ Stock-out probability is between 0 and 1
- ✅ Simulation returns expected fields

**Sanika (Backend & Database):**
- ✅ Database connection works
- ✅ CRUD operations on all tables
- ✅ Foreign key constraints enforced
- ✅ Inventory ledger immutability
- ✅ API endpoints return correct status codes
- ✅ Pydantic validation rejects invalid data

**Shantanu (Dashboard & Integration):**
- ✅ Dashboard pages load without errors
- ✅ Data flows from backend to frontend
- ✅ User interactions (filters, buttons) work
- ✅ Charts render with data
- ✅ End-to-end workflow (forecast → simulation → PO) completes
- ✅ Error messages display clearly

---

## 📝 Configuration

### Environment Variables (.env)

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/supply_chain_db

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# ML Models
MODEL_DIRECTORY=./models
LOOKBACK_DAYS=365

# Simulation
DEFAULT_SERVICE_LEVEL=0.95
DEFAULT_NUM_SIMULATIONS=100

# API
API_PORT=8000
LOG_LEVEL=INFO
```

### Configuration Files

- `configs/default.yaml` - Default settings
- `configs/demo.yaml` - Hackathon demo configuration
- `configs/mosquitto.conf` - MQTT broker settings

---

## 🐛 Troubleshooting

### PostgreSQL Connection Error

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Verify connection string in .env
# Format: postgresql://user:password@host:port/database

# Test connection
psql -U user -h localhost -d supply_chain_db
```

### MQTT Connection Error

```bash
# Check if Mosquitto is running
docker ps | grep mosquitto

# Test MQTT connection
mosquitto_sub -h localhost -t test/topic

# In another terminal
mosquitto_pub -h localhost -t test/topic -m "Hello"
```

### Model Training Too Slow

```bash
# Reduce training data
# In ml_engine/train_forecaster.py
lookback_days = 90  # Reduce from 365

# Use fewer boosting rounds
num_boost_round = 500  # Reduce from 1000

# Use sample of data for testing
df_sample = df.sample(frac=0.1, random_state=42)
```

### Dashboard Not Connecting to Backend

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check .env BACKEND_URL
# Should be: http://backend:8000 (Docker) or http://localhost:8000 (local)

# Check dashboard logs
streamlit run dashboard/app.py --logger.level=debug
```

### Docker Compose Fails to Start

```bash
# Check for port conflicts
lsof -i :5432  # PostgreSQL
lsof -i :1883  # MQTT
lsof -i :8000  # Backend
lsof -i :8501  # Dashboard

# Rebuild images
docker-compose build --no-cache

# Start with verbose logging
docker-compose up --verbose
```

---

## 📚 Documentation

- **PRD.md** - Product requirements and features
- **ARCHITECTURE.md** - Technical design and data flow (detailed)
- **API.md** - Auto-generated API documentation (run `python docs/generate_api_docs.py`)
- **DEMO.md** - Live demonstration script (5–10 minute walkthrough)

**Generate API Docs:**
```bash
python docs/generate_api_docs.py
# Creates API.md with all endpoints
```

---

## 🎓 Learning Resources

### LightGBM Quantile Regression
- https://lightgbm.readthedocs.io/en/latest/
- Kaggle: "Quantile Regression with LightGBM"

### SimPy Discrete-Event Simulation
- https://simpy.readthedocs.io/
- Official Tutorial: Modeling a Bank & Customers

### Streamlit Dashboard Development
- https://streamlit.io/docs
- Streamlit Gallery: https://streamlit.io/gallery

### FastAPI Best Practices
- https://fastapi.tiangolo.com/
- Full Stack Python FastAPI + PostgreSQL

### Supply Chain Optimization
- Wilson EOQ Model (Economic Order Quantity)
- Safety Stock Formulas (Dynamic Inventory Management)

---

## 🏆 Hackathon Success Criteria

### ✅ Must-Haves (for acceptance)

1. **Working Database** with 10+ tables and sample data ✓ (Sanika)
2. **Demand Forecast** that generates P10/P50/P90 with WAPE < 20% ✓ (Khushi)
3. **Inventory Optimization** (ROP, SS, Stock-out Risk) ✓ (Khushi)
4. **FastAPI Backend** with functional endpoints ✓ (Sanika + Khushi)
5. **Streamlit Dashboard** with at least 4 working pages ✓ (Shantanu)
6. **Digital Twin Simulation** running 100+ scenarios ✓ (Khushi)
7. **IoT Telemetry** ingestion and discrepancy detection ✓ (Khushi)
8. **GitHub Repository** with clean code and documentation ✓ (All)

### ✨ Nice-to-Haves (differentiation)

1. **What-If Scenario Comparison** ✓ (Page 5)
2. **PO Export** (JSON/CSV) ✓ (Page 6)
3. **Explainable Recommendations** (reasoning logged) ✓
4. **Real MQTT Sensors** integration ✓
5. **Docker Deployment** ✓
6. **Comprehensive Testing** (> 80% code coverage) ✓
7. **Live Demo Video** ✓

---

## 📞 Support & Communication

### Daily Standup

**Time:** 10:00 AM  
**Duration:** 15 minutes  
**Agenda:** Blockers, progress, plan for next 8 hours

### Weekly Review (Every Hackathon Day 4, 7)

**Time:** 6:00 PM  
**Duration:** 30 minutes  
**Agenda:** Demo of working features, discuss next phase

### Communication Channels

- **Slack/Discord:** Real-time questions
- **GitHub Issues:** Bug reports & feature requests
- **GitHub Discussions:** Technical decisions & design reviews

**Escalation:** If blocked for > 1 hour, ping team lead immediately

---

## 📄 License

MIT License — See LICENSE file

---

## 🚀 Ready to Start?

1. ✅ Clone the repository
2. ✅ Copy `.env.example` to `.env`
3. ✅ Run `docker-compose up -d` or follow local setup
4. ✅ Load sample data: `python scripts/load_sample_data.py`
5. ✅ Open dashboard: http://localhost:8501
6. ✅ Check API docs: http://localhost:8000/docs

**Questions?** → Check the ARCHITECTURE.md or reach out to the team!

---

## 📌 Quick Command Reference

```bash
# Database
python scripts/setup_db.py              # Initialize DB
python scripts/load_sample_data.py      # Load demo data
psql -U user -d supply_chain_db         # Connect to DB

# ML Training
python ml_engine/train_forecaster.py    # Train models
python -m pytest tests/test_ml_engine.py -v

# Backend
uvicorn erp_backend.main:app --reload   # Start API
curl http://localhost:8000/docs         # View API docs

# Dashboard
streamlit run dashboard/app.py           # Start UI

# Testing
pytest tests/ -v --cov=.                # Full coverage

# Docker
docker-compose up -d                    # Start all services
docker-compose logs -f backend          # View backend logs
docker-compose down                     # Stop services
```

---

**Project Kickoff:** August 18, 2026  
**Hackathon Submission Deadline:** August 25, 2026  

**Let's build something amazing! 🚀**
