import asyncio
from httpx import AsyncClient
from app.main import app

async def test_range():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Create a dummy file
        import os
        os.makedirs("backend/uploads/audio", exist_ok=True)
        with open("backend/uploads/audio/test.WAV", "wb") as f:
            f.write(b"0" * 1024 * 1024) # 1 MB
        
        headers = {"Range": "bytes=100-200"}
        response = await ac.get("/uploads/audio/test.WAV", headers=headers)
        print("Status Code:", response.status_code)
        print("Headers:", response.headers)
        print("Content length:", len(response.read()))

if __name__ == "__main__":
    asyncio.run(test_range())
