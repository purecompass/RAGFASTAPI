from fastapi import APIRouter
from pydantic import BaseModel

try:
    from ..db import get_db
except ImportError:
    from db import get_db


class CustomerCreateRequest(BaseModel):
    name: str
    phone: str
    email: str
    whatsapp: str
    source: str
    assignedOwner: str


router = APIRouter(prefix="/api", tags=["CustomerSupport"])


def _get_led_customer_row(row: dict) -> dict:
    return {
        "id": row.get("LCM_Customer_ID"),
        "name": row.get("LCM_Customer_Name"),
        "phone": row.get("LCM_Primary_Phone"),
        "email": row.get("LCM_Primary_Email"),
        "whatsapp": row.get("LCM_Whatsapp_Number"),
        "source": row.get("LCM_Customer_Type") or "LED",
        "assignedOwner": "LED System",
        "lastContact": row.get("LCM_Updated_At"),
        "status": row.get("LCM_Status"),
        "location": row.get("LCM_Location"),
        "customerType": row.get("LCM_Customer_Type"),
        "customerCode": row.get("LCM_Customer_Code"),
    }


def _fetch_led_dashboard():
    try:
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("LED_SP_Dashboard_Summary")
            result_sets = []
            for result in cursor.stored_results():
                result_sets.append(result.fetchall())

            if not result_sets:
                return None

            summary = result_sets[0][0] if result_sets[0] else {}
            recent_rows = result_sets[1] if len(result_sets) > 1 else []

            leadSummary = [
                {
                    "label": "Total customers",
                    "value": str(summary.get("LCM_Total_Customers", 0)),
                    "change": f"{summary.get('LCM_Active_Customers', 0)} active",
                    "tone": "bg-orange-50 text-orange-700",
                },
                {
                    "label": "Active",
                    "value": str(summary.get("LCM_Active_Customers", 0)),
                    "change": "+10%",
                    "tone": "bg-emerald-50 text-emerald-700",
                },
                {
                    "label": "Prospect",
                    "value": str(summary.get("LCM_Prospect_Customers", 0)),
                    "change": "pipeline",
                    "tone": "bg-amber-50 text-amber-700",
                },
                {
                    "label": "Inactive",
                    "value": str(summary.get("LCM_Inactive_Customers", 0)),
                    "change": "review",
                    "tone": "bg-sky-50 text-sky-700",
                },
            ]

            recentLeads = [
                {
                    "id": row.get("LCM_Customer_ID"),
                    "customer": row.get("LCM_Customer_Name"),
                    "channel": "LED",
                    "status": row.get("LCM_Status"),
                    "owner": "LED System",
                    "intent": row.get("LCM_Customer_Type") or "Customer master",
                    "value": row.get("LCM_Primary_Phone") or "-",
                    "time": row.get("LCM_Created_At").strftime("%Y-%m-%d") if row.get("LCM_Created_At") else "-",
                }
                for row in recent_rows
            ]
            return {"leadSummary": leadSummary, "recentLeads": recentLeads}
    except Exception:
        return None


def _fetch_led_customers():
    try:
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("LED_SP_Customer_Master_List")
            rows = []
            for result in cursor.stored_results():
                rows = result.fetchall()
                break

            return [{
                "id": row.get("LCM_Customer_ID"),
                "name": row.get("LCM_Customer_Name"),
                "phone": row.get("LCM_Primary_Phone"),
                "email": row.get("LCM_Primary_Email"),
                "whatsapp": row.get("LCM_Whatsapp_Number"),
                "source": row.get("LCM_Customer_Type") or "LED",
                "assignedOwner": "LED System",
                "lastContact": row.get("LCM_Updated_At"),
                "status": row.get("LCM_Status"),
                "customerCode": row.get("LCM_Customer_Code"),
                "location": row.get("LCM_Location"),
                "customerType": row.get("LCM_Customer_Type"),
            } for row in rows]
    except Exception:
        return None


