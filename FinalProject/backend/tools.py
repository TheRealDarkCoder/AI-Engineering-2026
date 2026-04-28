import math

INDUSTRY_TAM = {
    "food": 9_000_000_000_000,
    "transport": 8_000_000_000_000,
    "education": 6_000_000_000_000,
    "finance": 22_000_000_000_000,
    "health": 4_000_000_000_000,
    "retail": 5_000_000_000_000,
    "real estate": 3_000_000_000_000,
    "travel": 1_500_000_000_000,
    "entertainment": 2_500_000_000_000,
    "software": 1_000_000_000_000,
    "gaming": 300_000_000_000,
    "fitness": 100_000_000_000,
    "social": 500_000_000_000,
    "pet": 200_000_000_000,
    "fashion": 1_700_000_000_000,
    "agriculture": 3_500_000_000_000,
    "energy": 9_000_000_000_000,
}

GEO_MULTIPLIER = {
    "global": 1.0,
    "us": 0.30,
    "europe": 0.20,
    "asia": 0.35,
    "latin america": 0.08,
}


def run_financial_projection(
    customer_acquisition_cost: float,
    monthly_fee: float,
    estimated_users: int,
) -> dict:
    """Compute burn rate, break-even, funding required, and ROI for a startup."""
    monthly_revenue = monthly_fee * estimated_users
    monthly_cac_burn = (customer_acquisition_cost * estimated_users) / 12
    # Real startups burn salaries, infra, support on top of acquisition cost.
    # Model that as 30 % of revenue (floored at $8 K/mo so even tiny startups feel it).
    operating_overhead = max(8_000, monthly_revenue * 0.30)
    total_monthly_burn = monthly_cac_burn + operating_overhead
    funding_required = customer_acquisition_cost * estimated_users

    net_monthly = monthly_revenue - total_monthly_burn
    if net_monthly <= 0:
        break_even_months = None
        roi_at_break_even = None
    else:
        break_even_months = math.ceil(funding_required / net_monthly)
        roi_at_break_even = round(
            (monthly_revenue * break_even_months) / funding_required, 2
        )

    return {
        "monthly_revenue_usd": round(monthly_revenue, 2),
        "monthly_burn_rate_usd": round(total_monthly_burn, 2),
        "operating_overhead_usd": round(operating_overhead, 2),
        "funding_required_usd": round(funding_required, 2),
        "break_even_months": break_even_months,
        "roi_at_break_even": roi_at_break_even,
    }


def estimate_market_size(
    industry: str,
    target_demographic: str,
    geography: str = "global",
) -> dict:
    """Estimate TAM / SAM / SOM for an industry and target demographic."""
    industry_lower = industry.lower()
    tam_base = None
    matched_keyword = None

    for keyword, value in INDUSTRY_TAM.items():
        if keyword in industry_lower:
            tam_base = value
            matched_keyword = keyword
            break

    confidence = "HIGH" if tam_base is not None else "LOW"
    if tam_base is None:
        tam_base = 500_000_000_000  # $500B generic fallback

    geo_key = geography.lower()
    multiplier = GEO_MULTIPLIER.get(geo_key, 0.5)
    tam = round(tam_base * multiplier)
    sam = round(tam * 0.05)
    som = round(sam * 0.01)

    return {
        "total_addressable_market_usd": tam,
        "serviceable_addressable_market_usd": sam,
        "serviceable_obtainable_market_usd": som,
        "confidence_level": confidence,
        "matched_industry": matched_keyword or "generic",
        "geography": geography,
        "target_demographic": target_demographic,
    }
