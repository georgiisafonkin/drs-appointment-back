import uuid
from sqlalchemy import select
from app.infrastructure.db.models import EmailVerificationToken, User
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User):
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: uuid.UUID, **kwargs):
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.commit()
        await self.session.refresh(user)
        return user


class EmailVerificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_token(self, user_id: uuid.UUID, token: str, expires_at: datetime):
        entity = EmailVerificationToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.session.add(entity)
        await self.session.commit()

    async def get_by_token(self, token: str) -> EmailVerificationToken | None:
        result = await self.session.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token == token,
                EmailVerificationToken.expires_at > datetime.utcnow()
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, entity: EmailVerificationToken):
        await self.session.delete(entity)
        await self.session.commit()