def _insert_led_customer(payload: CustomerCreateRequest):
    try:
        with get_db() as conn:
            cursor = conn.cursor(dictionary=True)
            customer_code = f"LED-CUST-{payload.name.replace(' ', '-').upper()[:20]}-{cursor.lastrowid or '001'}"
            cursor.callproc(
                "LED_SP_Customer_Master_Insert",
                args=(
                    customer_code,
                    payload.name,
                    "Retail",
                    payload.email,
                    payload.phone,
                    payload.whatsapp,
                    payload.source,
                    "Active",
                ),
            )
            result = next(cursor.stored_results())
            inserted_id = result.fetchall()[0]["LCM_Customer_ID"]
            return {"customer": {"id": inserted_id, "name": payload.name, "status": "Active"}}
    except Exception:
        return None


router = APIRouter(prefix="/api", tags=["CustomerSupport"])

leadSummary = [
    {"label": "New leads", "value": "128", "change": "+18%", "tone": "bg-orange-50 text-orange-700"},
    {"label": "Follow-ups due", "value": "41", "change": "8 today", "tone": "bg-amber-50 text-amber-700"},
    {"label": "Qualified", "value": "34", "change": "+12%", "tone": "bg-emerald-50 text-emerald-700"},
    {"label": "Avg. response", "value": "12m", "change": "-4m", "tone": "bg-sky-50 text-sky-700"},
]

recentLeads = [
    {
        "id": "LC-1042",
        "customer": "Aisha Rahman",
        "channel": "WhatsApp",
        "status": "New",
        "owner": "Nadia",
        "intent": "Interested in villa package",
        "value": "AED 118,000",
        "time": "2 mins ago",
    },
    {
        "id": "LC-1038",
        "customer": "Omar Haddad",
        "channel": "WhatsApp",
        "status": "Follow-up",
        "owner": "Salem",
        "intent": "Price clarification",
        "value": "AED 82,500",
        "time": "18 mins ago",
    },
    {
        "id": "LC-1029",
        "customer": "Leena Joseph",
        "channel": "WhatsApp",
        "status": "Qualified",
        "owner": "Sara",
        "intent": "Ready to book site visit",
        "value": "AED 221,000",
        "time": "1 hour ago",
    },
    {
        "id": "LC-1017",
        "customer": "Mohammed Ali",
        "channel": "WhatsApp",
        "status": "Quoted",
        "owner": "Khalid",
        "intent": "Comparing floor plans",
        "value": "AED 96,000",
        "time": "3 hours ago",
    },
]

