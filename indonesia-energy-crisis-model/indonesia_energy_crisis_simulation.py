"""
Indonesia Energy Crisis Model
==============================
Simulates Indonesia's energy supply-demand dynamics, modelling crisis
scenarios across multiple energy commodities (coal, LNG, crude oil)
and their cascading impacts on electricity, fuel subsidies, inflation,
and the transport sector.

Based on real public data sources (2024-2025):
- PLN Statistics 2024 (installed capacity, peak demand, tariffs)
- ESDM Handbook of Energy & Economic Statistics of Indonesia 2023-2024
- EIA Country Analysis Brief: Indonesia (August 2025)
- RUPTL 2025-2034 (PLN Electricity Supply Business Plan)
- BPS Statistics Indonesia (population, GDP)
- Ministry of Finance 2025 State Budget (fuel subsidies)
- IEA Enhancing Indonesia's Power System report
- Ember: Indonesia RUKN 2025 / expansion of clean power report
- World Bank economic impact estimates for developing Asia

Key scenarios modelled:
1. Coal supply disruption
2. Extreme heat wave (El Nino)
3. Grid cascade failure
4. Natural gas / LNG price shock
5. Crude oil price shock (fuel subsidy, inflation, transport)
6. Renewable transition gap

Author: Indonesia Energy Crisis Model Team
"""

import json
import math
import random
import uuid
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Indonesia Energy Constants — sourced from real public data (2025-2026)
# ---------------------------------------------------------------------------

# PLN Statistics 2024: 100.6 GW installed, 61.3 GW peak load
# RUPTL 2025-2034: +5.6 GW/yr → ~107 GW est. end-2025, ~112 GW est. mid-2026
# Solar capacity reached 1.49 GW (PV Magazine, Feb 2026)
INDONESIA_INSTALLED_CAPACITY_GW = 107.0          # Est. end-2025 (101 + ~5.6 GW added)
INDONESIA_PEAK_DEMAND_GW = 64.2                  # Est. 2025 (61.3 GW × 1.047 growth)
RESERVE_MARGIN_TARGET = 0.30                     # 30% PLN target

# BPS/Worldometer mid-2026 projection
POPULATION = 287_900_000                         # 287.9M (Worldometer mid-2026)
URBAN_POPULATION_RATIO = 0.58                    # ~58% urban

# PLN electrification data
ELECTRIFICATION_RATIO = 0.9975                   # ~99.75% (est. 2025)

# PLN tariffs: unchanged Q1 2026 (ESDM Regulation No. 7/2024)
# Residential (non-subsidized R1 1,300-2,200 VA): Rp 1,444.70/kWh
# Business B1 (450-5,500 VA): Rp 1,100/kWh
# PLN all-customer blended average: ~Rp 1,153/kWh (2024 actual)
# Electricity subsidy budget 2026: Rp 101.72T
AVERAGE_TARIFF_IDR_KWH = 1_444                   # Rp/kWh non-subsidized residential

# Electricity generation mix (ESDM 2024-2025)
# Coal still ~67-68% of electricity (IEEFA 2026, ESDM)
# NRE on-grid: 11.5% (2024 actual), RUPTL target 15.9% for 2025
# Actual NRE realization: 14.4-15.75% (Oct 2025, ESDM)
ENERGY_MIX = {
    "coal": 0.670,          # 67-68% — dominant (ESDM 2024, IEEFA 2026)
    "natural_gas": 0.177,   # 17.7% (ESDM 2024)
    "oil": 0.031,           # 3.1% fuel & BBN (ESDM 2024)
    "hydro": 0.069,         # 6.9% (ESDM 2024)
    "geothermal": 0.053,    # 5.3% (ESDM 2024)
    "solar_wind": 0.003,    # 0.3% — solar 1.49 GW capacity (PV Magazine Feb 2026)
    "biomass": 0.010,       # 1.0% (ESDM 2024)
    "other_re": 0.007,      # 0.7% (remaining NRE)
}
# NRE share target missed 9 consecutive years (IESR 2026 Outlook)
# Revised target: 23% pushed to 2030 (was 2025 under KEN 2014)

# Priority cities — population from BPS, GDP estimated from provincial GRDP
PRIORITY_CITIES = {
    "Jakarta":   {"population_m": 31.0,  "gdp_b_usd": 250, "grid_zone": "Java-Bali", "efficiency_adoption": 0.08},
    "Surabaya":  {"population_m": 3.0,   "gdp_b_usd": 60,  "grid_zone": "Java-Bali", "efficiency_adoption": 0.04},
    "Bandung":   {"population_m": 2.5,   "gdp_b_usd": 35,  "grid_zone": "Java-Bali", "efficiency_adoption": 0.05},
    "Medan":     {"population_m": 2.5,   "gdp_b_usd": 35,  "grid_zone": "Sumatra",   "efficiency_adoption": 0.02},
    "Semarang":  {"population_m": 1.8,   "gdp_b_usd": 25,  "grid_zone": "Java-Bali", "efficiency_adoption": 0.03},
    "Makassar":  {"population_m": 1.5,   "gdp_b_usd": 15,  "grid_zone": "Sulawesi",  "efficiency_adoption": 0.02},
}

