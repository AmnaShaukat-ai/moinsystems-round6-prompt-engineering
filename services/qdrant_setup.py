import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# ========================================
# 1. LOAD ENV VARIABLES
# ========================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "moinsystems_knowledge")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing in .env")

if not QDRANT_URL:
    raise ValueError("QDRANT_URL missing in .env")

# ========================================
# 2. INITIALIZE CLIENTS
# ========================================

client = OpenAI(api_key=OPENAI_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

# ========================================
# 3. LOAD EXCEL KNOWLEDGE BASE
# ========================================

excel_file = "MoinSystems_AI_Public_Chatbot_RAG_Dataset_v2 (1).xlsx"

print("Loading Excel:", excel_file)

df = pd.read_excel(excel_file, sheet_name="RAG_Knowledge")

print("Total records:", len(df))

# ========================================
# 4. GENERATE EMBEDDINGS
# ========================================

embeddings = []

print("Generating embeddings...")

for text in df["Embedding Text"]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    embeddings.append(response.data[0].embedding)

print("Embeddings generated:", len(embeddings))

# ========================================
# 5. CREATE COLLECTION IN QDRANT CLOUD
# ========================================

print("Deleting old collection (if exists)...")
qdrant.delete_collection(QDRANT_COLLECTION)

print("Creating new collection:", QDRANT_COLLECTION)

qdrant.create_collection(
    collection_name=QDRANT_COLLECTION,
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

# ========================================
# 6. UPLOAD POINTS
# ========================================

points = []

print("Uploading points to Qdrant Cloud...")

for i, (_, row) in enumerate(df.iterrows()):
    points.append(
        PointStruct(
            id=i,
            vector=embeddings[i],
            payload={
                "id": row["ID"],
                "title": row["Title"],
                "category": row["Category"],
                "tags": row["Tags"],
                "intents": row["Intents"],
                "text": row["Embedding Text"],
                "data_status": row["Data Status"]
            }
        )
    )

qdrant.upsert(
    collection_name=QDRANT_COLLECTION,
    points=points
)

print("Qdrant Cloud updated successfully!")
print("Total points uploaded:", len(points))