allLeads = [
    {
        "id": "LC-1042",
        "customer": "Aisha Rahman",
        "channel": "WhatsApp",
        "status": "New",
        "owner": "Nadia",
        "intent": "Interested in premium lifestyle offer",
        "value": "AED 118,000",
        "time": "2 mins ago",
        "occupation": "Interior designer",
        "interests": "Home styling, premium lifestyle offers",
        "customerSegment": "Premium shoppers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "May 2025",
        "location": "Dubai",
        "preferredLanguage": "English",
        "lifetimeValue": "AED 220,000",
        "lastPurchaseCategory": "Lifestyle",
        "activityTimeline": [
            {"time": "2 mins ago", "title": "New inquiry received", "detail": "Customer showed interest in a premium lifestyle offer."},
            {"time": "Yesterday", "title": "Offer shared", "detail": "Pricing details were sent through WhatsApp with a follow-up CTA."},
            {"time": "3 days ago", "title": "Profile tagged", "detail": "Customer was segmented as a premium shopper with high purchase intent."},
        ],
        "nextAction": "Send a curated offer and invite them to a quick callback.",
        "replySuggestion": "Hi Aisha, thanks for reaching out. I can share the best-fit options and arrange a quick follow-up call.",
    },
    {
        "id": "LC-1038",
        "customer": "Omar Haddad",
        "channel": "WhatsApp",
        "status": "Follow-up",
        "owner": "Salem",
        "intent": "Price clarification for a value package",
        "value": "AED 82,500",
        "time": "18 mins ago",
        "occupation": "Project manager",
        "interests": "Value products, practical bundles",
        "customerSegment": "Value-driven buyers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "April 2025",
        "location": "Sharjah",
        "preferredLanguage": "Arabic",
        "lifetimeValue": "AED 150,000",
        "lastPurchaseCategory": "Home essentials",
        "activityTimeline": [
            {"time": "18 mins ago", "title": "Follow-up reminder created", "detail": "Sales task was scheduled for a package recommendation."},
            {"time": "Yesterday", "title": "Budget discussion", "detail": "Customer requested value-focused options and a flexible payment plan."},
            {"time": "4 days ago", "title": "Price-sensitive signal", "detail": "Customer was labeled as value-driven and asked for a better fit."},
        ],
        "nextAction": "Follow up with a more suitable package and a flexible payment option.",
        "replySuggestion": "Hi Omar, I can review the options that better match your budget and share a simple recommendation.",
    },
    {
        "id": "LC-1029",
        "customer": "Leena Joseph",
        "channel": "WhatsApp",
        "status": "Qualified",
        "owner": "Sara",
        "intent": "Ready to review premium options",
        "value": "AED 221,000",
        "time": "1 hour ago",
        "occupation": "Banking consultant",
        "interests": "Premium products, trusted recommendations",
        "customerSegment": "High-intent buyers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "March 2025",
        "location": "Abu Dhabi",
        "preferredLanguage": "English",
        "lifetimeValue": "AED 310,000",
        "lastPurchaseCategory": "Premium services",
        "activityTimeline": [
            {"time": "1 hour ago", "title": "Qualification confirmed", "detail": "Customer expressed readiness for the next step and asked for guidance."},
            {"time": "2 days ago", "title": "Recommendation summary sent", "detail": "A trusted summary was shared to support the purchase decision."},
            {"time": "1 week ago", "title": "High-intent signal", "detail": "Customer was categorized as a high-intent buyer after repeated engagement."},
        ],
        "nextAction": "Book the next conversation and send a trusted recommendation summary.",
        "replySuggestion": "Hi Leena, I can help with the next step and send a clear summary so you can make an informed choice.",
    },
    {
        "id": "LC-1017",
        "customer": "Mohammed Ali",
        "channel": "WhatsApp",
        "status": "Quoted",
        "owner": "Khalid",
        "intent": "Comparing shortlisted options",
        "value": "AED 96,000",
        "time": "3 hours ago",
        "occupation": "Operations supervisor",
        "interests": "Efficiency, practical upgrades",
        "customerSegment": "Practical buyers",
        "preferredChannel": "Email",
        "firstEngagement": "January 2025",
        "location": "Ajman",
        "preferredLanguage": "Arabic",
        "lifetimeValue": "AED 120,000",
        "lastPurchaseCategory": "Home & office supplies",
        "activityTimeline": [
            {"time": "3 hours ago", "title": "Quote reviewed", "detail": "Customer compared shortlisted options and asked for a practical recommendation."},
            {"time": "2 days ago", "title": "Comparison note added", "detail": "Internal notes highlighted the most efficient option for this buyer."},
            {"time": "1 week ago", "title": "Lead scored", "detail": "Customer was marked as a practical buyer based on recurring product comparisons."},
        ],
        "nextAction": "Share a concise comparison summary and highlight the most practical option.",
        "replySuggestion": "Hi Mohammed, I have compared the shortlisted options and recommend the most practical choice for your needs.",
    },
    {
        "id": "LC-1009",
        "customer": "Noura Sayegh",
        "channel": "WhatsApp",
        "status": "New",
        "owner": "Nadia",
        "intent": "Looking for flexible payment support",
        "value": "AED 140,500",
        "time": "5 hours ago",
        "occupation": "Teacher",
        "interests": "Affordable plans, flexible support",
        "customerSegment": "Budget-conscious shoppers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "June 2025",
        "location": "Dubai",
        "preferredLanguage": "English",
        "lifetimeValue": "AED 95,000",
        "lastPurchaseCategory": "Budget essentials",
        "activityTimeline": [
            {"time": "5 hours ago", "title": "New support request", "detail": "Customer asked for flexible payment support and a quick callback."},
            {"time": "1 day ago", "title": "Offer prepared", "detail": "A budget-conscious option was prepared to match the customer profile."},
            {"time": "4 days ago", "title": "Segment assigned", "detail": "Customer was grouped under budget-conscious shoppers for better routing."},
        ],
        "nextAction": "Provide payment options and book an immediate follow-up callback.",
        "replySuggestion": "Hi Noura, I can share flexible payment options and arrange a quick callback to explain them clearly.",
    },
    {
        "id": "LC-1002",
        "customer": "Rami Yusuf",
        "channel": "WhatsApp",
        "status": "Qualified",
        "owner": "Sara",
        "intent": "Interested in curated product recommendations",
        "value": "AED 205,000",
        "time": "8 hours ago",
        "occupation": "Entrepreneur",
        "interests": "Curated recommendations, premium selections",
        "customerSegment": "High-value shoppers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "February 2025",
        "location": "Ras Al Khaimah",
        "preferredLanguage": "English",
        "lifetimeValue": "AED 260,000",
        "lastPurchaseCategory": "Premium accessories",
        "activityTimeline": [
            {"time": "8 hours ago", "title": "Recommendation request", "detail": "Customer asked for curated suggestions aligned to their preferences."},
            {"time": "3 days ago", "title": "Profile enriched", "detail": "More customer insights were added to improve future recommendations."},
            {"time": "6 days ago", "title": "High-value segment", "detail": "This buyer was moved into a high-value customer segment for special handling."},
        ],
        "nextAction": "Send tailored recommendations that match the requested category and preference.",
        "replySuggestion": "Hi Rami, I have found a few curated options that align with your preferred style and budget.",
    },
]

