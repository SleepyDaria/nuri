from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class TransactionStatus(str, Enum):
    ACTIVE = "active"
    MATCHED = "matched"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class UserRole(str, Enum):
    USER = "user"
    MODERATOR = "moderator"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    phone: str
    id_document: str  # For verification
    city: str
    rating: float = 5.0
    total_transactions: int = 0
    role: UserRole = UserRole.USER
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    phone: str
    id_document: str
    city: str

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    amount: float
    currency: str
    from_city: str
    to_city: str
    recipient_name: str
    recipient_details: str
    status: TransactionStatus = TransactionStatus.ACTIVE
    matched_transaction_id: Optional[str] = None
    matched_user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class TransactionCreate(BaseModel):
    title: str
    description: str
    amount: float
    currency: str
    from_city: str
    to_city: str
    recipient_name: str
    recipient_details: str

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transaction_id: str
    sender_id: str
    receiver_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatMessageCreate(BaseModel):
    transaction_id: str
    receiver_id: str
    message: str

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rater_id: str
    rated_user_id: str
    transaction_id: str
    rating: int  # 1-5
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RatingCreate(BaseModel):
    rated_user_id: str
    transaction_id: str
    rating: int
    comment: str

# Major world cities list
MAJOR_CITIES = [
    "New York", "London", "Tokyo", "Paris", "Berlin", "Moscow", "Beijing",
    "Shanghai", "Mumbai", "Delhi", "Bangkok", "Singapore", "Hong Kong",
    "Dubai", "Istanbul", "Cairo", "Lagos", "Johannesburg", "São Paulo",
    "Rio de Janeiro", "Buenos Aires", "Mexico City", "Toronto", "Sydney",
    "Melbourne", "Seoul", "Osaka", "Kuala Lumpur", "Jakarta", "Manila",
    "Ho Chi Minh City", "Hanoi", "Dhaka", "Karachi", "Tehran", "Baghdad",
    "Riyadh", "Tel Aviv", "Athens", "Rome", "Madrid", "Barcelona",
    "Amsterdam", "Brussels", "Vienna", "Prague", "Warsaw", "Stockholm",
    "Copenhagen", "Helsinki", "Oslo", "Zurich", "Geneva", "Milan",
    "Naples", "Lisbon", "Dublin", "Edinburgh", "Manchester", "Liverpool",
    "Birmingham", "Glasgow", "Cardiff", "Montreal", "Vancouver", "Calgary",
    "Chicago", "Los Angeles", "San Francisco", "Miami", "Boston",
    "Washington D.C.", "Atlanta", "Dallas", "Houston", "Phoenix",
    "Philadelphia", "San Diego", "Seattle", "Las Vegas", "Detroit"
]

# User routes
@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    # Check if username or email already exists
    existing_user = await db.users.find_one({
        "$or": [
            {"username": user_data.username},
            {"email": user_data.email}
        ]
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    user = User(**user_data.dict())
    await db.users.insert_one(user.dict())
    return user

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(100)
    return [User(**user) for user in users]

# Cities route
@api_router.get("/cities")
async def get_cities():
    return {"cities": sorted(MAJOR_CITIES)}

# Transaction routes
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate, user_id: str):
    # Verify user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transaction_dict = transaction_data.dict()
    transaction_dict["user_id"] = user_id
    transaction = Transaction(**transaction_dict)
    await db.transactions.insert_one(transaction.dict())
    return transaction

@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions(city: Optional[str] = None, status: Optional[str] = None):
    query = {}
    if city:
        query["$or"] = [{"from_city": city}, {"to_city": city}]
    if status:
        query["status"] = status
    
    transactions = await db.transactions.find(query).sort("created_at", -1).to_list(100)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.get("/transactions/user/{user_id}", response_model=List[Transaction])
async def get_user_transactions(user_id: str):
    transactions = await db.transactions.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    return [Transaction(**transaction) for transaction in transactions]

@api_router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    transaction = await db.transactions.find_one({"id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return Transaction(**transaction)

# Matching routes
@api_router.get("/transactions/{transaction_id}/matches", response_model=List[Transaction])
async def find_matches(transaction_id: str):
    # Get the original transaction
    transaction = await db.transactions.find_one({"id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Find potential matches (reverse direction)
    matches = await db.transactions.find({
        "from_city": transaction["to_city"],
        "to_city": transaction["from_city"],
        "status": "active",
        "id": {"$ne": transaction_id}
    }).to_list(50)
    
    return [Transaction(**match) for match in matches]

@api_router.post("/transactions/{transaction_id}/match/{match_id}")
async def create_match(transaction_id: str, match_id: str, user_id: str):
    # Update both transactions to matched status
    await db.transactions.update_one(
        {"id": transaction_id},
        {
            "$set": {
                "status": "matched",
                "matched_transaction_id": match_id,
                "matched_user_id": user_id
            }
        }
    )
    
    await db.transactions.update_one(
        {"id": match_id},
        {
            "$set": {
                "status": "matched",
                "matched_transaction_id": transaction_id
            }
        }
    )
    
    return {"message": "Match created successfully"}

# Chat routes
@api_router.post("/chat", response_model=ChatMessage)
async def send_message(message_data: ChatMessageCreate, sender_id: str):
    message_dict = message_data.dict()
    message_dict["sender_id"] = sender_id
    message = ChatMessage(**message_dict)
    await db.chat_messages.insert_one(message.dict())
    return message

@api_router.get("/chat/{transaction_id}", response_model=List[ChatMessage])
async def get_messages(transaction_id: str):
    messages = await db.chat_messages.find({"transaction_id": transaction_id}).sort("timestamp", 1).to_list(1000)
    return [ChatMessage(**message) for message in messages]

# Admin/Moderator routes
@api_router.post("/admin/approve/{transaction_id}")
async def approve_transaction(transaction_id: str, moderator_id: str):
    # Verify moderator
    moderator = await db.users.find_one({"id": moderator_id})
    if not moderator or moderator["role"] != "moderator":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update transaction status
    await db.transactions.update_one(
        {"id": transaction_id},
        {
            "$set": {
                "status": "approved",
                "approved_by": moderator_id,
                "approved_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Transaction approved"}

@api_router.post("/admin/request-approval")
async def request_approval(transaction_id: str, match_id: str):
    # Update both transactions to pending approval
    await db.transactions.update_one(
        {"id": transaction_id},
        {"$set": {"status": "pending_approval"}}
    )
    
    await db.transactions.update_one(
        {"id": match_id},
        {"$set": {"status": "pending_approval"}}
    )
    
    return {"message": "Approval requested"}

# Rating routes
@api_router.post("/ratings", response_model=Rating)
async def create_rating(rating_data: RatingCreate, rater_id: str):
    rating_dict = rating_data.dict()
    rating_dict["rater_id"] = rater_id
    rating = Rating(**rating_dict)
    await db.ratings.insert_one(rating.dict())
    
    # Update user's average rating
    ratings = await db.ratings.find({"rated_user_id": rating_data.rated_user_id}).to_list(1000)
    avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
    
    await db.users.update_one(
        {"id": rating_data.rated_user_id},
        {"$set": {"rating": round(avg_rating, 1)}}
    )
    
    return rating

@api_router.get("/ratings/{user_id}", response_model=List[Rating])
async def get_user_ratings(user_id: str):
    ratings = await db.ratings.find({"rated_user_id": user_id}).sort("created_at", -1).to_list(100)
    return [Rating(**rating) for rating in ratings]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()