# Grid zones — capacity proportional to PLN (est. 107 GW by end-2025)
# Java-Bali ~60%, Sumatra ~15%, Kalimantan ~8%, Sulawesi ~7%, Eastern ~5%
GRID_ZONES = {
    "Java-Bali":  {"capacity_gw": 64.0, "demand_gw": 42.0, "interconnected": True},
    "Sumatra":    {"capacity_gw": 16.0, "demand_gw": 10.5, "interconnected": True},
    "Kalimantan": {"capacity_gw": 8.5,  "demand_gw": 5.2,  "interconnected": False},
    "Sulawesi":   {"capacity_gw": 7.5,  "demand_gw": 4.2,  "interconnected": False},
    "Papua-NTT":  {"capacity_gw": 5.5,  "demand_gw": 2.4,  "interconnected": False},
}

# Crude oil / fuel subsidy constants (2025-2026)
# Oil consumption ~1.7M bbl/day, production ~608K bbl/day (IPA 2025)
# 2026 state budget ICP assumption: $70/bbl
# Every $1/bbl increase → Rp 7T extra fiscal impact (ESI estimate)
# Fuel reserve: only 21-23 days (Energy Council 2025)
CRUDE_OIL_BASELINE_USD_BBL = 70.0       # 2026 state budget ICP assumption
FUEL_SUBSIDY_BUDGET_B_IDR = 101_720     # Rp 101.72T electricity subsidy 2026
BBM_CONSUMPTION_MBPD = 1.70             # ~1.7M bbl/day consumption (2025)
NET_OIL_IMPORT_MBPD = 1.10              # ~1.1M bbl/day net imports (production ~600K)
IDR_PER_USD = 16_975                    # March 2026 rate (BI)
INDONESIA_GDP_B_USD = 1_510             # Est. 2026 ($1.44T × 1.051 growth)
TRANSPORT_SHARE_OF_GDP = 0.05           # transport ~5% of GDP
FUEL_SHARE_OF_CPI = 0.08               # fuel ~8% weight in CPI basket
INFLATION_CURRENT_PCT = 4.76            # Feb 2026 CPI (near 3-year high)

# Energy efficiency potential (general estimates, not platform-specific)
EFFICIENCY_POTENTIAL = {
    "hvac_optimization":    0.25,   # 20-30% → midpoint
    "lighting_retrofit":    0.50,   # 40-60% → midpoint
    "occupancy_management": 0.20,   # 15-25% → midpoint
    "peak_demand_shift":    0.15,   # 10-20% → midpoint
    "predictive_maintenance": 0.10, # 5-15% → midpoint
}


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class CrisisScenario:
    name: str
    description: str
    severity: float             # 0.0 – 1.0
    duration_days: int
    supply_reduction_pct: float # how much supply drops
    demand_increase_pct: float  # how much demand spikes
    affected_zones: List[str]
    trigger: str
    probability_annual: float   # estimated annual probability
    # Oil-specific fields (only used by crude_oil_price_shock)
    oil_price_multiplier: float = 1.0       # e.g. 2.0 = price doubles
    fuel_subsidy_overrun_pct: float = 0.0   # extra fiscal burden
    inflation_impact_pct: float = 0.0       # CPI increase
    transport_disruption_pct: float = 0.0   # transport GDP loss

@dataclass
class MonthlySnapshot:
    month: str
    demand_gw: float
    supply_gw: float
    reserve_margin: float
    deficit_gw: float
    load_shedding_gw: float
    efficiency_savings_gw: float
    energy_mix: Dict[str, float]
    crisis_active: Optional[str]
    tariff_idr_kwh: float
    co2_mt: float
    # Oil-shock specific (zero for non-oil scenarios)
    oil_price_usd_bbl: float = 0.0
    fuel_subsidy_cost_b_idr: float = 0.0
    inflation_pct: float = 0.0
    transport_loss_m_usd: float = 0.0

@dataclass
class CityImpact:
    city: str
    population_affected_m: float
    blackout_hours: float
    economic_loss_m_usd: float
    efficiency_mitigation_pct: float
    fuel_subsidy_burden_m_usd: float = 0.0
    transport_loss_m_usd: float = 0.0

@dataclass
class SimulationResult:
    scenario: str
    year: int
    monthly_data: List[dict]
    city_impacts: List[dict]
    summary: dict


# ---------------------------------------------------------------------------
# Crisis Scenarios
# ---------------------------------------------------------------------------

