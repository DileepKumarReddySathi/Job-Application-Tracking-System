from dotenv import load_dotenv
import os

# Load .env using absolute path
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

from app.database import engine
from app.models import Base

Base.metadata.create_all(engine)
print("✅ Tables created successfully")
