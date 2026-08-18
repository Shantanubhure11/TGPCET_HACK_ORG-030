# Product Requirements Document (PRD)
## AI-Powered Predictive Supply Chain Digital Twin

**Project:** TGPCET Hackathon 2026  
**Repository:** https://github.com/Shantanubhure11/TGPCET_HACK_ORG-030.git  
**Team:** Shantanu (Frontend/Design/Testing) | Sanika (Backend/Database) | Khushi (Backend Enhancement)  
**Version:** 1.0  
**Date:** August 2026

---

## 1. Executive Summary

The AI-Powered Predictive Supply Chain Digital Twin is an intelligent inventory and procurement management system that combines machine learning demand forecasting, stochastic supply chain simulation, and real-time IoT monitoring to optimize inventory levels, minimize stockouts, and reduce holding costs.

The system implements a closed-loop optimization cycle:

**OBSERVE → PREDICT → SIMULATE → OPTIMIZE → DECIDE → ACT → LEARN**

---

## 2. Problem Statement

Modern supply chains face critical challenges:

- **Demand Uncertainty:** Historical data alone cannot capture future variability
- **Supplier Unpredictability:** Lead times vary; delays cascade through inventory
- **Stock-out Risk:** Under-stock leads to lost sales and customer dissatisfaction
- **Overstock Waste:** Over-purchase ties up capital and increases holding costs
- **Inventory Blindness:** ERP systems lack real-time visibility; IoT discrepancies undetected
- **Manual Decision-Making:** PO decisions rely on rules-of-thumb, not data-driven optimization

---

## 3. Solution Overview

The digital twin creates a **simulation sandbox** where the system:

1. Analyzes historical sales, inventory, and supplier data
2. Trains probabilistic demand forecasting models (LightGBM quantile regression)
3. Generates demand uncertainty bands (P10, P50, P90)
4. Simulates supplier lead-time variability with Monte Carlo methods
5. Calculates dynamic safety stock and reorder points
6. Monitors real-time IoT telemetry for discrepancies
7. Recommends purchase orders with explainable reasoning
8. Allows "what-if" scenario testing before real actions
9. Continuously learns from new data

**Key Differentiator:** This is NOT just demand prediction. It is a **closed-loop AI system** that combines forecasting, simulation, optimization, and decision automation.

---

## 4. Core Business Objectives

| Objective | Success Metric |
|-----------|---|
| Reduce stockouts | Achieve target service level (e.g., 95%) within 2% tolerance |
| Minimize overstock | Reduce excess inventory by 20% vs. baseline |
| Optimize inventory levels | Improve inventory turnover by 15% |
| Automate procurement | 80% of PO recommendations accepted by users |
| Detect IoT anomalies | Identify inventory discrepancies within 5 minutes |
| Improve forecast accuracy | WAPE < 20% on 30-day horizon |
| Enable scenario planning | Run what-if simulations in < 30 seconds |

---

## 5. Functional Requirements

### 5.1 Demand Forecasting

**FR-DF-01:** Multi-SKU demand prediction
- Support forecasting for 50+ SKUs simultaneously
- Input: Historical sales by SKU, date, warehouse, price, promotion

**FR-DF-02:** Probabilistic forecasting
- Generate P10, P50, P90 demand quantiles
- Method: LightGBM Quantile Regression
- Configurable forecast horizon: 7, 14, 30, 60, 90 days

**FR-DF-03:** Feature engineering
- Temporal: day-of-week, month, quarter, holidays
- Lag features: 1, 7, 14, 30 days
- Rolling aggregates: mean/std over 7, 14, 30 days
- Commercial: price, discount %, promotion flag
- Inventory: distinguish stock-out from zero-demand

**FR-DF-04:** Model evaluation
- Calculate WAPE (Weighted Absolute Percentage Error)
- Calculate RMSE
- Calculate Pinball Loss for quantile forecasts
- Report by SKU and overall

---

### 5.2 Inventory Optimization

**FR-IO-01:** Dynamic Reorder Point (ROP)
- Formula: ROP = d̄L + Z√(Lσd² + d̄²σL²)
- Where:
  - d̄ = predicted average daily demand
  - L = mean supplier lead time
  - σd = std dev of daily demand
  - σL = std dev of lead time
  - Z = service-level factor (configurable: 90%, 95%, 99%)

**FR-IO-02:** Dynamic Safety Stock
- SS = Z√(Lσd² + d̄²σL²)
- Must be explainable and separately displayed