CRISIS_SCENARIOS = [
    CrisisScenario(
        name="coal_supply_disruption",
        description="Major coal supply disruption due to export ban reversal, mining accidents, or logistics failure. "
                    "Coal is 67-68% of electricity (ESDM 2024-2025, IEEFA 2026). "
                    "Coal production 833 Mt in 2024 (EIA), exports 615 Mt.",
        severity=0.7,
        duration_days=90,
        supply_reduction_pct=0.25,
        demand_increase_pct=0.0,
        affected_zones=["Java-Bali", "Sumatra", "Kalimantan"],
        trigger="Coal mine flooding / export policy shift / rail logistics collapse",
        probability_annual=0.15,
    ),
    CrisisScenario(
        name="extreme_heat_wave",
        description="Prolonged El Niño driven heatwave pushes temperatures above 38°C across Java. "
                    "AC demand surges while hydro output drops due to drought. "
                    "Java-Bali system already has ~6 GW overcapacity but contractual PPA constraints limit flexibility (IEA).",
        severity=0.6,
        duration_days=60,
        supply_reduction_pct=0.10,
        demand_increase_pct=0.25,
        affected_zones=["Java-Bali", "Sulawesi"],
        trigger="El Niño event / climate change amplification",
        probability_annual=0.25,
    ),
    CrisisScenario(
        name="grid_cascade_failure",
        description="Cascading grid failure triggered by transmission line fault on the Java-Bali "
                    "interconnected system. Java-Bali carries 61 GW capacity serving 60% of national demand. "
                    "Coal IPP capacity = 2/3 of Java-Bali peak demand (IEA), creating inflexible baseload.",
        severity=0.9,
        duration_days=7,
        supply_reduction_pct=0.60,
        demand_increase_pct=0.0,
        affected_zones=["Java-Bali"],
        trigger="Transmission line failure / transformer overload / cyberattack",
        probability_annual=0.05,
    ),
    CrisisScenario(
        name="natural_gas_price_shock",
        description="Global LNG price spike (3x) makes gas-fired generation uneconomic. "
                    "Gas is 17.7% of generation mix (ESDM 2024). "
                    "Gas plants reduce output; coal plants (48% utilization in 2023) cannot ramp fast enough.",
        severity=0.5,
        duration_days=180,
        supply_reduction_pct=0.12,
        demand_increase_pct=0.0,
        affected_zones=["Java-Bali", "Sumatra", "Kalimantan", "Sulawesi"],
        trigger="Geopolitical conflict / LNG market disruption",
        probability_annual=0.20,
    ),
    CrisisScenario(
        name="crude_oil_price_shock",
        description="Global crude oil price spike (2x) due to Middle East conflict or OPEC+ cuts. "
                    "Indonesia imports ~1.1M bbl/day (production only ~608K bbl/day). "
                    "2026 budget assumes ICP $70/bbl — every $1 increase = Rp 7T fiscal impact (ESI). "
                    "Fuel reserve only 21-23 days (Energy Council). Inflation already 4.76% (Feb 2026).",
        severity=0.65,
        duration_days=180,
        supply_reduction_pct=0.03,       # oil-fired plants curtailed
        demand_increase_pct=0.0,
        affected_zones=["Java-Bali", "Sumatra", "Kalimantan", "Sulawesi", "Papua-NTT"],
        trigger="Middle East conflict / OPEC+ production cuts / sanctions disruption",
        probability_annual=0.20,
        oil_price_multiplier=2.0,        # price doubles from $70 to $140/bbl
        fuel_subsidy_overrun_pct=0.65,   # 65% budget overrun on fuel subsidies
        inflation_impact_pct=2.5,        # 2.5% additional CPI inflation
        transport_disruption_pct=0.15,   # 15% transport GDP loss
    ),
    CrisisScenario(
        name="renewable_transition_gap",
        description="Coal plant retirements outpace renewable + storage buildout. "
                    "RUPTL 2025-2034 targets 42.6 GW NRE + 10.3 GW storage. "
                    "NRE target missed 9 consecutive years (IESR 2026). "
                    "2025 NRE realization only 14.4% vs 15.9% RUPTL target. "
                    "23% target pushed from 2025 to 2030.",
        severity=0.4,
        duration_days=365,
        supply_reduction_pct=0.08,
        demand_increase_pct=0.05,
        affected_zones=["Java-Bali", "Sumatra", "Sulawesi", "Kalimantan", "Papua-NTT"],
        trigger="Policy-driven coal retirement without adequate replacement",
        probability_annual=0.30,
    ),
]


# ---------------------------------------------------------------------------
# Simulation Engine
# ---------------------------------------------------------------------------

