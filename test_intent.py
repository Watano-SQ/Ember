import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from brain.llm_client import LLMClient
from config.settings import settings

client = LLMClient()
user_msg = "依鸣，我们现在回到南京大学鼓楼校区图书馆复习吧，别在宿舍睡了！"
msgs = [
    {"role": "system", "content": settings.PRE_ROUTING_PROMPT},
    {"role": "user", "content": f"用户最新输入：{user_msg}"}
]

print("Sending request to small model...")
resp = client.one_chat(settings.SMALL_LLM, msgs, timeout=20, call_type="pre_routing")
print("Raw Response:", resp)
data = client._extract_json(resp)
print("Extracted JSON:", data)