**FR-IO-03:** Service Level Configuration
- Allow user to set target service level: 90%, 95%, 99%
- Immediately recalculate ROP, Safety Stock, PO recommendations
- Dashboard shows impact on each metric

**FR-IO-04:** Stock-out Risk Calculation
- P_stockout = (simulations with stockout) / (total simulations)
- Classification: LOW, MEDIUM, HIGH, CRITICAL
- Thresholds configurable (not hard-coded)

**FR-IO-05:** Overstock Detection
- Rules: Days of Inventory > threshold
- Inventory significantly above expected demand
- Inventory > maximum stock level
- Low demand + high inventory
- Explain WHY each item is classified as overstocked

---

### 5.3 Purchase Order Recommendation

**FR-PO-01:** PO Recommendation Engine
- Trigger: Current Inventory + Incoming < Dynamic ROP
- Factors: Current stock, allocated stock, incoming stock, forecast demand, lead time, safety stock, supplier MOQ, supplier capacity

**FR-PO-02:** Explainable Recommendations
- Structured output: SKU, supplier, quantity, reason, urgency, projected stock-out date
- Format: JSON, exportable as CSV/JSON/PDF

**FR-PO-03:** PO Simulation
- Do NOT automatically send to suppliers
- Simulate PO action and show projected inventory impact
- Allow user to approve/reject before action

---

### 5.4 Supply Chain Digital Twin

**FR-DT-01:** Discrete-Event Simulation (SimPy)
- Model: Customer demand → Inventory consumption → Reorder trigger → PO creation → Supplier processing → Transportation → Goods receipt → Inventory replenishment

**FR-DT-02:** Stochastic Supplier Behavior
- Lead time: LogNormal distribution (configurable mean, std dev)
- Supplier reliability: % of orders delayed
- Transportation delay: configurable range
- Number of runs: configurable (100–1000 initially)

**FR-DT-03:** Monte Carlo Results
- For each run: stock-out events, average inventory, max inventory, turnover, holding cost, shortage cost, total cost
- Aggregate: stock-out probability, cost distribution, service level

**FR-DT-04:** What-If Scenarios
- User can modify: lead time, demand multiplier, supplier reliability, service level
- System recalculates and compares: ROP, safety stock, stock-out probability, PO quantity, total cost
- Side-by-side comparison of baseline vs. scenario

---

### 5.5 Real-Time IoT Monitoring

**FR-IoT-01:** MQTT Telemetry Ingestion
- Protocol: MQTT via Paho
- Payload: sensor_id, sku_id, weight_grams, unit_weight_grams, detected_quantity, timestamp
- Validation: reject malformed payloads

**FR-IoT-02:** Inventory Discrepancy Detection
- Calculate: Δ = |IoT Stock - ERP Stock|
- Alert if: Δ > threshold (configurable)
- Display: ERP qty, IoT qty, discrepancy, % difference, sensor, SKU, timestamp

**FR-IoT-03:** Inventory Ledger
- Record all inventory changes as transactions (not overwrites)
- Maintain audit trail: source (PO, Sales, IoT adjustment), timestamp, user, quantity change

---

### 5.6 ERP Backend

**FR-ERP-01:** Master Data
- Items: SKU, name, category, unit, unit cost, selling price, supplier, MOQ
- Suppliers: name, avg lead time, lead-time std dev, reliability %, MOQ
- Warehouses: name, address, capacity

**FR-ERP-02:** Inventory Ledger
- Real-time balance by SKU and warehouse
- Fields: physical stock, allocated stock, available stock, safety stock, ROP, last update

**FR-ERP-03:** Purchase Orders
- Create, update, query POs
- Fields: PO number, supplier, SKU, quantity, order date, expected delivery, status, notes

**FR-ERP-04:** Goods Received Notes (GRN)
- Record receipt of PO
- Fields: GRN number, PO reference, received quantity, received date, discrepancy flag

**FR-ERP-05:** Sales Orders
- Record sales transactions
- Fields: order ID, SKU, quantity, timestamp, warehouse

**FR-ERP-06:** Sensor Logs
- Record IoT telemetry
- Fields: sensor ID, SKU, measured quantity, weight, timestamp, location

---

### 5.7 Interactive Dashboard (Streamlit)

**FR-Dashboard-01:** Executive Overview (Page 1)
- Total SKUs managed
- Total inventory value
- Stock-out risk summary (count by risk level)
- Overstock count and value
- Pending POs (count, total value)
- Supplier delays (count)
- IoT discrepancies (count)

