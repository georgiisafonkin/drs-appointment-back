from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import async_session
from app.infrastructure.db.repository import EmailVerificationRepository, UserRepository
from app.domain.services import AuthService
from app.schemas.auth import MessageResponse, RegisterRequest, LoginRequest, VerifyEmailResponse
from app.schemas.token import TokenResponse

router = APIRouter(prefix="/auth")

async def get_session():
    async with async_session() as session:
        yield session

@router.post("/register", response_model=MessageResponse)
async def register(data: RegisterRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(UserRepository(session))
    try:
        await service.register(data.email, data.password)
        return {"message": "Registration successful. Please verify your email."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    service = AuthService(UserRepository(session))
    try:
        token = await service.login(data.email, data.password)
        return {"access_token": token}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(token: str, session: AsyncSession = Depends(get_session)):
    service = AuthService(
        UserRepository(session),
        EmailVerificationRepository(session)
    )
    try:
        await service.verify_email(token)
        return {"message": "Email verified successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
