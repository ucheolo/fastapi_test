from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import *
import models, schemas, crud
from database import AsyncSessionDev, engine
import uvicorn

# 데이터베이스 연결을 위해 테이블 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield  # lifespan 이벤트 종료 시점

app = FastAPI(lifespan=lifespan)

# 의존성 주입을 통해 데이터베이스 세션을 제공하는 함수
async def get_db():
    async with AsyncSessionDev() as db:
        try:
            yield db
        finally:
            db.close()

# 사용자 생성 엔드포인트
@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"Email already registered"}
        )
    return await crud.create_user(db=db, user=user)

# 특정 사용자 조회 엔드포인트
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# 전체 사용자 조회 엔드포인트
@app.get("/users/", response_model=list[schemas.UserResponse])
async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    users = await crud.get_users(db, skip=skip, limit=limit)
    return users

# main.py가 직접 실행될 때 uvicorn을 실행하도록 설정
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)