class IndonesiaEnergyCrisisSimulation:
    """
    Models Indonesia's energy system month-by-month for a given year,
    injecting crisis scenarios and computing impacts on cities,
    including oil-specific fiscal and macroeconomic effects.
    """

    def __init__(self, year: int = 2026, efficiency_adoption_rate: float = 0.05):
        """
        Args:
            year: Simulation year
            efficiency_adoption_rate: Fraction of commercial buildings with efficiency measures (0-1)
        """
        self.year = year
        self.efficiency_adoption_rate = efficiency_adoption_rate
        self.results: List[SimulationResult] = []

        # Demand growth ~4.7% per year (PLN RUPTL 2025-2034 / Ember projection)
        # 306 TWh (2024) → 445 TWh (2030), peak 61.3 GW (2024) → ~77 GW (2030)
        years_from_base = year - 2026
        self.demand_growth = 1.047 ** years_from_base

        # RUPTL 2025-2030: 27.9 GW new capacity over 5 years ≈ 5.6 GW/year
        self.capacity_gw = INDONESIA_INSTALLED_CAPACITY_GW + (5.6 * years_from_base)

    def _seasonal_demand_factor(self, month: int) -> float:
        """Indonesia's demand peaks in hot dry season (Sep-Nov) and Ramadan."""
        seasonal = {
            1: 0.95, 2: 0.93, 3: 0.97,    # Ramadan often Mar-Apr
            4: 1.00, 5: 0.98, 6: 0.96,
            7: 0.97, 8: 1.00, 9: 1.05,     # Dry season peak
            10: 1.08, 11: 1.06, 12: 1.02,  # Peak before wet season
        }
        return seasonal.get(month, 1.0)

    def _compute_co2(self, generation_gwh: float, mix: Dict[str, float]) -> float:
        """Compute monthly CO2 emissions in million tonnes."""
        # Emission factors (tCO2/GWh)
        factors = {
            "coal": 900, "natural_gas": 400, "oil": 700,
            "hydro": 4, "geothermal": 15, "solar_wind": 10,
            "biomass": 50, "other_re": 20,
        }
        total = sum(generation_gwh * mix.get(fuel, 0) * factors.get(fuel, 0) for fuel in mix)
        return total / 1_000_000  # convert to Mt

    def _efficiency_savings_gw(self, demand_gw: float, adoption_rate: float) -> float:
        """
        Calculate demand reduction from energy efficiency measures.
        """
        # Commercial buildings are ~40% of electricity demand in urban Indonesia
        commercial_share = 0.40
        commercial_demand = demand_gw * commercial_share

        # Weighted average savings across efficiency measures
        avg_savings = sum(EFFICIENCY_POTENTIAL.values()) / len(EFFICIENCY_POTENTIAL)

        # Only adopted buildings contribute
        savings = commercial_demand * adoption_rate * avg_savings
        return round(savings, 3)

    def _compute_oil_impact(self, scenario: 'CrisisScenario', is_crisis: bool) -> dict:
        """
        Compute crude oil price shock impacts: fuel subsidy overrun,
        inflation, and transport sector loss.
        """
        if not is_crisis or scenario.oil_price_multiplier <= 1.0:
            return {"oil_price": CRUDE_OIL_BASELINE_USD_BBL, "subsidy_cost": 0, "inflation": 0, "transport_loss": 0}

        oil_price = CRUDE_OIL_BASELINE_USD_BBL * scenario.oil_price_multiplier

        # Fuel subsidy overrun (monthly)
        # Extra cost = (new price - baseline) * net imports * 30 days
        extra_import_cost_usd = (oil_price - CRUDE_OIL_BASELINE_USD_BBL) * NET_OIL_IMPORT_MBPD * 1_000_000 * 30
        subsidy_cost_b_idr = (extra_import_cost_usd * IDR_PER_USD) / 1e12  # in trillion IDR

        # Inflation impact (fuel price pass-through)
        inflation = scenario.inflation_impact_pct

        # Transport GDP loss (monthly, in $M USD)
        # Indonesia GDP $1.4T (IMF 2024), transport 5%, disruption pct per month
        annual_transport_gdp_m = INDONESIA_GDP_B_USD * 1000 * TRANSPORT_SHARE_OF_GDP
        transport_loss_m = annual_transport_gdp_m * scenario.transport_disruption_pct / 12

        return {
            "oil_price": round(oil_price, 2),
            "subsidy_cost": round(subsidy_cost_b_idr, 2),
            "inflation": round(inflation, 2),
            "transport_loss": round(transport_loss_m, 1),
        }

    def _compute_tariff(self, base_tariff: float, reserve_margin: float,
                        crisis_active: bool) -> float:
        """Tariff increases when reserve margin drops or during crisis."""
        tariff = base_tariff
        if reserve_margin < 0.15:
            tariff *= 1.15  # 15% surcharge
        if reserve_margin < 0.05:
            tariff *= 1.30  # additional 30%
        if crisis_active:
            tariff *= 1.10  # crisis surcharge
        return round(tariff)

    def run_scenario(self, scenario: CrisisScenario) -> SimulationResult:
        """Run a full year simulation under a given crisis scenario."""
        print(f"\n{'='*70}")
        print(f"  SCENARIO: {scenario.name.upper().replace('_', ' ')}")
        print(f"  Severity: {scenario.severity:.0%} | Duration: {scenario.duration_days}d")
        print(f"  Affected zones: {', '.join(scenario.affected_zones)}")
        print(f"  Efficiency adoption: {self.efficiency_adoption_rate:.1%}")
        if scenario.oil_price_multiplier > 1.0:
            print(f"  Oil price: ${CRUDE_OIL_BASELINE_USD_BBL}/bbl → ${CRUDE_OIL_BASELINE_USD_BBL * scenario.oil_price_multiplier}/bbl")
        print(f"{'='*70}")

        # Determine crisis months
        crisis_start_month = random.randint(1, max(1, 12 - (scenario.duration_days // 30)))
        crisis_end_month = min(12, crisis_start_month + (scenario.duration_days // 30))

        monthly_data = []
        total_deficit = 0
        total_shedding = 0
        total_efficiency_savings = 0
        total_subsidy_cost = 0
        total_transport_loss = 0

        for month in range(1, 13):
            month_name = datetime(self.year, month, 1).strftime("%b %Y")
            is_crisis = crisis_start_month <= month <= crisis_end_month

            # Base demand with growth and seasonal factor
            base_demand = INDONESIA_PEAK_DEMAND_GW * self.demand_growth
            demand = base_demand * self._seasonal_demand_factor(month)

            # Crisis demand increase
            if is_crisis:
                demand *= (1 + scenario.demand_increase_pct)

            # Supply computation
            supply = self.capacity_gw * 0.65  # typical availability factor
            if is_crisis:
                # Reduce supply in affected zones proportionally
                affected_capacity_share = sum(
                    GRID_ZONES[z]["capacity_gw"] for z in scenario.affected_zones
                ) / self.capacity_gw
                supply *= (1 - scenario.supply_reduction_pct * affected_capacity_share)

            # Efficiency demand reduction
            eff_savings = self._efficiency_savings_gw(demand, self.efficiency_adoption_rate)
            effective_demand = demand - eff_savings

            # Deficit and load shedding
            deficit = max(0, effective_demand - supply)
            reserve_margin = (supply - effective_demand) / supply if supply > 0 else -1
            load_shedding = deficit * 0.8  # 80% of deficit results in rolling blackouts

            # Energy mix adjustment during crisis
            mix = dict(ENERGY_MIX)
            if is_crisis and "coal" in scenario.trigger.lower():
                mix["coal"] *= (1 - scenario.supply_reduction_pct)
                mix["natural_gas"] += mix["coal"] * scenario.supply_reduction_pct * 0.3
            if is_crisis and "gas" in scenario.name:
                mix["natural_gas"] *= (1 - scenario.supply_reduction_pct)
                mix["coal"] += mix["natural_gas"] * scenario.supply_reduction_pct * 0.5
            if is_crisis and "oil" in scenario.name:
                mix["oil"] *= (1 - scenario.supply_reduction_pct)
                mix["coal"] += mix["oil"] * scenario.supply_reduction_pct * 0.7

            # Normalize mix
            total_mix = sum(mix.values())
            mix = {k: round(v / total_mix, 4) for k, v in mix.items()}

            # CO2 (approximate monthly GWh from GW peak * hours * load factor)
            monthly_gwh = supply * 730 * 0.7
            co2 = self._compute_co2(monthly_gwh, mix)

            # Tariff
            tariff = self._compute_tariff(AVERAGE_TARIFF_IDR_KWH, reserve_margin, is_crisis)

            # Oil price shock impacts
            oil_impact = self._compute_oil_impact(scenario, is_crisis)

            snapshot = MonthlySnapshot(
                month=month_name,
                demand_gw=round(demand, 2),
                supply_gw=round(supply, 2),
                reserve_margin=round(reserve_margin, 4),
                deficit_gw=round(deficit, 2),
                load_shedding_gw=round(load_shedding, 2),
                efficiency_savings_gw=round(eff_savings, 3),
                energy_mix=mix,
                crisis_active=scenario.name if is_crisis else None,
                tariff_idr_kwh=tariff,
                co2_mt=round(co2, 2),
                oil_price_usd_bbl=oil_impact["oil_price"],
                fuel_subsidy_cost_b_idr=oil_impact["subsidy_cost"],
                inflation_pct=oil_impact["inflation"],
                transport_loss_m_usd=oil_impact["transport_loss"],
            )
            monthly_data.append(asdict(snapshot))
            total_deficit += deficit
            total_shedding += load_shedding
            total_efficiency_savings += eff_savings
            total_subsidy_cost += oil_impact["subsidy_cost"]
            total_transport_loss += oil_impact["transport_loss"]

            # Print monthly status
            status = "CRISIS" if is_crisis else "NORMAL"
            margin_str = f"{reserve_margin:.1%}"
            oil_str = f" | Oil: ${oil_impact['oil_price']}/bbl" if oil_impact["oil_price"] > CRUDE_OIL_BASELINE_USD_BBL else ""
            print(f"  {month_name:>8} | {status:>7} | Demand: {demand:.1f} GW | "
                  f"Supply: {supply:.1f} GW | Margin: {margin_str:>6} | "
                  f"Eff Savings: {eff_savings:.2f} GW | Deficit: {deficit:.1f} GW{oil_str}")

        # City-level impact analysis
        city_impacts = []
        for city, info in PRIORITY_CITIES.items():
            zone = info["grid_zone"]
            zone_affected = zone in scenario.affected_zones

            if zone_affected and (total_deficit > 0 or total_transport_loss > 0):
                # Blackout hours proportional to city's share of zone demand
                zone_demand = GRID_ZONES[zone]["demand_gw"]
                city_demand_share = info["population_m"] / 50.0  # rough share
                blackout_hours = (total_shedding / zone_demand) * scenario.duration_days * 2 * city_demand_share if total_deficit > 0 else 0
                blackout_hours = min(blackout_hours, scenario.duration_days * 8)  # cap at 8h/day

                # Economic loss: ~$0.5M per GWh unserved (World Bank estimate for developing Asia)
                unserved_gwh = (total_shedding * city_demand_share * 730 * 0.3)
                economic_loss = unserved_gwh * 0.5

                # Efficiency mitigation
                city_adoption = max(info["efficiency_adoption"], self.efficiency_adoption_rate)
                mitigation = city_adoption * sum(EFFICIENCY_POTENTIAL.values()) / len(EFFICIENCY_POTENTIAL) * 100

                # Oil-specific city impacts
                city_gdp_share = info["gdp_b_usd"] / INDONESIA_GDP_B_USD  # share of national GDP
                city_fuel_subsidy = total_subsidy_cost * city_gdp_share
                city_transport_loss = total_transport_loss * city_gdp_share
                economic_loss += city_transport_loss  # transport loss adds to total
            else:
                blackout_hours = 0
                economic_loss = 0
                mitigation = 0
                city_fuel_subsidy = 0
                city_transport_loss = 0

            impact = CityImpact(
                city=city,
                population_affected_m=round(info["population_m"] if zone_affected else 0, 1),
                blackout_hours=round(blackout_hours, 1),
                economic_loss_m_usd=round(economic_loss, 1),
                efficiency_mitigation_pct=round(mitigation, 1),
                fuel_subsidy_burden_m_usd=round(city_fuel_subsidy * 1000 / IDR_PER_USD, 1),  # convert T IDR to $M
                transport_loss_m_usd=round(city_transport_loss, 1),
            )
            city_impacts.append(asdict(impact))

        # Summary
        total_economic_loss = sum(c["economic_loss_m_usd"] for c in city_impacts)
        total_population_affected = sum(c["population_affected_m"] for c in city_impacts)

        summary = {
            "scenario": scenario.name,
            "severity": scenario.severity,
            "year": self.year,
            "efficiency_adoption_rate": self.efficiency_adoption_rate,
            "total_deficit_gw_months": round(total_deficit, 2),
            "total_load_shedding_gw_months": round(total_shedding, 2),
            "total_efficiency_savings_gw_months": round(total_efficiency_savings, 2),
            "total_economic_loss_m_usd": round(total_economic_loss, 1),
            "total_population_affected_m": round(total_population_affected, 1),
            "peak_tariff_idr_kwh": max(m["tariff_idr_kwh"] for m in monthly_data),
            "avg_co2_mt_per_month": round(sum(m["co2_mt"] for m in monthly_data) / 12, 2),
            "crisis_months": crisis_end_month - crisis_start_month + 1,
            "worst_month_deficit_gw": max(m["deficit_gw"] for m in monthly_data),
            "demand_reduced_by_efficiency_pct": round(
                (total_efficiency_savings / (sum(m["demand_gw"] for m in monthly_data))) * 100, 2
            ) if total_efficiency_savings > 0 else 0,
            # Oil-specific summary fields
            "total_fuel_subsidy_overrun_t_idr": round(total_subsidy_cost, 2),
            "total_transport_loss_m_usd": round(total_transport_loss, 1),
            "peak_oil_price_usd_bbl": max(m["oil_price_usd_bbl"] for m in monthly_data),
            "peak_inflation_pct": max(m["inflation_pct"] for m in monthly_data),
        }

        print(f"\n  SUMMARY:")
        print(f"    Total deficit:           {summary['total_deficit_gw_months']:.1f} GW-months")
        print(f"    Efficiency savings:      {summary['total_efficiency_savings_gw_months']:.1f} GW-months")
        print(f"    Demand reduced:          {summary['demand_reduced_by_efficiency_pct']:.2f}%")
        print(f"    Economic loss:           ${summary['total_economic_loss_m_usd']:.0f}M USD")
        print(f"    Population affected:     {summary['total_population_affected_m']:.1f}M people")
        print(f"    Peak tariff:             Rp {summary['peak_tariff_idr_kwh']:,}/kWh")
        if summary['peak_oil_price_usd_bbl'] > CRUDE_OIL_BASELINE_USD_BBL:
            print(f"    Peak oil price:          ${summary['peak_oil_price_usd_bbl']}/bbl")
            print(f"    Fuel subsidy overrun:    Rp {summary['total_fuel_subsidy_overrun_t_idr']:.1f}T")
            print(f"    Transport sector loss:   ${summary['total_transport_loss_m_usd']:.0f}M USD")
            print(f"    Peak inflation impact:   +{summary['peak_inflation_pct']:.1f}%")

        result = SimulationResult(
            scenario=scenario.name,
            year=self.year,
            monthly_data=monthly_data,
            city_impacts=city_impacts,
            summary=summary,
        )
        self.results.append(result)
        return result

    def run_all_scenarios(self) -> List[SimulationResult]:
        """Run all crisis scenarios."""
        print(f"\n{'#'*70}")
        print(f"  INDONESIA ENERGY CRISIS MODEL — Year {self.year}")
        print(f"  Efficiency Adoption Rate: {self.efficiency_adoption_rate:.1%}")
        print(f"  Installed Capacity: {self.capacity_gw:.1f} GW")
        print(f"  Base Peak Demand: {INDONESIA_PEAK_DEMAND_GW * self.demand_growth:.1f} GW")
        print(f"{'#'*70}")

        results = []
        for scenario in CRISIS_SCENARIOS:
            results.append(self.run_scenario(scenario))
        return results

    def compare_efficiency_adoption(self, scenario: CrisisScenario,
                                    adoption_rates: List[float] = None) -> Dict:
        """
        Compare outcomes under different energy efficiency adoption rates.
        """
        if adoption_rates is None:
            adoption_rates = [0.0, 0.05, 0.10, 0.20, 0.35, 0.50]

        print(f"\n{'='*70}")
        print(f"  EFFICIENCY ADOPTION COMPARISON: {scenario.name.upper().replace('_', ' ')}")
        print(f"{'='*70}")
        print(f"  {'Adoption':>10} | {'Deficit GW-mo':>14} | {'Savings GW-mo':>14} | {'Loss $M':>10} | {'Mitigation':>10}")
        print(f"  {'-'*10}-+-{'-'*14}-+-{'-'*14}-+-{'-'*10}-+-{'-'*10}")

        comparison = []
        for rate in adoption_rates:
            original_rate = self.efficiency_adoption_rate
            self.efficiency_adoption_rate = rate
            result = self.run_scenario(scenario)
            self.efficiency_adoption_rate = original_rate

            s = result.summary
            baseline_loss = comparison[0]["economic_loss_m_usd"] if comparison else s["total_economic_loss_m_usd"]
            mitigation = ((baseline_loss - s["total_economic_loss_m_usd"]) / baseline_loss * 100) if baseline_loss > 0 else 0

            row = {
                "adoption_rate": rate,
                "deficit_gw_months": s["total_deficit_gw_months"],
                "efficiency_savings_gw_months": s["total_efficiency_savings_gw_months"],
                "economic_loss_m_usd": s["total_economic_loss_m_usd"],
                "loss_mitigation_pct": round(mitigation, 1),
            }
            comparison.append(row)
            print(f"  {rate:>9.0%} | {s['total_deficit_gw_months']:>14.2f} | "
                  f"{s['total_efficiency_savings_gw_months']:>14.2f} | "
                  f"${s['total_economic_loss_m_usd']:>9.0f} | {mitigation:>9.1f}%")

        return {"scenario": scenario.name, "comparison": comparison}

    def export_json(self, filepath: str = "simulation_results.json"):
        """Export all results to JSON for dashboard consumption."""
        output = {
            "metadata": {
                "model": "Indonesia Energy Crisis Model v3.0 — Real Public Data",
                "generated_at": datetime.now().isoformat(),
                "year": self.year,
                "efficiency_adoption_rate": self.efficiency_adoption_rate,
                "installed_capacity_gw": self.capacity_gw,
                "base_peak_demand_gw": round(INDONESIA_PEAK_DEMAND_GW * self.demand_growth, 2),
                "crude_oil_baseline_usd_bbl": CRUDE_OIL_BASELINE_USD_BBL,
            },
            "constants": {
                "energy_mix": ENERGY_MIX,
                "grid_zones": {k: v for k, v in GRID_ZONES.items()},
                "priority_cities": PRIORITY_CITIES,
                "efficiency_potential": EFFICIENCY_POTENTIAL,
                "oil_constants": {
                    "baseline_price_usd_bbl": CRUDE_OIL_BASELINE_USD_BBL,
                    "fuel_subsidy_budget_b_idr": FUEL_SUBSIDY_BUDGET_B_IDR,
                    "bbm_consumption_mbpd": BBM_CONSUMPTION_MBPD,
                    "net_oil_import_mbpd": NET_OIL_IMPORT_MBPD,
                },
            },
            "scenarios": [asdict(s) for s in CRISIS_SCENARIOS],
            "results": [asdict(r) for r in self.results],
        }
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\nResults exported to {filepath}")
        return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("  INDONESIA ENERGY CRISIS MODEL v3.0 — Real Public Data (2024-2025)")
    print("  Multi-commodity: Coal, LNG, Crude Oil, Renewables")
    print("  Modeling energy supply-demand dynamics & macroeconomic impacts")
    print("=" * 70)

    # Run baseline simulation (current ~5% efficiency adoption)
    sim = IndonesiaEnergyCrisisSimulation(year=2026, efficiency_adoption_rate=0.05)
    sim.run_all_scenarios()

    # Compare efficiency adoption impact for key scenarios
    print("\n\n" + "#" * 70)
    print("  EFFICIENCY ADOPTION ANALYSIS")
    print("#" * 70)

    renewable_gap = CRISIS_SCENARIOS[5]  # renewable_transition_gap (most probable)
    heat_wave = CRISIS_SCENARIOS[1]      # extreme_heat_wave
    oil_shock = CRISIS_SCENARIOS[4]      # crude_oil_price_shock

    sim.compare_efficiency_adoption(renewable_gap)
    sim.compare_efficiency_adoption(heat_wave)

    # Export results
    export_path = "/home/user/Smart-Home-and-Smart-Office-System/indonesia-energy-crisis-model/simulation_results.json"
    data = sim.export_json(export_path)

    # Print key insights
    print("\n" + "=" * 70)
    print("  KEY INSIGHTS — INDONESIA ENERGY CRISIS MODEL")
    print("=" * 70)
    print("""
    1. COAL DEPENDENCY RISK: Coal is 67-68% of electricity (ESDM/IEEFA).
       Coal capacity alone is 80 GW of 120 GW total (on+off grid).
       Production record 833 Mt in 2024 (EIA). A 25% supply disruption
       causes cascading blackouts across Java-Bali (~64 GW, 60% of national).

    2. CLIMATE AMPLIFICATION: El Nino heatwaves simultaneously increase
       demand (+25% AC load) and reduce supply (-10% hydro). Java-Bali
       has structural overcapacity but coal IPP PPA constraints limit
       dispatch flexibility (IEA). Data centers adding 1.44→3.56 GW by 2030.

    3. CRUDE OIL VULNERABILITY: Indonesia imports ~1.1M bbl/day
       (production only ~608K bbl/day). 2026 state budget assumes
       ICP $70/bbl — every $1 increase = Rp 7T fiscal impact (ESI).
       - FISCAL: Electricity subsidy Rp 101.72T (2026 budget)
       - INFLATION: Already 4.76% in Feb 2026 (near 3-year high)
       - RESERVES: Fuel reserve only 21-23 days (Energy Council)
       - CURRENCY: Rupiah at Rp 16,975/USD (Mar 2026), down -1.73% YTD
       If oil averages $92/bbl, fiscal deficit widens to 3.6% of GDP.

    4. LNG PRICE SENSITIVITY: Gas is 17.7% of generation (ESDM 2024).
       Global LNG price spikes (3x) reduce gas-fired output 12%.
       Coal capacity utilization already low at 48%, limiting ability
       to compensate quickly.

    5. ENERGY EFFICIENCY POTENTIAL: Key demand-side measures include:
       - HVAC optimization (25% savings) — biggest single lever
       - Lighting retrofit (50% savings) — fastest ROI
       - Peak demand shifting (15% savings) — grid stability
       - Occupancy management (20% savings) — commercial buildings
       At 20% adoption, these can reduce peak demand by 2-4%.

    6. RENEWABLE TRANSITION GAP: NRE target missed 9 consecutive years
       (IESR Indonesia Energy Transition Outlook 2026). 2025 realization
       only 14.4% vs 15.9% RUPTL target (Oct 2025, ESDM). 23% target
       pushed from 2025 to 2030. RUPTL 2025-2034 plans 42.6 GW NRE +
       10.3 GW storage, but still includes 16.6 GW new fossil capacity.

    DATA SOURCES (verified 2025-2026):
    - PLN Statistics 2024 (capacity 101 GW, peak 61.3 GW)
    - ESDM/Deputy Minister (coal 67%, generation mix)
    - EIA Country Analysis Brief: Indonesia (Aug 2025)
    - RUPTL 2025-2034 (69.5 GW new capacity plan)
    - IEEFA: Can Indonesia Pivot in 2026? (Jan 2026)
    - IESR: Indonesia Energy Transition Outlook 2026
    - IMF Article IV Consultation (Jan 2026: GDP $1.44T, growth 5.1%)
    - PV Magazine (Feb 2026: solar 1.49 GW)
    - 2026 State Budget (ICP $70/bbl, electricity subsidy Rp 101.72T)
    - Energy Council (fuel reserve 21-23 days)
    - Bank Indonesia (Rupiah Rp 16,975/USD, Mar 2026)
    """)

    return data


if __name__ == "__main__":
    main()