**FR-Dashboard-02:** Demand Forecast (Page 2)
- Historical demand chart (past 12 months)
- Forecast chart: P10, P50, P90 (future 30+ days)
- Forecast horizon selector (7/14/30/60/90 days)
- SKU selector (dropdown or multi-select)
- Model performance metrics (WAPE, RMSE)

**FR-Dashboard-03:** Inventory Health (Page 3)
- By-SKU table: current stock, available stock, allocated stock, safety stock, ROP, days of inventory, stock-out probability, status
- Filter by: warehouse, category, risk level
- Visual: traffic light (RED/YELLOW/GREEN)

**FR-Dashboard-04:** Supply Chain Simulation (Page 4)
- Input controls: lead time, lead-time variability, demand multiplier, supplier reliability, service level, simulation runs
- Output: projected inventory curve, stock-out events, average inventory, risk score, total cost
- Run button (with progress indicator)

**FR-Dashboard-05:** What-If Scenario (Page 5)
- Baseline scenario (current parameters)
- Scenario input: modify 1+ parameters
- Comparison table: ROP, safety stock, stock-out probability, average inventory, recommended PO, total cost
- Side-by-side charts

**FR-Dashboard-06:** Procurement (Page 6)
- Recommended POs: SKU, supplier, quantity, reason, urgency, projected stock-out date
- Sort by: urgency, stock-out date
- Export: JSON, CSV
- Action buttons: simulate, approve, reject (for future integration)

---

## 6. Non-Functional Requirements

| Requirement | Standard | Rationale |
|---|---|---|
| Response Time | Demand forecast: < 5s | Dashboard interactivity |
| Response Time | Simulation (100 runs): < 30s | User expectations |
| Availability | 99% uptime (dev environment) | Hackathon demo reliability |
| Data Accuracy | WAPE < 20% (30-day horizon) | Acceptable forecast quality |
| Scalability | Support 500+ SKUs | Enterprise-ready foundation |
| Usability | Intuitive dashboard; no training needed | Hackathon demo to non-technical judges |
| Maintainability | Modular code; clear documentation | Team handoff |
| Testability | Unit tests for core ML and inventory logic | Hackathon judging criteria |
| Reproducibility | Seed-controlled randomness; logged configurations | Consistent demo results |
| Explainability | Every decision logged with reasoning | Trustworthiness for real use |

---

## 7. Data Requirements

### 7.1 Input Data

**Historical Sales Data**
- date, SKU, warehouse, quantity_sold, price, discount, promotion, stock_available

**Supplier Master Data**
- supplier_id, name, avg_lead_time, lead_time_std, reliability %, MOQ

**Inventory Records**
- SKU, warehouse, date, physical_stock, allocated_stock, received_date, source (PO, Sales, IoT)

**IoT Telemetry**
- sensor_id, SKU, weight_grams, unit_weight, detected_quantity, timestamp

### 7.2 Data Volume

- Historical sales: 2+ years (minimum 1000+ transactions)
- SKUs: 50–500
- Warehouses: 2–10
- Sensors: 10–50

### 7.3 Data Quality

- Completeness: > 95% non-null critical fields
- Timeliness: Batch uploads daily; IoT updates real-time
- Consistency: No negative quantities; dates in valid range

---

## 8. User Personas & Use Cases

### Persona 1: Supply Chain Manager (Alice)

**Goal:** Optimize inventory levels without stockouts

**Use Case:** Alice checks the Inventory Health dashboard every morning. She sees that SKU-9902 is approaching ROP. The system recommends a PO of 500 units from Supplier S-004, with urgency HIGH. She clicks "What-If: Extend Lead Time to 7 days" to simulate a supplier delay. The stock-out probability jumps to 82%. She approves the PO immediately.

### Persona 2: Data Analyst (Bob)

**Goal:** Understand forecast accuracy and improve model

**Use Case:** Bob reviews model performance on the Demand Forecast page. WAPE is 18% for most SKUs, but SKU-1234 shows 35% WAPE. He suspects seasonality is not captured. He proposes adding a seasonal lag feature and retrains the model offline.

### Persona 3: Warehouse Operations (Carol)

**Goal:** Detect inventory discrepancies early

**Use Case:** Carol monitors the IoT Discrepancy dashboard. SHELF-B04 shows 30 units on IoT but ERP shows 45 units. Δ = 15 (33%). An alert flags this for investigation. Carol checks the physical shelf and finds 10 units (possibly damaged). She updates ERP and marks the discrepancy as resolved.

### Persona 4: C-Suite Executive (David)

**Goal:** Quick snapshot of supply chain health

