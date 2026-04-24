"""
PDF generation tool for travel offers.
Uses WeasyPrint to generate professional PDF proposals.
"""

import os
import tempfile
from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Template

from core import get_supabase_client, settings
from .base import ToolError


# Default HTML template for travel offers
DEFAULT_OFFER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @bottom-center {
                content: "{{ agency_name }} | Page " counter(page);
                font-size: 9pt;
                color: #666;
            }
        }
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid {{ primary_color }};
        }
        .logo {
            max-height: 60px;
            margin-bottom: 10px;
        }
        .agency-info {
            font-size: 10pt;
            color: #666;
            margin-bottom: 5px;
        }
        .offer-title {
            font-size: 24pt;
            color: {{ primary_color }};
            margin: 20px 0 10px 0;
        }
        .destination {
            font-size: 16pt;
            color: #555;
            margin-bottom: 5px;
        }
        .dates {
            font-size: 12pt;
            color: #777;
        }
        .section {
            margin: 25px 0;
            page-break-inside: avoid;
        }
        .section-title {
            font-size: 14pt;
            color: {{ primary_color }};
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
        .highlight-box {
            background: #f8f8f8;
            border-left: 4px solid {{ primary_color }};
            padding: 15px;
            margin: 15px 0;
        }
        .day-card {
            background: #fafafa;
            border: 1px solid #eee;
            padding: 15px;
            margin: 10px 0;
            page-break-inside: avoid;
        }
        .day-number {
            font-size: 12pt;
            font-weight: bold;
            color: {{ primary_color }};
        }
        .pricing-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        .pricing-table td {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        .pricing-table td:first-child {
            text-align: left;
        }
        .pricing-table td:last-child {
            text-align: right;
            font-weight: bold;
        }
        .total-row {
            background: #f0f0f0;
            font-size: 14pt;
        }
        .validity {
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 10px;
            text-align: center;
            margin: 20px 0;
            font-size: 11pt;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 9pt;
            color: #666;
            text-align: center;
        }
        .terms {
            font-size: 8pt;
            color: #888;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="header">
        {% if logo_url %}
        <img src="{{ logo_url }}" class="logo" alt="{{ agency_name }}">
        {% endif %}
        <div class="agency-info">{{ agency_name }} | {{ agency_address }} | {{ agency_phone }} | {{ agency_email }}</div>
    </div>

    <div class="offer-title">{{ title }}</div>
    <div class="destination">{{ destination }}</div>
    <div class="dates">{{ duration }} days | {{ travel_dates }}</div>

    {% if description %}
    <div class="section">
        <p>{{ description }}</p>
    </div>
    {% endif %}

    {% if highlights %}
    <div class="section">
        <div class="section-title">Trip Highlights</div>
        <ul>
            {% for highlight in highlights %}
            <li>{{ highlight }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if itinerary %}
    <div class="section">
        <div class="section-title">Your Itinerary</div>
        {% for day in itinerary %}
        <div class="day-card">
            <div class="day-number">Day {{ day.day }}: {{ day.theme }}</div>
            <p><strong>Morning:</strong> {{ day.morning.activity }} at {{ day.morning.location }}</p>
            <p><strong>Afternoon:</strong> {{ day.afternoon.activity }} at {{ day.afternoon.location }}</p>
            <p><strong>Evening:</strong> {{ day.evening.activity }} at {{ day.evening.location }}</p>
            {% if day.insider_tip %}
            <div class="highlight-box">💡 {{ day.insider_tip }}</div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if flights %}
    <div class="section">
        <div class="section-title">Flight Details</div>
        {% for flight in flights %}
        <div class="day-card">
            <p><strong>{{ flight.airline }} {{ flight.flight_number }}</strong></p>
            <p>From: {{ flight.departure.airport }} at {{ flight.departure.time }}</p>
            <p>To: {{ flight.arrival.airport }} at {{ flight.arrival.time }}</p>
            <p>Duration: {{ flight.duration }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="section">
        <div class="section-title">Pricing</div>
        <table class="pricing-table">
            <tr>
                <td>Base Cost</td>
                <td>{{ pricing.formatted.base }}</td>
            </tr>
            <tr>
                <td>Agency Markup</td>
                <td>{{ pricing.formatted.markup }}</td>
            </tr>
            {% if pricing.fees and pricing.fees != "0" %}
            <tr>
                <td>Additional Fees</td>
                <td>{{ pricing.formatted.fees }}</td>
            </tr>
            {% endif %}
            {% if pricing.taxes and pricing.taxes != "0" %}
            <tr>
                <td>Taxes</td>
                <td>{{ pricing.formatted.taxes }}</td>
            </tr>
            {% endif %}
            <tr class="total-row">
                <td>Total Price</td>
                <td>{{ pricing.formatted.total }}</td>
            </tr>
        </table>
    </div>

    {% if included %}
    <div class="section">
        <div class="section-title">What's Included</div>
        <ul>
            {% for item in included %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if excluded %}
    <div class="section">
        <div class="section-title">Not Included</div>
        <ul>
            {% for item in excluded %}
            <li>{{ item }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    <div class="validity">
        This offer is valid until {{ valid_until }}. Prices and availability subject to change.
    </div>

    <div class="footer">
        <p>Thank you for choosing {{ agency_name }}!</p>
        <p>Questions? Contact us at {{ agency_email }} or {{ agency_phone }}</p>
    </div>

    <div class="terms">
        Terms and conditions apply. This proposal is for informational purposes and does not constitute a binding contract.
        Final booking is subject to availability and confirmation. Cancellation policies vary by supplier.
    </div>
</body>
</html>
"""


async def generate_pdf(
    offer_id: Optional[str] = None,
    offer_data: Optional[Dict[str, Any]] = None,
    template: str = "standard",
    _agency_id: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate a PDF proposal from offer data.

    Args:
        offer_id: Offer UUID (if already saved)
        offer_data: Offer data dict (if generating before save)
        template: PDF template name
        _agency_id: Injected agency ID

    Returns:
        PDF generation result with URL

    Raises:
        ToolError: If generation fails
    """
    if not _agency_id:
        raise ToolError("Agency context required")

    # Load offer if ID provided
    if offer_id and not offer_data:
        supabase = get_supabase_client()
        result = supabase.table("offers")\
            .select("*")\
            .eq("id", offer_id)\
            .eq("agency_id", _agency_id)\
            .single()\
            .execute()

        if not result.data:
            raise ToolError(f"Offer not found: {offer_id}")

        offer_data = result.data

    if not offer_data:
        raise ToolError("Offer data or ID required")

    # Load agency info for branding
    try:
        supabase = get_supabase_client()
        agency_result = supabase.table("agencies")\
            .select("name,branding_config")\
            .eq("id", _agency_id)\
            .single()\
            .execute()

        agency_info = agency_result.data or {}
        branding = agency_info.get("branding_config", {})
    except Exception:
        agency_info = {"name": "Your Agency"}
        branding = {}

    # Build template context
    content = offer_data.get("content_json", {})
    pricing = offer_data.get("pricing", {})

    context = {
        # Agency info
        "agency_name": agency_info.get("name", "Your Agency"),
        "agency_address": "",  # Could be added to agency settings
        "agency_phone": branding.get("phone", ""),
        "agency_email": branding.get("email", ""),
        "logo_url": branding.get("logo_url"),
        "primary_color": branding.get("primary_color", "#E85D04"),

        # Offer info
        "title": offer_data.get("title"),
        "destination": offer_data.get("destination"),
        "description": offer_data.get("description"),
        "travel_dates": "TBD",  # Extract from content or itinerary
        "duration": len(offer_data.get("itinerary", [])),

        # Content
        "highlights": content.get("highlights", []),
        "included": content.get("included", []),
        "excluded": content.get("excluded", []),
        "itinerary": offer_data.get("itinerary", []),
        "flights": offer_data.get("flights", []),
        "pricing": pricing,
        "valid_until": offer_data.get("valid_until", "TBD"),
    }

    # Generate HTML
    template_obj = Template(DEFAULT_OFFER_TEMPLATE)
    html_content = template_obj.render(**context)

    try:
        # Import WeasyPrint (may not be available in all environments)
        from weasyprint import HTML, CSS

        # Create PDF
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            html = HTML(string=html_content)
            html.write_pdf(tmp.name)

            # Upload to Supabase Storage
            supabase = get_supabase_client()

            filename = f"offer_{offer_id or 'draft'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            storage_path = f"{_agency_id}/{filename}"

            with open(tmp.name, "rb") as pdf_file:
                result = supabase.storage.from_(settings.STORAGE_BUCKET).upload(
                    path=storage_path,
                    file=pdf_file,
                    file_options={"content-type": "application/pdf"}
                )

            # Get public URL
            pdf_url = supabase.storage.from_(settings.STORAGE_BUCKET).get_public_url(storage_path)

            # Clean up temp file
            os.unlink(tmp.name)

            # Update offer if ID provided
            if offer_id:
                supabase.table("offers").update({
                    "pdf_url": pdf_url,
                    "pdf_generated_at": "now()"
                }).eq("id", offer_id).execute()

            return {
                "success": True,
                "pdf_url": pdf_url,
                "filename": filename,
                "message": "PDF generated successfully"
            }

    except ImportError:
        # WeasyPrint not installed - return HTML instead
        return {
            "success": False,
            "error": "PDF generation requires WeasyPrint. Install with: pip install weasyprint",
            "html_preview": html_content[:500] + "...",
            "message": "PDF generation not available. Install WeasyPrint to enable this feature."
        }

    except Exception as e:
        raise ToolError(f"PDF generation failed: {str(e)}")


async def get_pdf_template_names(_agency_id: str = None) -> list:
    """Get available PDF template names."""
    # In the future, this could load from a templates table
    return ["standard", "minimal", "luxury"]
