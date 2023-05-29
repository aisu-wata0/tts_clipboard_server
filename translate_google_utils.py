
from googletrans import Translator

translator = Translator()

def translateText(text, src='en', dest='ja') -> str:
  response_jp = translator.translate(text, src=src, dest=dest)
  return response_jp.text
