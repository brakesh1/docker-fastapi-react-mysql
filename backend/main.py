from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import models
from database import SessionLocal, engine
from crud import user_create, user_get, check_email, check_username, user_update
from schemas import UserCreate, User, UserUpdate
from utils import create_access_token, verify_password
from sqlalchemy.orm import Session

app = FastAPI(root_path="/api")
models.Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_create(db, user)
    token = create_access_token(data={"sub": db_user.username})
    return {"id":db_user.id,
            "first_name":db_user.first_name,
            "last_name":db_user.last_name,
            "username":db_user.username,
            "email":db_user.email,
            "access_token": token,
            "token_type": "bearer"}
    

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user and verify_password(user.password, db_user.password_hash):
        token = create_access_token(data={"sub": db_user.username})
        return {"access_token": token, "token_type": "bearer", "user_id": db_user.id}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@app.get("/users/emails/{user_email}")
def user_email(user_email: str, db: Session = Depends(get_db)):
    isEmail = check_email(db, user_email)
    if isEmail:
        return {"emailPresent": "true"}
    else:
        return {"emailPresent": "false"}
    
@app.get("/users/usernames/{user_username}")
def user_username(user_username: str, db: Session = Depends(get_db)):
    isusername = check_username(db, user_username)
    if isusername:
        return {"usernamePresent": "true"}
    else:
        return {"usernamePresent": "false"}

@app.get("/users/{user_id}", response_model=User)
def user_get_details(user_id: int, db: Session = Depends(get_db)):
    return user_get(db, user_id)

@app.put("/users/{user_id}", response_model=User)
def edit_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    return user_update(db, user_id, user)

