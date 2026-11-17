import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        self.client = AsyncMongoClient(uri)
        self.db = self.client["moguri_db"]
        self.users = self.db["users"]

    async def get_user(self, user_id: int) -> dict:
        """Retrieve user data or insert default record if missing."""
        user = await self.users.find_one({"_id": user_id})
        if not user:
            user = {
                "_id": user_id,
                "balance": 100,
                "bank": 0
            }
            await self.users.insert_one(user)
        return user

    async def update_balance(self, user_id: int, amount: int):
        """Update wallet balance by adding or subtracting an amount."""
        await self.get_user(user_id)
        return await self.users.update_one(
            {"_id": user_id},
            {"$inc": {"balance": amount}}
        )

    async def update_bank(self, user_id: int, amount: int):
        """Update bank balance by adding or subtracting an amount."""
        await self.get_user(user_id)
        return await self.users.update_one(
            {"_id": user_id},
            {"$inc": {"bank": amount}}
        )

db = Database()
