from fastapi import APIRouter, HTTPException
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




@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/dashboard")
def get_dashboard():
    led_data = _fetch_led_dashboard()
    return led_data if led_data is not None else {"leadSummary": [], "recentLeads": []}


@router.get("/leads")
def get_leads():
    return {"leadSummary": [], "allLeads": []}


@router.get("/customers")
def get_customers():
    led_customers = _fetch_led_customers()
    return {"customers": led_customers if led_customers is not None else []}


@router.post("/customers")
def create_customer(payload: CustomerCreateRequest):
    led_customer = _insert_led_customer(payload)
    if led_customer is None:
        raise HTTPException(status_code=500, detail="Customer could not be created in the database.")
    return led_customer


@router.get("/conversations")
def get_conversations():
    return {"conversationThreads": []}


@router.get("/follow-ups")
def get_follow_ups():
    return {"followUps": []}


@router.get("/roles")
def get_roles():
    return {"roleOptions": [], "rolePermissions": {}}
