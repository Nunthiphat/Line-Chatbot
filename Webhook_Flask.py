from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import requests
import os

app = Flask(__name__)

# กำหนด LINE API Token
LINE_ACCESS_TOKEN = "5sxR4J8CysZz32B5ZRrITOv3qk7qx5ldZQCNSNR3rfKTSMwWOvy1GdHgCzcR/RkP9eyPhWGRFU67Xi+RHO7NnXTkAvIy2O8V3znV0e2JCMB4jyA9d5xxWyy4k+WMUxoWAR3mvpffxko6cVLRKcG5MAdB04t89/1O/w1cDnyilFU="
LINE_SECRET = "6ebdf06d2ba5be7fa285845b9a08068a"
API_URL = "https://ml-model-production-58e2.up.railway.app/predict/"  # URL API ที่โฮสต์บน Railway

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    # ตัวอย่าง: แยกค่า input ออกจากข้อความ (ผู้ใช้ต้องพิมพ์ค่าในรูปแบบ age,blood_pressure,cholesterol)
    try:
        age, blood_pressure, cholesterol = map(float, user_text.split(","))
        data = {"age": age, "blood_pressure": blood_pressure, "cholesterol": cholesterol}
        
        # ส่งข้อมูลไปยัง API บน Railway
        response = requests.post(API_URL, json=data)
        result = response.json().get("prediction", "ไม่สามารถทำนายได้")

        reply_message = f"ผลลัพธ์การทำนาย: {result}"

    except Exception:
        reply_message = "โปรดป้อนข้อมูลในรูปแบบ: อายุ,ความดันโลหิต,คอเลสเตอรอล (เช่น 50,120,200)"

    # ส่งข้อความกลับไปหา user
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # ใช้ PORT ที่ Railway กำหนด
    app.run(host="0.0.0.0", port=port, debug=True)