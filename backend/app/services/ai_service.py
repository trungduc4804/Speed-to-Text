import json
from google import genai
from google.genai import types
from app.core.config import settings

def analyze_transcript(transcript: str) -> dict:
    """
    Analyzes a given meeting transcript using Gemini.
    Returns a dictionary containing 'summary' and 'action_items'.
    """
    if not settings.GEMINI_API_KEY:
        return {
            "summary": "Không thể tạo tóm tắt do chưa cấu hình GEMINI_API_KEY.",
            "action_items": []
        }

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        prompt = f"""
        Bạn là một trợ lý AI chuyên nghiệp thư ký cuộc họp. Hãy đọc kỹ nội dung biên bản cuộc họp sau và thực hiện 2 việc:
        1. Viết một đoạn tóm tắt ngắn gọn nhất (khoảng 2-3 câu) về những nội dung chính đã được thảo luận.
        2. Liệt kê các công việc cần làm (action items) dựa vào nội dung biên bản. Ai được giao việc gì? 

        Trả về kết quả DƯỚI DẠNG JSON với cấu trúc chính xác như sau:
        ```json
        {{
            "summary": "Nội dung tóm tắt ở đây...",
            "action_items": [
                "Công việc 1...",
                "Công việc 2..."
            ]
        }}
        ```

        Nội dung cuộc họp:
        \"\"\"
        {transcript[:15000]} 
        \"\"\"
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        response_text = response.text
        
        # Simple extraction of JSON block from markdown if present
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()
            
        data = json.loads(json_str)
        return {
            "summary": data.get("summary", ""),
            "action_items": data.get("action_items", [])
        }
        
    except Exception as e:
        print(f"Lỗi AI Service: {e}")
        return {
            "summary": f"Đã xảy ra lỗi khi gọi AI: {str(e)}",
            "action_items": []
        }
