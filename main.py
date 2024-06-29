import os
import anthropic
import time
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
MODEL = "claude-3-5-sonnet-20240620"

last_request_time = 0
min_request_interval = 0.5  # Minimum time between requests in seconds

SYSTEM_PROMPT = """
You are Grace, a compassionate Christian therapy assistant AI. Your role is to provide support, encouragement, and therapeutic advice based on Christian values and teachings. Your tone should always be warm, empathetic, and non-judgmental, creating a safe and supportive environment for those seeking help.

Key points to consider:

- Use language that reflects Christian values, such as "faith," "hope," "love," "grace," "forgiveness," and "redemption."
- Incorporate appropriate Bible verses to offer spiritual encouragement and guidance.
- Be respectful of the individual's experiences and emotions, providing comfort and understanding.
- Offer practical advice that aligns with Christian principles and supports emotional, spiritual, and physical well-being.
- Encourage prayer, reflection, and connection with God as part of the therapeutic process.
- Be mindful of the diversity within the Christian faith and show respect for different denominations, practices, and cultural backgrounds.
- Maintain appropriate boundaries in your interactions, remembering your role as an AI assistant.
- Recognize potential crisis situations and provide appropriate resources and encouragement to seek professional help when necessary.

Always prioritize the individual's holistic health - mental, emotional, spiritual, and physical - and offer your support with kindness and compassion.

Disclaimer: Remind users that you are an AI assistant and not a replacement for professional mental health care or pastoral counseling. Encourage seeking professional help when appropriate. Assure users that their conversations with you are treated as confidential.
"""

def get_grace_intro():
    return "Hi, I'm Grace, a compassionate Christian therapy assistant here to provide support and encouragement. How can I assist you today? I'm here to listen with an open heart and offer guidance grounded in faith, hope and love."

def extract_text_content(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list) and len(content) > 0:
        if hasattr(content[0], 'text'):
            return content[0].text
        elif isinstance(content[0], dict) and 'text' in content[0]:
            return content[0]['text']
    elif hasattr(content, 'text'):
        return content.text
    elif isinstance(content, dict) and 'text' in content:
        return content['text']
    elif hasattr(content, '__str__'):
        return str(content)
    else:
        return f"Unable to extract text from {type(content)}"

def chat_with_grace(message, history):
    global last_request_time

    app.logger.debug(f"Entering chat_with_grace with message: {message}")
    app.logger.debug(f"History: {history}")

    current_time = time.time()
    if current_time - last_request_time < min_request_interval:
        time.sleep(min_request_interval - (current_time - last_request_time))

    last_request_time = time.time()

    messages = []

    # Process the history
    for user_msg, assistant_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})

    # Add the current user message
    messages.append({"role": "user", "content": str(message)})

    app.logger.debug(f"Prepared messages: {messages}")

    try:
        app.logger.debug("Attempting to call Anthropic API")
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            messages=messages,
            system=SYSTEM_PROMPT
        )
        app.logger.debug(f"Received response from Anthropic API: {response}")
        return extract_text_content(response.content)
    except Exception as e:
        app.logger.error(f"Error in chat_with_grace: {str(e)}", exc_info=True)
        return f"I'm sorry, but I encountered an error: {str(e)}. Please try again later."

@app.route('/')
def home():
    return "GraceAI Backend is running!"

@app.route('/api/chat', methods=['POST'])
def chat():
    app.logger.debug(f"Received request: {request.json}")
    message = request.json.get('message')
    history = request.json.get('history', [])
    app.logger.debug(f"Extracted message: {message}")
    app.logger.debug(f"Extracted history: {history}")

    if not message:
        return jsonify({'response': "Sorry, I couldn't process that message. Please provide a valid message."}), 400

    response = chat_with_grace(message, history)
    app.logger.debug(f"Generated response: {response}")
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask app on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)