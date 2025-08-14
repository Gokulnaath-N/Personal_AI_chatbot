from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Response, Cookie, Query
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import os
from dotenv import load_dotenv
import database as db
import secrets
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI with app settings
app = FastAPI(
    title="Fin-TechAI",
    description="AI-Powered Finance Management Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class User(BaseModel):
    email: str
    fullname: Optional[str] = None

class UserInDB(User):
    hashed_password: str

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Try to get token from cookie if not in header
    if not token and access_token:
        token = access_token.replace("Bearer ", "")
    
    # Try to get token from Authorization header if not in cookie
    if not token and "authorization" in request.headers:
        try:
            scheme, token = request.headers["authorization"].strip().split()
            if scheme.lower() != 'bearer':
                raise HTTPException(status_code=400, detail="Invalid authentication scheme")
        except ValueError:
            raise credentials_exception
    
    if not token:
        raise credentials_exception
    
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
            
        # Get user from database
        user = db.get_user_by_email(email=email)
        if not user:
            raise credentials_exception
            
        return user
        
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception from e
    except Exception as e:
        print(f"Unexpected error in get_current_user: {str(e)}")
        raise credentials_exception from e

# App initialization moved to the top of the file

@app.get("/", response_class=HTMLResponse)
async def index(req: Request):
    return templates.TemplateResponse("index.html", {"request": req})

@app.get("/about", response_class=HTMLResponse)
async def about(req: Request):
    return templates.TemplateResponse("about.html", {"request": req})

@app.get("/hello", response_class=HTMLResponse)
async def hello(req: Request):
    return templates.TemplateResponse("hello.html", {"request": req})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(req: Request):
    return templates.TemplateResponse("signup_page.html", {"request": req, "url": req.url_for("signup")})

@app.post("/signup")
async def signup(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        # Check if user already exists using the database method
        existing_user = db.users.find_one({"email": email})
        if existing_user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Email already registered"}
            )
        
        # Create new user data
        user_data = {
            "fullname": fullname,
            "email": email,
            "password": password,  # Will be hashed in create_user
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        
        # Create user in database
        user_id = db.create_user(user_data)
        
        if isinstance(user_id, dict) and "error" in user_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": user_id["error"]}
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, 
            expires_delta=access_token_expires
        )
        
        # Set the access token in a secure HTTP-only cookie
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            samesite="lax",
            secure=request.url.scheme == "https"
        )
        
        return response
        
    except Exception as e:
        print(f"Error in signup: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An error occurred during signup. Please try again."}
        )

@app.post("/login")
async def login_for_access_token(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        # Authenticate user
        user = db.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, 
            expires_delta=access_token_expires
        )
        
        # Determine if we're in production
        is_production = os.getenv("ENV", "development").lower() == "production"
        
        # Set the access token in a secure, httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=is_production,
            path="/"
        )
        
        # Set a non-http-only cookie for client-side auth state
        response.set_cookie(
            key="is_authenticated",
            value="true",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=is_production,
            path="/"
        )
        
        # Return success response
        return {
            "status": "success",
            "message": "Login successful",
            "user": {
                "email": user["email"],
                "fullname": user.get("fullname", ""),
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@app.get("/login", response_class=HTMLResponse)
async def login_page(req: Request):
    return templates.TemplateResponse("logging_page.html", {"request": req, "url": req.url_for("login")})

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        user = db.authenticate_user(email, password)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Incorrect email or password"}
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, 
            expires_delta=access_token_expires
        )
        
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        # Set the access token in an HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=request.url.scheme == "https",
            path="/"
        )
        # Also set a non-http-only cookie for the frontend to read if needed
        response.set_cookie(
            key="is_authenticated",
            value="true",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=request.url.scheme == "https",
            path="/"
        )
        
        return response
        
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An error occurred during login. Please try again."}
        )
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/login"}
            )
            
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request, 
                "user": {
                    "email": current_user["email"], 
                    "fullname": current_user.get("fullname", "")
                }
            },
            headers={"Cache-Control": "no-store, must-revalidate"}
        )
        
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            response = RedirectResponse(
                url="/login",
                status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )
            response.delete_cookie("access_token", path="/")
            response.delete_cookie("is_authenticated", path="/")
            return response
        raise e
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        response = RedirectResponse(
            url="/login",
            status_code=status.HTTP_307_TEMPORARY_REDIRECT
        )
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("is_authenticated", path="/")
        return response

@app.get("/api/user/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
            
        return {
            "status": "success",
            "data": {
                "email": current_user["email"],
                "fullname": current_user.get("fullname", ""),
                "is_active": current_user.get("is_active", True)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in read_users_me: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user data"
        )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
