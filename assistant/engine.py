import re
import json
import logging
import requests
from decimal import Decimal
from django.conf import settings
from django.db.models import Q
from products.models import Product, ProductCategory, Offer
from faq.models import FAQ
from troubleshooting.models import ErrorCode
from cart.models import Order

logger = logging.getLogger(__name__)


def extract_price_constraint(query):
    """
    Extracts price ceilings like 'under 50000', 'under 1 lakh', '< 80000', etc.
    """
    query_lower = query.lower().replace(',', '')
    match = re.search(r'(under|below|less than|<|budget of)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|lakh|lac)?', query_lower)
    if match:
        val = float(match.group(2))
        unit = match.group(3)
        if unit == 'k':
            val *= 1000
        elif unit in ('lakh', 'lac'):
            val *= 100000
        return val
    return None


def retrieve_context(query, user=None):
    """
    Retrieves grounded records from Products, FAQs, ErrorCodes, Offers, and User Orders.
    Returns:
        retrieved_data: dictionary of domain records
        sources: list of formatted source reference dictionaries
    """
    query_clean = query.strip()
    words = [w for w in re.split(r'\W+', query_clean) if len(w) > 2]
    max_price = extract_price_constraint(query_clean)

    retrieved = {
        'products': [],
        'faqs': [],
        'error_codes': [],
        'offers': [],
        'orders': []
    }
    sources = []

    # 1. Product Search
    product_qs = Product.objects.filter(is_active=True).select_related('category')
    if max_price:
        product_qs = product_qs.filter(corporate_price__lte=max_price)

    # Search by text
    if words:
        p_q = Q()
        for w in words:
            p_q |= (
                Q(name__icontains=w) |
                Q(tagline__icontains=w) |
                Q(category__name__icontains=w) |
                Q(sku__icontains=w) |
                Q(description__icontains=w)
            )
        matched_products = product_qs.filter(p_q).distinct()[:5]
    else:
        matched_products = product_qs.order_by('-is_featured')[:3]

    for p in matched_products:
        retrieved['products'].append({
            'name': p.name,
            'sku': p.sku,
            'category': p.category.name,
            'corporate_price': float(p.corporate_price),
            'original_price': float(p.original_price),
            'discount_percent': p.discount_percent,
            'savings': float(p.savings),
            'stock': p.stock_quantity,
            'in_stock': p.is_in_stock(),
            'specs': p.specs,
            'url': f"/products/{p.slug}/",
            'image_url': p.image_url,
            'badge': p.badge,
        })
        sources.append({
            'type': 'Product',
            'title': f"{p.name} (₹{p.corporate_price:,.0f})",
            'url': f"/products/{p.slug}/",
            'snippet': f"SKU: {p.sku} | Save {p.discount_percent}% off MSRP. Stock: {p.stock_quantity} units."
        })

    # 2. Offer / Coupon Search
    offer_intent = any(w.lower() in ('offer', 'offers', 'coupon', 'coupons', 'discount', 'code', 'promo', 'deals') for w in words)
    if offer_intent or words:
        o_q = Q(is_active=True)
        if words and not offer_intent:
            o_sub = Q()
            for w in words:
                o_sub |= Q(code__icontains=w) | Q(title__icontains=w)
            o_q &= o_sub
        matched_offers = Offer.objects.filter(o_q)[:3]
        for o in matched_offers:
            retrieved['offers'].append({
                'code': o.code,
                'title': o.title,
                'discount_percent': o.discount_percent,
                'min_order_amount': float(o.min_order_amount),
                'description': o.description
            })
            sources.append({
                'type': 'Offer',
                'title': f"Coupon: {o.code} ({o.discount_percent}% Off)",
                'url': '/products/offers/',
                'snippet': o.description
            })

    # 3. FAQ Search
    faq_q = Q(is_active=True)
    if words:
        sub_f = Q()
        for w in words:
            sub_f |= Q(question__icontains=w) | Q(answer__icontains=w) | Q(category__name__icontains=w)
        faq_q &= sub_f
    matched_faqs = FAQ.objects.filter(faq_q)[:4]
    for f in matched_faqs:
        retrieved['faqs'].append({
            'question': f.question,
            'answer': f.answer,
            'category': f.category.name,
            'helpful_count': f.helpful_count,
        })
        sources.append({
            'type': 'FAQ',
            'title': f.question,
            'url': f"/faq/?category={f.category.slug}",
            'snippet': f.answer[:120] + "..."
        })

    # 4. Error Code Search
    # Check for exact code like AUTH-001, CART-001 or keywords like 'error', 'failed', 'problem', 'troubleshoot'
    code_match = re.search(r'[A-Z]{3,4}-\d{3}', query_clean.upper())
    error_intent = code_match or any(w.lower() in ('error', 'code', 'issue', 'failed', 'troubleshoot', 'bug') for w in words)
    
    if error_intent:
        err_q = Q(is_active=True)
        if code_match:
            err_q &= Q(code=code_match.group(0))
        elif words:
            sub_err = Q()
            for w in words:
                sub_err |= Q(code__icontains=w) | Q(title__icontains=w) | Q(description__icontains=w)
            err_q &= sub_err
        
        matched_errors = ErrorCode.objects.filter(err_q)[:3]
        for e in matched_errors:
            retrieved['error_codes'].append({
                'code': e.code,
                'title': e.title,
                'category': e.get_category_display(),
                'severity': e.get_severity_display(),
                'description': e.description,
                'troubleshooting_steps': e.troubleshooting_steps,
                'preventive_recommendations': e.preventive_recommendations,
                'action_url': e.action_url,
                'action_label': e.action_label,
            })
            sources.append({
                'type': 'Troubleshooting',
                'title': f"Error {e.code}: {e.title}",
                'url': f"/troubleshooting/{e.code}/",
                'snippet': e.description[:120] + "..."
            })

    # 5. User Orders Search (if authenticated)
    order_intent = any(w.lower() in ('order', 'orders', 'tracking', 'package', 'delivery', 'shipped', 'status') for w in words)
    if user and user.is_authenticated and order_intent:
        user_orders = Order.objects.filter(user=user).order_by('-created_at')[:3]
        for o in user_orders:
            items_list = [f"{item.quantity}x {item.product_name}" for item in o.items.all()[:3]]
            retrieved['orders'].append({
                'order_number': o.order_number,
                'status': o.get_status_display(),
                'total_amount': float(o.total_amount),
                'created_at': o.created_at.strftime('%b %d, %Y'),
                'tracking_number': o.tracking_number,
                'estimated_delivery': o.estimated_delivery,
                'items': items_list
            })
            sources.append({
                'type': 'Order',
                'title': f"Order #{o.order_number} ({o.get_status_display()})",
                'url': f"/cart/orders/{o.order_number}/",
                'snippet': f"Placed on {o.created_at.strftime('%b %d, %Y')} for ₹{o.total_amount:,.2f}. Items: {', '.join(items_list)}"
            })

    return retrieved, sources


