# Indonesia Energy Crisis Model

**Smart Home & Smart Office System — Energy Supply-Demand Simulation & Mitigation Analysis**

## Overview

This model simulates Indonesia's energy supply-demand dynamics under various crisis scenarios and quantifies how smart building / smart home systems can mitigate crisis impacts. It builds directly on existing platform data:

- **Indonesia ASEAN Market Analysis** — 270M population, 5 priority cities, $2.5-3B TAM
- **Feature Expansion Roadmap** — energy management features with 20-30% savings targets
- **Existing IoT architecture** — MQTT, TimescaleDB, FastAPI sensor infrastructure

## Key Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Installed Capacity | 82 GW | PLN 2025 |
| Peak Demand | 43.5 GW | PLN 2025 |
| Coal Dependency | 61.7% | ESDM |
| Population | 270M | BPS |
| Urban Ratio | 57% | World Bank |
| Smart HVAC Savings | 25% | Feature Roadmap |
| Smart Lighting Savings | 50% | Feature Roadmap |

## Crisis Scenarios Modeled

| Scenario | Severity | Annual Probability | Supply Impact |
|----------|----------|-------------------|---------------|
| Coal Supply Disruption | 70% | 15% | -25% supply |
| Extreme Heat Wave | 60% | 25% | -10% supply, +25% demand |
| Grid Cascade Failure | 90% | 5% | -60% supply |
| Natural Gas Price Shock | 50% | 20% | -12% supply |
| Renewable Transition Gap | 40% | 30% | -8% supply, +5% demand |

## Files

| File | Description |
|------|-------------|
| `indonesia_energy_crisis_simulation.py` | Python simulation engine — run all scenarios, compare smart adoption rates, export JSON |
| `energy-crisis-dashboard.html` | Interactive browser dashboard — scenario selection, KPIs, charts, city impact table |
| `simulation_results.json` | Generated output (after running simulation) |

## Quick Start

### Run Python Simulation

```bash
cd indonesia-energy-crisis-model
python indonesia_energy_crisis_simulation.py
```

This will:
1. Run all 5 crisis scenarios for 2026
2. Compare smart building adoption rates (0% to 50%)
3. Export results to `simulation_results.json`
4. Print key insights

### Open Dashboard

Open `energy-crisis-dashboard.html` in any browser. The dashboard runs entirely client-side with:
- Scenario selector (5 crisis types)
- Year slider (2026-2030)
- Smart building adoption slider (0-50%)
- Supply vs Demand chart
- Reserve margin & load shedding chart
- Energy mix breakdown
- Adoption vs Economic Loss comparison
- City-level impact table (Jakarta, Surabaya, Bandung, Medan, Semarang)

## Key Findings

1. **Coal dependency (61.7%)** creates acute vulnerability — a 25% coal disruption causes cascading blackouts across Java-Bali affecting 30M+ people

2. **Climate amplification** is the most frequent risk (25%/year) — El Nino simultaneously increases demand (+25% AC) and reduces supply (-10% hydro)

3. **Smart buildings at 20% adoption** reduce peak demand by 2-4%, preventing ~30% of load shedding events

4. **At 50% adoption**, economic losses from energy crises drop by 40-60%

5. **HVAC optimization (25% savings)** is the biggest single lever; **smart lighting (50% savings)** has the fastest ROI

6. **Platform value**: The Smart Home & Smart Office System is both a cost-saving tool AND crisis mitigation infrastructure

## Architecture Integration

The model connects to the existing platform architecture:

```
Sensors (MQTT) → IoT Gateway → Energy Management Service → TimescaleDB
                                      ↓
                              Smart Controls (HVAC, Lighting, Load Shifting)
                                      ↓
                              Crisis Dashboard (this model)
```

## Data Sources

- PLN (State Electricity Company) — capacity & demand data
- ESDM (Ministry of Energy) — energy mix, RUPTL targets
- World Bank — economic loss estimates ($0.5M/GWh unserved)
- Feature Expansion Roadmap — smart building savings rates
- Indonesia ASEAN Market Analysis — city demographics & market data
