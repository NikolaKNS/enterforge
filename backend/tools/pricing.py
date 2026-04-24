"""
Pricing calculation tool with agency markup.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional

from core import get_supabase_client
from .base import ToolError


async def calculate_pricing(
    base_cost: float,
    markup_percent: Optional[float] = None,
    fees: float = 0,
    taxes: float = 0,
    currency: Optional[str] = None,
    _agency_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate total pricing with agency markup.

    Args:
        base_cost: Base cost of flights, hotels, activities
        markup_percent: Agency markup percentage (uses agency default if not provided)
        fees: Additional fees
        taxes: Tax amount
        currency: Currency code (uses agency default if not provided)
        _agency_id: Injected agency ID

    Returns:
        Complete pricing breakdown

    Raises:
        ToolError: If calculation fails
    """
    if base_cost < 0:
        raise ToolError("Base cost cannot be negative")

    try:
        # Get agency settings if not provided
        if markup_percent is None or currency is None:
            if _agency_id is None:
                raise ToolError("Agency context required for pricing")

            supabase = get_supabase_client()
            result = supabase.table("agencies")\
                .select("settings")\
                .eq("id", _agency_id)\
                .single()\
                .execute()

            if result.data:
                settings = result.data.get("settings", {})
                if markup_percent is None:
                    markup_percent = settings.get("default_markup_percent", 10)
                if currency is None:
                    currency = settings.get("currency", "EUR")
            else:
                markup_percent = markup_percent or 10
                currency = currency or "EUR"

        # Use Decimal for precise calculations
        base = Decimal(str(base_cost))
        markup_rate = Decimal(str(markup_percent)) / Decimal("100")
        fees_dec = Decimal(str(fees))
        taxes_dec = Decimal(str(taxes))

        # Calculate markup amount
        markup_amount = (base * markup_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Calculate total
        total = base + markup_amount + fees_dec + taxes_dec
        total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "base_cost": str(base),
            "markup_percent": float(markup_percent),
            "markup_amount": str(markup_amount),
            "fees": str(fees_dec),
            "taxes": str(taxes_dec),
            "total": str(total),
            "currency": currency,
            "breakdown": {
                "items": [
                    {"description": "Base cost", "amount": str(base), "type": "base"},
                    {"description": f"Agency markup ({markup_percent}%)", "amount": str(markup_amount), "type": "markup"},
                    {"description": "Additional fees", "amount": str(fees_dec), "type": "fee"},
                    {"description": "Taxes", "amount": str(taxes_dec), "type": "tax"}
                ],
                "total": str(total)
            },
            "formatted": {
                "base": f"{currency} {float(base):,.2f}",
                "markup": f"{currency} {float(markup_amount):,.2f}",
                "fees": f"{currency} {float(fees_dec):,.2f}",
                "taxes": f"{currency} {float(taxes_dec):,.2f}",
                "total": f"{currency} {float(total):,.2f}"
            }
        }

    except ToolError:
        raise
    except Exception as e:
        raise ToolError(f"Pricing calculation failed: {str(e)}")


async def calculate_multiple(
    items: list,
    agency_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate pricing for multiple items.

    Args:
        items: List of {name, base_cost, category} dicts
        agency_id: Agency ID for settings

    Returns:
        Combined pricing breakdown
    """
    if not items:
        raise ToolError("No items provided")

    total_base = sum(item.get("base_cost", 0) for item in items)

    # Calculate with agency settings
    return await calculate_pricing(
        base_cost=total_base,
        _agency_id=agency_id
    )