def generate_search_fallback_response(query, retrieved_data, user=None):
    """
    Intelligent, grounded search-based assistant fallback engine.
    Clearly identifies itself as a search-based assistant, never hallucinates,
    and returns rich markdown responses with structured answers.
    """
    products = retrieved_data.get('products', [])
    faqs = retrieved_data.get('faqs', [])
    error_codes = retrieved_data.get('error_codes', [])
    offers = retrieved_data.get('offers', [])
    orders = retrieved_data.get('orders', [])

    lines = []
    lines.append(f"### PerkCart Assistant Search Results for: *\"{query}\"*\n")

    # Has comparison intent?
    is_comparison = bool(re.search(r'\b(compare|versus|vs|difference between)\b', query.lower()))
    if is_comparison and len(products) >= 2:
        p1, p2 = products[0], products[1]
        lines.append(f"#### ⚖️ Side-by-Side Comparison: **{p1['name']}** vs **{p2['name']}**\n")
        lines.append(f"| Feature | **{p1['name']}** | **{p2['name']}** |")
        lines.append("| :--- | :--- | :--- |")
        lines.append(f"| **Corporate Price** | ₹{p1['corporate_price']:,.0f} (MSRP: ₹{p1['original_price']:,.0f}) | ₹{p2['corporate_price']:,.0f} (MSRP: ₹{p2['original_price']:,.0f}) |")
        lines.append(f"| **Corporate Savings** | Save {p1['discount_percent']}% (₹{p1['savings']:,.0f}) | Save {p2['discount_percent']}% (₹{p2['savings']:,.0f}) |")
        lines.append(f"| **Category** | {p1['category']} | {p2['category']} |")
        lines.append(f"| **Stock Status** | {'In Stock (' + str(p1['stock']) + ' units)' if p1['in_stock'] else 'Out of Stock'} | {'In Stock (' + str(p2['stock']) + ' units)' if p2['in_stock'] else 'Out of Stock'} |")
        lines.append(f"| **Link** | [View Details]({p1['url']}) | [View Details]({p2['url']}) |\n")

        # Key specs comparison
        all_spec_keys = list(p1.get('specs', {}).keys())[:4]
        if all_spec_keys:
            lines.append("**Key Technical Specifications:**")
            for k in all_spec_keys:
                v1 = p1.get('specs', {}).get(k, 'N/A')
                v2 = p2.get('specs', {}).get(k, 'N/A')
                lines.append(f"- **{k}**: {p1['name']} has `{v1}`, while {p2['name']} has `{v2}`.")
            lines.append("")

    elif products:
        lines.append("#### 🛍️ Matching Corporate Hardware Products:\n")
        for p in products:
            lines.append(f"- **[{p['name']}]({p['url']})** (`{p['sku']}`)")
            lines.append(f"  - **Corporate Price:** **₹{p['corporate_price']:,.0f}** ~~₹{p['original_price']:,.0f}~~ *(Save {p['discount_percent']}% / ₹{p['savings']:,.0f})*")
            lines.append(f"  - **Availability:** {'✅ In Stock (' + str(p['stock']) + ' available)' if p['in_stock'] else '⚠️ Out of Stock'}")
            if p.get('specs'):
                specs_summary = ", ".join([f"{k}: {v}" for k, v in list(p['specs'].items())[:3]])
                lines.append(f"  - **Specs:** {specs_summary}")
        lines.append("")

    # Errors
    if error_codes:
        lines.append("#### 🛠️ Troubleshooting & Error Code Assistance:\n")
        for ec in error_codes:
            lines.append(f"**Error Code [{ec['code']}]: {ec['title']}** ({ec['severity']})")
            lines.append(f"{ec['description']}")
            lines.append("\n**Resolution Steps:**")
            lines.append(f"{ec['troubleshooting_steps']}")
            if ec.get('action_url'):
                lines.append(f"\n👉 [{ec.get('action_label', 'Resolve Now')}]({ec['action_url']})")
            lines.append("")

    # Offers
    if offers:
        lines.append("#### 🏷️ Active Corporate Offers & Coupons:\n")
        for o in offers:
            lines.append(f"- **Coupon Code:** `{o['code']}` — **{o['discount_percent']}% Extra Discount**")
            lines.append(f"  - *{o['description']}* (Min Order: ₹{o['min_order_amount']:,.0f})")
        lines.append("")

    # FAQs
    if faqs:
        lines.append("#### ❓ Frequently Asked Shopping Questions:\n")
        for f in faqs:
            lines.append(f"**Q: {f['question']}**")
            lines.append(f"> {f['answer']}\n")

    # Orders (if authenticated)
    if orders:
        lines.append("#### 📦 Your Recent Corporate Orders:\n")
        for o in orders:
            lines.append(f"- **Order [{o['order_number']}](/cart/orders/{o['order_number']}/)** — Status: **{o['status']}**")
            lines.append(f"  - Total: ₹{o['total_amount']:,.2f} | Placed on: {o['created_at']}")
            lines.append(f"  - Tracking: `{o['tracking_number']}` (Estimated Delivery: {o['estimated_delivery']})")
            lines.append(f"  - Items: {', '.join(o['items'])}")
        lines.append("")

    # If nothing matched
    if not (products or faqs or error_codes or offers or orders):
        lines.append("I could not find exact matching corporate products, FAQs, or error codes in our database for that query.\n")
        lines.append("Here are suggested topics you can explore:")
        lines.append("- *\"Show laptops under ₹1,00,000\"*")
        lines.append("- *\"Compare PerkBook Ultra 16 Pro and ThinkPro X1\"*")
        lines.append("- *\"What corporate coupons are active?\"*")
        lines.append("- *\"How does corporate verification work?\"*")
        lines.append("- *\"What does error AUTH-002 mean?\"*")
        if user and user.is_authenticated:
            lines.append("- *\"Where is my recent order?\"*")

    lines.append("\n---")
    lines.append("*🤖 Search-Based Fallback Engine active. Verified database grounding applied.*")
    return "\n".join(lines)