customerRecords = [
    {
        "id": "CUST-201",
        "name": "Aisha Rahman",
        "phone": "+971 50 123 4567",
        "email": "aisha.rahman@example.com",
        "whatsapp": "+971 50 123 4567",
        "source": "Website enquiry",
        "assignedOwner": "Nadia",
        "lastContact": "Today, 9:15 AM",
        "status": "Warm",
        "occupation": "Interior designer",
        "interests": "Home styling, premium lifestyle offers",
        "customerSegment": "Premium shoppers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "May 2025",
        "location": "Dubai",
        "preferredLanguage": "English",
        "lifetimeValue": "AED 220,000",
        "lastPurchaseCategory": "Lifestyle",
        "activityTimeline": [
            {"time": "Today", "title": "Warm customer check-in", "detail": "Recent engagement indicates a strong interest in lifestyle offers."},
            {"time": "Last week", "title": "Offer follow-up", "detail": "Customer was contacted after showing interest in premium categories."},
            {"time": "2 weeks ago", "title": "Profile enrichment", "detail": "Customer preferences were updated after the last interaction."},
        ],
    },
    {
        "id": "CUST-198",
        "name": "Omar Haddad",
        "phone": "+971 55 908 3311",
        "email": "omar.haddad@example.com",
        "whatsapp": "+971 55 908 3311",
        "source": "WhatsApp ad",
        "assignedOwner": "Salem",
        "lastContact": "Today, 8:20 AM",
        "status": "Needs follow-up",
        "occupation": "Project manager",
        "interests": "Value products, practical bundles",
        "customerSegment": "Value-driven buyers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "April 2025",
        "location": "Sharjah",
        "preferredLanguage": "Arabic",
        "lifetimeValue": "AED 150,000",
        "lastPurchaseCategory": "Home essentials",
        "activityTimeline": [
            {"time": "Today", "title": "Follow-up reminder", "detail": "The sales team added a reminder to re-engage with a value-focused offer."},
            {"time": "Last week", "title": "Budget review", "detail": "Customer requested practical options and a more suitable package."},
            {"time": "2 weeks ago", "title": "Channel preference", "detail": "Customer confirmed WhatsApp as the preferred communication channel."},
        ],
    },
    {
        "id": "CUST-172",
        "name": "Leena Joseph",
        "phone": "+971 52 354 4422",
        "email": "leena.joseph@example.com",
        "whatsapp": "+971 52 354 4422",
        "source": "Social media",
        "assignedOwner": "Sara",
        "lastContact": "Yesterday, 5:50 PM",
        "status": "Qualified",
        "occupation": "Banking consultant",
        "interests": "Premium products, trusted recommendations",
        "customerSegment": "High-intent buyers",
        "preferredChannel": "WhatsApp",
        "firstEngagement": "March 2025",
        "location": "Abu Dhabi",
        "preferredLanguage": "English",
        "lifetimeValue": "AED 310,000",
        "lastPurchaseCategory": "Premium services",
        "activityTimeline": [
            {"time": "Today", "title": "Qualified customer", "detail": "The customer moved to a qualified stage after strong engagement signals."},
            {"time": "Last week", "title": "Recommendation shared", "detail": "A recommendation summary was sent to support the customer decision path."},
            {"time": "2 weeks ago", "title": "Intent validation", "detail": "Customer confirmed intent through repeated conversations and positive replies."},
        ],
    },
    {
        "id": "CUST-145",
        "name": "Mohammed Ali",
        "phone": "+971 56 789 3344",
        "email": "mohammed.ali@example.com",
        "whatsapp": "+971 56 789 3344",
        "source": "Referral",
        "assignedOwner": "Khalid",
        "lastContact": "Yesterday, 4:00 PM",
        "status": "Quoted",
        "occupation": "Operations supervisor",
        "interests": "Efficiency, practical upgrades",
        "customerSegment": "Practical buyers",
        "preferredChannel": "Email",
        "firstEngagement": "January 2025",
        "location": "Ajman",
        "preferredLanguage": "Arabic",
        "lifetimeValue": "AED 120,000",
        "lastPurchaseCategory": "Home & office supplies",
        "activityTimeline": [
            {"time": "Today", "title": "Quote follow-up", "detail": "Customer reviewed the shortlist and requested a practical recommendation."},
            {"time": "Last week", "title": "Comparison note", "detail": "Internal notes captured value and efficiency preferences for this buyer."},
            {"time": "2 weeks ago", "title": "Segment refreshed", "detail": "Buyer profile was updated after a series of practical product comparisons."},
        ],
    },
]

