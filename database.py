from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class MongoDB:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("MONGODB_DB", "fin_tech_ai")
        self.client = None
        self.db = None
        self.users = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.users = self.db.users
            # Create unique index on email
            self.users.create_index("email", unique=True)
            print("Connected to MongoDB successfully!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    def create_user(self, user_data: dict):
        try:
            # Hash the password before storing
            user_data["password"] = pwd_context.hash(user_data["password"])
            user_data["created_at"] = datetime.utcnow()
            user_data["updated_at"] = datetime.utcnow()
            
            result = self.users.insert_one(user_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            return {"error": "Email already exists"}
        except Exception as e:
            return {"error": str(e)}

    def authenticate_user(self, email: str, password: str):
        user = self.users.find_one({"email": email})
        if not user:
            return False
        if not pwd_context.verify(password, user["password"]):
            return False
        return user

    def get_user_by_email(self, email: str):
        return self.users.find_one({"email": email}, {"password": 0})  # Exclude password from result
    
    def update_user(self, user_id: str, update_data: dict):
        update_data["updated_at"] = datetime.utcnow()
        return self.users.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )

# Create a single instance to be used across the application
db = MongoDB()
