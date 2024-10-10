from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import models, schemas, crud
from database import AsyncSessionDev, engine

app = FastAPI()

# 데이터베이스 연결을 위해 테이블 생성
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# 의존성 주입을 통해 데이터베이스 세션을 제공하는 함수
def get_db():
    db = AsyncSessionDev()
    try:
        yield db
    finally:
        db.close()

# 사용자 생성 엔드포인트
@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# 특정 사용자 조회 엔드포인트
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 전체 사용자 조회 엔드포인트
@app.get("/users/", response_model=list[schemas.UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users
