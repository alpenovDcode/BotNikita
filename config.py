import openai
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

API_TOKEN = "6786447329:AAGBjuy7GKD1TK-mNYqkO8h2EgH3FNDdtPI"
ADMINS = [6139227440, 6977471553]

api_key = "sk-proj-DBC69MSUGsscp914JnkaT3BlbkFJ7e3CYFFPPMTPudr1sVNU"
openai.api_key = api_key

def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150  # Установите ограничение на количество токенов
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError as e:
        logger.error(f"Quota exceeded: {e}")
        return "Вы превысили лимит использования API. Пожалуйста, проверьте ваш план и детали биллинга."
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Произошла ошибка при генерации ответа."
