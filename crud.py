from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import *
import models, schemas
from sqlalchemy.future import select
from fastapi.responses import JSONResponse

# 사용자 검색
async def get_user(db: AsyncSession, user_id: int):
    query = select(models.User).filter(models.User.id == user_id)
    result = await db.execute(query)

    return result.scalars().first()

# 사용자 목록 검색
async def get_users(db: AsyncSession):
    query = select(models.User)
    result = await db.execute(query)

    return result.scalars().all()

# 사용자 목록 검색 (페이징)
async def get_users_paging(db: AsyncSession, skip: int = 0, limit: int = 10):
    query = select(models.User).offset(skip).limit(limit)
    result = await db.execute(query)

    return result.scalars().all()

# 사용자 생성
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user

# Email로 사용자 검색
async def get_user_by_email(db: AsyncSession, email: str):
    query = select(models.User).filter(models.User.email == email)
    result = await db.execute(query)

    return result.scalars().first()

# 사용자 정보 업데이트
async def update_user(db: AsyncSession, user:schemas.UserBase):
    db_user = await get_user_by_email(db, user.email)

    if db_user is None:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"User not found"}
        )

    db_user.name = user.name
    db_user.email = user.email

    await db.commit()
    await db.refresh(db_user)

    return db_user
