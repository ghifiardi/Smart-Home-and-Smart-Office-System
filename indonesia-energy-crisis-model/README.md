# Indonesia Energy Crisis Model v2.0

**Multi-Commodity Energy Supply-Demand Simulation — Coal, LNG, Crude Oil & Renewables**

## Overview

This model simulates Indonesia's energy supply-demand dynamics under various crisis scenarios, including commodity-specific impacts from coal, LNG, and crude oil price shocks. It models both electricity system effects and broader macroeconomic impacts (fuel subsidies, inflation, transport disruption).

Based on Indonesia energy market data:
- 270M population, 57% urban, 5 priority cities
- PLN / ESDM energy statistics
- World Bank and Pertamina economic data

## Key Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Installed Capacity | 82 GW | PLN 2025 |
| Peak Demand | 43.5 GW | PLN 2025 |
| Coal Dependency | 61.7% | ESDM |
| Oil in Mix | 2.4% | ESDM |
| Net Oil Imports | ~600K bbl/day | Pertamina |
| Crude Oil Baseline | $80/bbl | Brent |
| Fuel Subsidy Budget | ~Rp 150T/year | APBN |
| Population | 270M | BPS |

## Crisis Scenarios Modeled

| Scenario | Severity | Annual Prob | Key Impact |
|----------|----------|-------------|------------|
| Coal Supply Disruption | 70% | 15% | -25% supply, blackouts |
| Extreme Heat Wave | 60% | 25% | -10% supply, +25% demand |
| Grid Cascade Failure | 90% | 5% | -60% supply, 150M+ affected |
| LNG Price Shock | 50% | 20% | -12% supply, electricity cost surge |
| **Crude Oil Price Shock** | **65%** | **20%** | **Oil 2x, subsidy crisis, +2.5% inflation, transport disruption** |
| Renewable Transition Gap | 40% | 30% | -8% supply, +5% demand |

### Crude Oil Price Shock — Detailed Impact Chain

```
Oil price doubles ($80 → $160/bbl)
    ├── Fiscal: Fuel subsidy (BBM) overrun ~65% (~Rp 97T+ extra)
    ├── Inflation: +2.5% CPI from fuel pass-through
    ├── Transport: 15% sector GDP loss (~$812M/month)
    ├── Currency: Rupiah pressure from widening trade deficit
    └── Electricity: Oil-fired generation (2.4%) curtailed
```

## Files

| File | Description |
|------|-------------|
| `indonesia_energy_crisis_simulation.py` | Python simulation engine — all 6 scenarios, efficiency comparison, JSON export |
| `energy-crisis-dashboard.html` | Interactive browser dashboard — scenario selection, oil-specific charts, KPIs, city impacts |
| `simulation_results.json` | Generated output (after running simulation) |

## Quick Start

### Run Python Simulation

```bash
cd indonesia-energy-crisis-model
python indonesia_energy_crisis_simulation.py
```

This will:
1. Run all 6 crisis scenarios for 2026 (including crude oil price shock)
2. Compare energy efficiency adoption rates (0% to 50%)
3. Export results to `simulation_results.json`
4. Print key insights

### Open Dashboard

Open `energy-crisis-dashboard.html` in any browser. The dashboard runs entirely client-side with:
- 6 scenario cards (including Crude Oil Price Shock)
- Year slider (2026-2030)
- Energy efficiency adoption slider (0-50%)
- Supply vs Demand chart
- Reserve margin & load shedding chart
- Energy mix breakdown
- **Oil price & fuel subsidy chart** (oil scenario only)
- **Inflation & transport loss chart** (oil scenario only)
- Efficiency adoption vs Economic Loss comparison
- City-level impact table with fuel subsidy and transport loss columns

## Key Findings

1. **Coal dependency (61.7%)** creates acute vulnerability — a 25% coal disruption causes cascading blackouts across Java-Bali affecting 30M+ people

2. **Climate amplification** is the most frequent risk (25%/year) — El Nino simultaneously increases demand (+25% AC) and reduces supply (-10% hydro)

3. **Crude oil price shock** has outsized economic impact despite oil being only 2.4% of generation mix:
   - ~Rp 159T fuel subsidy overrun
   - $5.7B+ transport sector losses
   - +2.5% inflation hitting household purchasing power
   - Rupiah depreciation from trade deficit widening

4. **LNG vs Oil**: LNG price shocks primarily affect electricity costs; oil price shocks cascade into transport, inflation, and fiscal policy

5. **Energy efficiency at 20% adoption** reduces peak demand by 2-4%, preventing ~30% of load shedding events

6. **Policy alignment**: Indonesia's RUPTL targets 23% renewable energy. The transition gap is the most probable scenario (30%/year)

## Data Sources

- PLN (State Electricity Company) — capacity & demand data
- ESDM (Ministry of Energy) — energy mix, RUPTL targets
- World Bank — economic loss estimates ($0.5M/GWh unserved)
- Pertamina — oil import volumes, fuel subsidy data
- BPS Indonesia — CPI weights, transport GDP share
- APBN (State Budget) — fuel subsidy allocations