conversationThreads = [
    {
        "id": "CONV-1",
        "customer": "Aisha Rahman",
        "leadId": "LC-1042",
        "channel": "WhatsApp",
        "status": "Open",
        "sentiment": "High intent",
        "lastMessage": "Can you share the exact villa package pricing?",
        "messages": [
            {"sender": "customer", "text": "Hi team, I want to know the pricing for your villa package.", "time": "9:12 AM"},
            {"sender": "agent", "text": "Hi Aisha, I can share the brochure and pricing details right away.", "time": "9:15 AM"},
            {"sender": "customer", "text": "Perfect. Can you also confirm the payment plan options?", "time": "9:17 AM"},
            {"sender": "agent", "text": "Absolutely. I will send the package summary along with flexible payment options.", "time": "9:18 AM"},
        ],
    },
    {
        "id": "CONV-2",
        "customer": "Omar Haddad",
        "leadId": "LC-1038",
        "channel": "WhatsApp",
        "status": "Follow-up required",
        "sentiment": "Price-sensitive",
        "lastMessage": "Please share a cheaper option.",
        "messages": [
            {"sender": "customer", "text": "Your quote is slightly above my budget.", "time": "8:08 AM"},
            {"sender": "agent", "text": "Thank you for the feedback. I can help with a more budget-friendly option.", "time": "8:10 AM"},
            {"sender": "customer", "text": "Please share a cheaper option.", "time": "8:11 AM"},
            {"sender": "agent", "text": "Sure, I will send a summary with financing options and a smaller unit suggestion.", "time": "8:14 AM"},
        ],
    },
    {
        "id": "CONV-3",
        "customer": "Leena Joseph",
        "leadId": "LC-1029",
        "channel": "WhatsApp",
        "status": "Qualified",
        "sentiment": "Ready to visit",
        "lastMessage": "Please confirm the site visit slot for tomorrow.",
        "messages": [
            {"sender": "customer", "text": "I would like a site visit tomorrow afternoon.", "time": "Yesterday, 7:40 PM"},
            {"sender": "agent", "text": "I can confirm a site visit slot for tomorrow at 4:00 PM.", "time": "Yesterday, 7:42 PM"},
            {"sender": "customer", "text": "Please confirm the site visit slot for tomorrow.", "time": "Yesterday, 7:43 PM"},
            {"sender": "agent", "text": "Confirmed. I have reserved the visit for tomorrow at 4:00 PM.", "time": "Yesterday, 7:45 PM"},
        ],
    },
]

