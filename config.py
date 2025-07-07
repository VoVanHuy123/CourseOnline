import os
from dotenv import load_dotenv
import secrets
import cloudinary
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    SECRET_KEY = secrets.token_hex(32)

    def init_cloudinary():
        cloudinary.config(
            cloud_name="dnzjjdg0v",
            api_key="123958894742992",
            api_secret="kQugdU7BMnVH5E4OYtFLvGKrHfk",
        )