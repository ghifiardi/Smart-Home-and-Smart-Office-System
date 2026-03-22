# Indonesia Energy Crisis Model v3.0

**Multi-Commodity Energy Supply-Demand Simulation — Coal, LNG, Crude Oil & Renewables**

*Based on verified public data from 2025-2026 sources*

## Overview

This model simulates Indonesia's energy supply-demand dynamics under various crisis scenarios, including commodity-specific impacts from coal, LNG, and crude oil price shocks. It models both electricity system effects and broader macroeconomic impacts (fuel subsidies, inflation, transport disruption).

## Key Parameters (2025-2026 Data)

| Parameter | Value | Source |
|-----------|-------|--------|
| Installed Capacity | 107 GW (est. end-2025) | PLN 2024 (101 GW) + RUPTL additions |
| Peak Demand | 64.2 GW (est. 2025) | PLN 2024 (61.3 GW) × 4.7% growth |
| Coal in Generation | 67-68% | ESDM 2024-2025, IEEFA 2026 |
| Gas in Generation | 17.7% | ESDM 2024 |
| Oil in Generation | 3.1% | ESDM 2024 |
| NRE Share (actual) | 14.4% (Oct 2025) | ESDM, vs 15.9% RUPTL target |
| Solar Capacity | 1.49 GW | PV Magazine, Feb 2026 |
| Oil Consumption | ~1.7M bbl/day | IPA 2025 |
| Oil Production | ~608K bbl/day | IPA 2025 |
| Net Oil Imports | ~1.1M bbl/day | EIA 2025 |
| Oil Price (ICP) | $70/bbl | 2026 State Budget assumption |
| Electricity Subsidy | Rp 101.72T | 2026 State Budget |
| Tariff (non-subsidized) | Rp 1,444.70/kWh | PLN Q1 2026 (unchanged) |
| Exchange Rate | Rp 16,975/USD | Bank Indonesia, Mar 2026 |
| GDP | ~$1.51T | IMF Jan 2026 (5.1% growth) |
| Inflation | 4.76% | Feb 2026 CPI (near 3-year high) |
| Population | 287.9M | Worldometer mid-2026 |
| Fuel Reserve | 21-23 days | Energy Council 2025 |

## Crisis Scenarios Modeled

| Scenario | Severity | Annual Prob | Key Impact |
|----------|----------|-------------|------------|
| Coal Supply Disruption | 70% | 15% | -25% supply, coal is 80 GW of 120 GW total capacity |
| Extreme Heat Wave | 60% | 25% | -10% supply, +25% demand, PPA constraints limit flexibility |
| Grid Cascade Failure | 90% | 5% | -60% supply on Java-Bali (64 GW, 60% of national) |
| LNG Price Shock | 50% | 20% | -12% supply, coal at 48% utilization can't compensate |
| **Crude Oil Price Shock** | **65%** | **20%** | **Oil 2x ($70→$140), subsidy crisis, +2.5% inflation** |
| Renewable Transition Gap | 40% | 30% | NRE target missed 9 years running (IESR 2026) |

### Crude Oil Price Shock — Detailed Impact Chain

```
Oil price doubles ($70 → $140/bbl, 2026 State Budget ICP = $70)
    ├── Fiscal: Every $1/bbl increase = Rp 7T extra cost (ESI)
    │          At $140/bbl → Rp 490T+ additional fiscal burden
    │          Fiscal deficit widens to 3.6% of GDP if oil averages $92
    ├── Inflation: +2.5% CPI (already 4.76% in Feb 2026, above BI target)
    ├── Transport: 15% sector GDP loss (~$875M/month)
    ├── Currency: Rupiah at Rp 16,975 (Mar 2026), -1.73% YTD
    ├── Reserves: Fuel reserve only 21-23 days (Energy Council)
    └── Electricity: Oil-fired generation (3.1%) curtailed
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
4. Print key insights with data source citations

### Open Dashboard

Open `energy-crisis-dashboard.html` in any browser. The dashboard runs entirely client-side with:
- 6 scenario cards (including Crude Oil Price Shock)
- Year slider (2026-2030)
- Energy efficiency adoption slider (0-50%)
- Supply vs Demand chart
- Reserve margin & load shedding chart
- Energy mix breakdown (67% coal dominant)
- **Oil price & fuel subsidy chart** (oil scenario only)
- **Inflation & transport loss chart** (oil scenario only)
- Efficiency adoption vs Economic Loss comparison
- City-level impact table (6 cities including Makassar)

## Key Findings

1. **Coal dependency (67-68%)** creates acute vulnerability — coal capacity alone is 80 GW of 120 GW total (on+off grid). A 25% coal disruption causes cascading blackouts across Java-Bali

2. **Climate amplification** is the most frequent risk (25%/year) — El Nino simultaneously increases demand (+25% AC) and reduces supply (-10% hydro). Coal IPP PPA constraints limit dispatch flexibility (IEA)

3. **Crude oil price shock** has outsized economic impact despite oil being only 3.1% of generation:
   - 2026 budget assumes ICP $70/bbl — every $1 increase = Rp 7T fiscal impact
   - Production only 608K bbl/day vs 1.7M consumption (refineries meet ~60%)
   - Inflation already 4.76% (Feb 2026), above BI target of 1.5-3.5%
   - Fuel reserve only 21-23 days
   - Rupiah at Rp 16,975/USD, weakening further

4. **Renewable transition gap** is the most probable scenario (30%/year) — NRE target missed 9 consecutive years (IESR 2026). 2025 NRE realization only 14.4% vs 15.9% RUPTL target. 23% target pushed from 2025 to 2030

5. **Energy efficiency at 20% adoption** reduces peak demand by 2-4%, preventing ~30% of load shedding events

6. **RUPTL 2025-2034** plans 69.5 GW new capacity (76% NRE+storage), but still includes 16.6 GW new fossil (including 1.4 GW coal)

## Data Sources (Verified 2025-2026)

| Source | Data Used | Date |
|--------|-----------|------|
| PLN Statistics 2024 | Installed capacity (101 GW), peak demand (61.3 GW) | 2024 |
| ESDM / Deputy Minister | Generation mix (coal 67%, gas 17.7%) | Aug 2024 |
| EIA Country Analysis Brief | Oil production, imports, consumption | Aug 2025 |
| RUPTL 2025-2034 | 69.5 GW new capacity plan, regional breakdown | May 2025 |
| IEEFA | "Can Indonesia Pivot in 2026?" — coal 68% of electricity | Jan 2026 |
| IESR | Indonesia Energy Transition Outlook 2026 — NRE missed 9 years | 2026 |
| IMF Article IV Consultation | GDP $1.44T (2025), 5.1% growth forecast | Jan 2026 |
| PV Magazine | Solar capacity reached 1.49 GW | Feb 2026 |
| 2026 State Budget | ICP $70/bbl, electricity subsidy Rp 101.72T | 2025 |
| Bank Indonesia | Rupiah Rp 16,975/USD, rate 4.75% | Mar 2026 |
| BPS / Worldometer | Population 287.9M (mid-2026) | 2026 |
| Energy Council | Fuel reserve 21-23 days | 2025 |
| IEA | Java-Bali PPA constraints, power system analysis | 2024 |
| Ember | RUKN 2025, demand growth 4.7%/yr projection | 2025 |
| ESI (Energy Shift Institute) | Every $1/bbl = Rp 7T fiscal impact | 2026 |
| Asia Times | Refineries meet only ~60% of demand | 2025 |
| IPA (Indonesia Petroleum Assoc.) | Oil production 608K bbl/day | 2025 |