followUps = [
    {
        "id": "FU-210",
        "customer": "Omar Haddad",
        "leadId": "LC-1038",
        "owner": "Salem",
        "channel": "WhatsApp",
        "due": "Today, 3:00 PM",
        "priority": "High",
        "status": "Pending",
        "note": "Send revised budget packages and financing options.",
    },
    {
        "id": "FU-198",
        "customer": "Noura Sayegh",
        "leadId": "LC-1009",
        "owner": "Nadia",
        "channel": "WhatsApp",
        "due": "Today, 5:30 PM",
        "priority": "Medium",
        "status": "Scheduled",
        "note": "Arrange callback to explain financing options.",
    },
    {
        "id": "FU-177",
        "customer": "Rami Yusuf",
        "leadId": "LC-1002",
        "owner": "Sara",
        "channel": "WhatsApp",
        "due": "Tomorrow, 10:00 AM",
        "priority": "Medium",
        "status": "Pending",
        "note": "Share matching resale listings in preferred location.",
    },
    {
        "id": "FU-155",
        "customer": "Mohammed Ali",
        "leadId": "LC-1017",
        "owner": "Khalid",
        "channel": "WhatsApp",
        "due": "Tomorrow, 1:00 PM",
        "priority": "Low",
        "status": "Completed",
        "note": "Comparison summary sent successfully.",
    },
]

roleOptions = ["Admin", "Sales Manager", "Sales Executive"]

rolePermissions = {
    "Admin": ["dashboard", "leads", "customer-master", "conversations", "follow-ups", "faq-upload", "terms", "privacy"],
    "Sales Manager": ["dashboard", "leads", "customer-master", "conversations", "follow-ups", "terms", "privacy"],
    "Sales Executive": ["dashboard", "leads", "conversations", "follow-ups", "terms", "privacy"],
}

leadStatusColors = {
    "New": "bg-blue-100 text-blue-700",
    "Follow-up": "bg-amber-100 text-amber-700",
    "Qualified": "bg-emerald-100 text-emerald-700",
    "Quoted": "bg-violet-100 text-violet-700",
}


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/dashboard")
def get_dashboard():
    led_data = _fetch_led_dashboard()
    if led_data is not None:
        return led_data
    return {"leadSummary": leadSummary, "recentLeads": recentLeads}


@router.get("/leads")
def get_leads():
    return {"leadSummary": leadSummary, "allLeads": allLeads}


@router.get("/customers")
def get_customers():
    led_customers = _fetch_led_customers()
    if led_customers is not None:
        return {"customers": led_customers}
    return {"customers": customerRecords}


@router.post("/customers")
def create_customer(payload: CustomerCreateRequest):
    led_customer = _insert_led_customer(payload)
    if led_customer is not None:
        return led_customer

    customer = {
        "id": f"CUST-{len(customerRecords) + 1:03d}",
        "name": payload.name,
        "phone": payload.phone,
        "email": payload.email,
        "whatsapp": payload.whatsapp,
        "source": payload.source,
        "assignedOwner": payload.assignedOwner,
        "lastContact": "Just now",
        "status": "New",
    }
    customerRecords.insert(0, customer)
    return {"customer": customer}


@router.get("/conversations")
def get_conversations():
    return {"conversationThreads": conversationThreads}


@router.get("/follow-ups")
def get_follow_ups():
    return {"followUps": followUps}


@router.get("/roles")
def get_roles():
    return {"roleOptions": roleOptions, "rolePermissions": rolePermissions}