**Use Case:** David opens the Executive Overview dashboard in a board meeting. Total inventory value: $2.3M. Stock-out risk: 2 SKUs (CRITICAL), 5 SKUs (HIGH). Overstock value: $250K. He asks: "What if we increase service level to 99%?" The system recalculates, and he sees the safety stock increases by 15%, but stock-out risk drops to zero.

---

## 9. Acceptance Criteria

### System Must Deliver

- [ ] Demand forecasting generates P10, P50, P90 for 50+ SKUs with WAPE < 20%
- [ ] Dynamic ROP calculation updates in real-time based on demand forecast and lead time
- [ ] Stock-out probability computed via Monte Carlo (100+ simulations)
- [ ] PO recommendations generated and exported as JSON/CSV
- [ ] MQTT telemetry ingested and discrepancies detected within 5 minutes
- [ ] ERP backend supports CRUD for items, inventory, POs, GRNs, sales, sensors
- [ ] Dashboard loads all pages within 3 seconds
- [ ] Simulation (100 runs) completes within 30 seconds
- [ ] What-If scenarios run and compare in < 10 seconds
- [ ] All critical business logic unit-tested (coverage > 80%)
- [ ] Code deployed to GitHub with README and setup instructions
- [ ] Live demo: end-to-end scenario (forecast → simulation → PO recommendation) in < 10 minutes

---

## 10. Success Metrics (Hackathon Judging Criteria)

| Metric | Target | How Measured |
|---|---|---|
| **Technical Depth** | Probabilistic forecasting + stochastic simulation + optimization | Code review; demo explainability |
| **Innovation** | IoT discrepancy detection + closed-loop AI | Unique features vs. other submissions |
| **Code Quality** | Modular, testable, documented | GitHub repo evaluation |
| **Demo Impact** | Judges understand the full system in 10 min | Clear narrative; live system |
| **Completeness** | All 6 dashboard pages working | Functional demo |
| **Presentation** | Clear technical explanation | Q&A during judging |

---

## 11. Timeline & Milestones

| Phase | Duration | Owner | Deliverable |
|-------|----------|-------|---|
| Phase 0–1 | Day 1–2 | Sanika, Khushi | Database schema + sample data |
| Phase 2–3 | Day 2–3 | Khushi | Feature engineering + model training |
| Phase 4–5 | Day 3–4 | Sanika, Khushi | Inventory math + ERP backend API |
| Phase 6–8 | Day 4–5 | Khushi | Simulation + Monte Carlo engine |
| Phase 9–10 | Day 5–6 | Shantanu | Dashboard UI + integration |
| Phase 11–13 | Day 6–7 | All | Testing, integration, Docker setup |
| Phase 14 | Day 7 | Shantanu | Demo preparation + presentation |

---

## 12. Constraints & Assumptions

### Constraints

- **Time:** 7-day hackathon sprint
- **Data:** Must use publicly available or synthetic data (no private customer data)
- **Infrastructure:** Local development (no cloud required initially)
- **Hardware:** Simulated IoT (no physical sensors required for MVP)

### Assumptions

- PostgreSQL available (Docker or local install)
- Python 3.10+ available
- MQTT broker available (Mosquitto or similar)
- Team has basic Git workflow knowledge
- Internet access for model training and library downloads

---

## 13. Out of Scope

- Real-time integrations with actual ERP systems (SAP, Oracle)
- Automated purchase order execution to real suppliers
- Mobile application
- Advanced ML (LSTM, transformers) unless justified by performance
- Custom hardware development
- Multi-language support

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-18 | Shantanu | Initial PRD from master brief |

---

## 15. Appendix: Technical Glossary

- **ROP (Reorder Point):** Inventory level at which a new purchase order is triggered
- **Safety Stock:** Extra inventory held to protect against demand/lead-time variability
- **P10/P50/P90:** 10th, 50th, 90th percentile of demand forecast (uncertainty bands)
- **WAPE:** Weighted Absolute Percentage Error (forecast accuracy metric)
- **Stock-out:** Situation when demand exceeds available inventory
- **IoT Discrepancy:** Difference between physical inventory (IoT sensor) and ERP record
- **DES:** Discrete-Event Simulation (SimPy)
- **GRN:** Goods Received Note (receipt of purchase order)
- **MOQ:** Minimum Order Quantity from supplier

---

**Document Status:** APPROVED FOR DEVELOPMENT  
**Next Step:** Proceed to PHASE 0 (Architecture Validation) and PHASE 1 (Database Schema)
