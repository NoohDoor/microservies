from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from dateutil import parser
from pydantic import BaseModel, Field, validator
from typing import List
from passlib.hash import bcrypt
import datetime
from jose import JWTError, jwt


# Definiert Konfigurationsvariablen für Authentifizierung und Datenbankverbindung

SECRET_KEY = "my_secret_key"  
ALGORITHM = "HS256"  # Algorithmus für die JWT-Authentifizierung

DATABASE_URL = "sqlite:///./test.db"

# Erstelle das Datenbankmodell und die Tabellenstruktur
Base = declarative_base()

# Definiert die User-Tabelle
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Definiert die Task-Tabelle
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    due_date = Column(DateTime)
    assigned_to = Column(Integer)
    created_by = Column(Integer)

# Erstellt die Datenbank und verbindet sie mit der definierten Struktur
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(bind=engine)

# Erstellt eine Session, um mit der Datenbank zu interagieren
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Funktion, um eine Datenbankverbindung zu erstellen und zu schließen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Erstellt die FastAPI-Anwendung
app = FastAPI()

# Definiert den Authentifizierungsschutz mit OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Definiert Pydantic-Modelle für Benutzer- und Aufgabenobjekte
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

# UserInDB-Klasse erweitert die UserCreate-Klasse um die Benutzer-ID
class UserInDB(UserCreate):
    id: int

    class Config:
        orm_mode = True  # Diese Einstellung ermöglicht die Verwendung von ORM-Objekten (z.B. SQLAlchemy) mit Pydantic

# TaskCreate-Klasse definiert die Felder, die zum Erstellen einer Aufgabe benötigt werden
class TaskCreate(BaseModel):
    name: str
    description: str
    due_date: str
    assigned_to: int

    # Validator-Methode, um das due_date-Feld zu überprüfen und in ein datetime-Objekt umzuwandeln
    @validator('due_date')
    def parse_due_date(cls, due_date):
        try:
            return parser.parse(due_date)  # Versucht, das angegebene Datum zu analysieren und zurückzugeben
        except ValueError:
            raise ValueError("Incorrect date format")  # Bei falschem Format wird ein ValueError ausgelöst

# TaskInDB-Klasse erweitert die TaskCreate-Klasse um die Aufgaben-ID und den Ersteller der Aufgabe
class TaskInDB(TaskCreate):
    id: int
    created_by: int

    class Config:
        orm_mode = True  # Diese Einstellung ermöglicht die Verwendung von ORM-Objekten (z.B. SQLAlchemy) mit Pydantic

    # Validator-Methode, um das due_date-Feld vor der Rückgabe in ein ISO-Format-String umzuwandeln
    @validator('due_date', pre=True)
    def format_due_date(cls, due_date):
        return due_date.isoformat()  # Wandelt das datetime-Objekt in einen ISO-Format-String um


# Definiert Funktionen für Benutzeroperationen (Erstellen, Abrufen, Aktualisieren, Löschen)
# und Aufgabenoperationen (Erstellen, Abrufen, Aktualisieren, Löschen, Abrufen von Aufgaben für einen Benutzer)
# An sich wären es zwei getrennte Services, jedoch hatten wir Probleme mit dem ForeignKey und deshalb ist es hier etwas Monolith mäßig aufgebaut


# Funktion zum Erstellen eines neuen Benutzers
def create_user(db: Session, user: UserCreate):
    hashed_password = bcrypt.hash(user.password)
    db_user = User(name=user.name, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Funktion zum Abrufen eines Benutzers anhand der Benutzer-ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Funktion zum Abrufen eines Benutzers anhand der E-Mail-Adresse
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Funktion zum Aktualisieren eines Benutzers
def update_user(db: Session, user_id: int, user: UserCreate):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db_user.name = user.name
    db_user.email = user.email
    db_user.password = bcrypt.hash(user.password)
    db.commit()
    db.refresh(db_user)
    return db_user

# Funktion zum Löschen eines Benutzers
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}

# Funktion zum Erstellen einer neuen Aufgabe
def create_task(db: Session, task: TaskCreate, user_id: int):
    db_task = Task(name=task.name, description=task.description, due_date=task.due_date, assigned_to=task.assigned_to, created_by=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Funktion zum Abrufen der Email durch den Token
def get_user_email_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")
        return user_email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")

# Funktion zum Abrufen des aktuellen Users anhand des Tokens
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserInDB:
    user_email = get_user_email_from_token(token)
    user = get_user_by_email(db, user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserInDB(**user.__dict__)

# Funktion zum Abrufen einer Aufgabe anhand der Aufgaben-ID
def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()

# Funktion zum Aktualisieren einer Aufgabe
def update_task(db: Session, task_id: int, task: TaskCreate):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db_task.name = task.name
    db_task.description = task.description
    db_task.due_date = task.due_date
    db_task.assigned_to = task.assigned_to
    db.commit()
    db.refresh(db_task)
    return db_task

# Funktion zum Löschen einer Aufgabe
def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(db_task)
    db.commit()
    return {"detail": "Task deleted"}

# Funktion zum Abrufen von Aufgaben für einen bestimmten Benutzer
def get_tasks_for_user(db: Session, user_id: int):
    return db.query(Task).filter(Task.assigned_to == user_id).all()

# Funktion zur Authentifizierung eines Benutzers (überprüft E-Mail und Passwort)
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not bcrypt.verify(password, user.password):
        return False
    return user

# Funktion zum Erstellen eines Access Tokens für einen Benutzer
def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# FastAPI-Endpunkte für Benutzer- und Aufgabenoperationen
# Erstellt Benutzer, holt Benutzer, aktualisiert Benutzer, löscht Benutzer
# Erstellt Aufgabe, holt Aufgabe, aktualisiert Aufgabe, löscht Aufgabe, holt Aufgaben für einen Benutzer

@app.post("/user", response_model=UserInDB)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return create_user(db=db, user=user)

@app.get("/user/{user_id}", response_model=UserInDB)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@app.put("/user/{user_id}", response_model=UserInDB)
def update_user_endpoint(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    return update_user(db=db, user_id=user_id, user=user)

@app.delete("/user/{user_id}")
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return delete_user(db=db, user_id=user_id)

@app.post("/task", response_model=TaskInDB)
def create_task_endpoint(task: TaskCreate, db: Session = Depends(get_db), user: UserInDB = Depends(get_current_user)):
    return create_task(db=db, task=task, user_id=user.id)

@app.get("/task/{task_id}", response_model=TaskInDB)
def get_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    db_task = get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task

@app.put("/task/{task_id}", response_model=TaskInDB)
def update_task_endpoint(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    return update_task(db=db, task_id=task_id, task=task)

@app.delete("/task/{task_id}")
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    return delete_task(db=db, task_id=task_id)

@app.get("/task", response_model=List[TaskInDB])
def get_tasks_for_user_endpoint(assignee_id: int, db: Session = Depends(get_db)):
    tasks = get_tasks_for_user(db=db, user_id=assignee_id)
    return tasks

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}