from fastapi import APIRouter
from pydantic import BaseModel

try:
    from ..db import get_db
except ImportError:
    from db import get_db


class ClientRequest(BaseModel):
    clientid: int


router = APIRouter(prefix="/UploadFile", tags=["UploadFile"])


@router.post("")
def getModelName(req: ClientRequest):
    clientid = req.clientid

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("CALL get_model_names_by_client(%s)", (clientid,))
        result = cur.fetchall()

    if not result or not result[0]:
        return {"model name": None, "message": "No model found for this client"}

    first_row = result[0]
    model_name = first_row[0] if first_row else None

    return {"model name": model_name, "message": "model name successfully"}
