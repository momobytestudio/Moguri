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

    @staticmethod
    def format_number(n: int) -> str:
        """Convert large numbers into readable alphabetical abbreviations up to zillion."""
        if n < 1000:
            return str(n)

        # Alphabetical number tiers (Short Scale)
        suffixes = [
            "", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", 
            "Dc", "UDc", "DDc", "TDc", "QaDc", "QiDc", "SxDc", "SpDc", "ODc", "NDc", 
            "Vg", "UVg", "DVg", "TVg", "QaVg", "QiVg", "SxVg", "SpVg", "OVg", "NVg",
            "Tg", "UTg", "DTg", "TTg", "QaTg", "QiTg", "SxTg", "SpTg", "OTg", "NTg",
            "Qag", "UQag", "DQag", "TQag", "QaQag", "QiQag", "SxQag", "SpQag", "OQag", "NQag",
            "Qig", "UQig", "DQig", "TQig", "QaQig", "QiQig", "SxQig", "SpQig", "OQig", "NQig",
            "Sxg", "USxg", "DSxg", "TSxg", "QaSxg", "QiSxg", "SxSxg", "SpSxg", "OSxg", "NSxg",
            "Spg", "USpg", "DSpg", "TSpg", "QaSpg", "QiSpg", "SxSpg", "SpSpg", "OSpg", "NSpg",
            "Ocg", "UOcg", "DOcg", "TOcg", "QaOcg", "QiOcg", "SxOcg", "SpOcg", "OOcg", "NOcg",
            "Nog", "UNog", "DNog", "TNog", "QaNog", "QiNog", "SxNog", "SpNog", "ONog", "NNog",
            "VgN", "UvN", "DvN", "TvN", "Qav", "Qiv", "Sxv", "Spv", "Ocv", "Nov",
            "Zillion" # Scale cap
        ]

        import math
        tier = int(math.floor(math.log10(abs(n)) / 3))
        
        if tier >= len(suffixes):
            return "Zillion+"

        suffix = suffixes[tier]
        scale = math.pow(10, tier * 3)
        scaled = n / scale

        return f"{scaled:.2f}".rstrip("0").rstrip(".") + suffix

db = Database()
