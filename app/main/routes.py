from flask import Blueprint, request, jsonify
import os
import anthropic
import time
import logging

from ..utils import extract_text_content, chat_with_grace

main = Blueprint('main', __name__)

@main.route('/api/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    history = request.json.get('history', [])

    if not message:
        return jsonify({'response': "Sorry, I couldn't process that message. Please provide a valid message."}), 400

    response = chat_with_grace(message, history)
    return jsonify({'response': response})