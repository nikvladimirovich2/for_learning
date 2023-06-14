from googletrans import Translator

# Создаем переводчик
translator = Translator()

# Задаем исходные язык и целевой язык
src = 'en'
dest = 'ru'

# Задаем исходный текст
text = 'Hello, how are you?'

# Переводим текст
translated_text = translator.translate(text, src=src, dest=dest).text

# Выводим переведенное предложение
print(translated_text)