def generate_llm_response(query, retrieved_data, history, api_key):
    """
    Grounds LLM with database context and calls Gemini API via REST.
    Falls back gracefully if API fails or times out.
    """
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    # Build grounded system prompt
    context_json = json.dumps(retrieved_data, indent=2)
    prompt = f"""You are the PerkCart AI Shopping Assistant, a corporate procurement helper inspired by Samsung corporate portal.
Respond politely and concisely to the corporate employee's shopping inquiry.

CRITICAL INSTRUCTIONS:
1. ONLY answer using the Grounded Corporate Database context provided below.
2. DO NOT invent products, prices, specifications, stock availability, discounts, or error-code meanings that are not in the context.
3. If the answer cannot be supported by the provided information, politely state that it is not currently available in our corporate database.
4. Format your answer with clean markdown, bullet points, and pricing comparisons when applicable.
5. Always reference specific SKUs, coupon codes (e.g. WELCOME10), error codes (e.g. AUTH-001), or order numbers where relevant.

GROUNDED CORPORATE DATABASE CONTEXT:
{context_json}

USER INQUIRY:
{query}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800,
        }
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=8)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    return text, "Gemini-1.5-Flash (Grounded AI Engine)"
        logger.warning(f"Gemini API returned status {response.status_code}: {response.text[:200]}")
    except Exception as err:
        logger.warning(f"Gemini API invocation error: {err}")

    # Fallback to search fallback
    fallback_text = generate_search_fallback_response(query, retrieved_data)
    return fallback_text, "Search-Based Fallback Engine (API Failover)"


def process_assistant_query(query, user=None, session_key=""):
    """
    Main orchestration entry point:
    1. Validates input
    2. Retrieves grounded database records
    3. Generates response using real AI API (if key configured) or robust search fallback
    4. Formats and returns sources
    """
    if not query or len(query.strip()) < 2:
        return {
            'content': "Please enter a valid question or search term (e.g., 'Find laptops under 90,000' or 'What does error CART-001 mean?').",
            'engine': "InputValidator",
            'sources': [],
        }

    # 1. Retrieve grounded context
    retrieved_data, sources = retrieve_context(query, user=user)

    # 2. Check for configured API key
    api_key = getattr(settings, 'GEMINI_API_KEY', '') or getattr(settings, 'OPENAI_API_KEY', '')

    if api_key:
        content, engine = generate_llm_response(query, retrieved_data, history=[], api_key=api_key)
    else:
        content = generate_search_fallback_response(query, retrieved_data, user=user)
        engine = "Search-Based Fallback Engine"

    return {
        'content': content,
        'engine': engine,
        'sources': sources,
    }
