from pydantic import BaseModel, EmailStr

class EmailVerificationEvent(BaseModel):
    event: str
    version: int
    user_id: str
    email: EmailStr
    token: str
