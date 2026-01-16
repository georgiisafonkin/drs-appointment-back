from datetime import datetime, timedelta
import secrets
from app.infrastructure.db.models import User
from app.infrastructure.db.repository import EmailVerificationRepository, UserRepository
from app.core.security import hash_password, verify_password, create_access_token
from app.core.kafka import publish_email_verification, publish_user_registered

class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        verification_repo: EmailVerificationRepository
    ):
        self.user_repo = user_repo
        self.verification_repo = verification_repo

    async def register(self, email: str, password: str):
        if await self.user_repo.get_by_email(email):
            raise ValueError("User already exists")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_verified=False
        )
        user = await self.user_repo.create(user)

        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=24)

        await self.verification_repo.create_token(
            user.id, token, expires
        )

        await publish_email_verification(
            email=user.email,
            user_id=str(user.id),
            token=token
        )

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        if not user.is_verified:
            raise ValueError("Email not verified")

        return create_access_token(str(user.id))

    async def verify_email(self, token: str):
        record = await self.verification_repo.get_by_token(token)
        if not record:
            raise ValueError("Invalid or expired token")

        user = await self.user_repo.get_by_id(record.user_id)
        if not user:
            raise ValueError("User not found")


        updated_user = await self.user_repo.update(user.id, is_verified=True)
        await self.verification_repo.delete(record)