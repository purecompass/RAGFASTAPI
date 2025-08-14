from fastapi import APIRouter
from db import get_db
from pydantic import BaseModel

class ClientRequest(BaseModel):
    clientid: int
router = APIRouter(prefix="/UploadFile", tags=["UploadFile"])

@router.post("")
def getModleName(req: ClientRequest):
     clientid = req.clientid
     with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM get_model_names_by_client(1);")
        model_name = cur.fetchone()[0]
        conn.commit()
        return {"model name": model_name, "message": "model name successfully"}
