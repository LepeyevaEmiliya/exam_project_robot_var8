import speech_recognition as sr
import os

def get_required_color_from_voice():
    recognizer = sr.Recognizer()

    # Используем микрофон для записи
    with sr.Microphone() as source:
        print("Please say the color (green, red, blue) or (зеленый, красный, голубой):")
        
        # Настроим шумоподавление и запишем звук
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            # Попробуем распознать речь сначала на русском, затем на английском
            print("Recognizing...")
            text = None
            # Попытка распознать на русском языке
            try:
                text = recognizer.recognize_google(audio, language="ru-RU").lower()
                print(f"Recognized: {text} (Russian)")
            except sr.UnknownValueError:
                pass  # Не удалось распознать на русском, пробуем английский

            # Если на русском не распознано, пробуем на английском
            if text is None:
                text = recognizer.recognize_google(audio, language="en-US").lower()
                print(f"Recognized: {text} (English)")

            # Проверяем, является ли распознанный текст валидным цветом
            if text in ['green', 'red', 'blue']:
                return text
            elif text == 'красный':
                return 'red'
            elif text == 'зелёный':
                return 'green'
            elif text == 'голубой':
                return 'blue'
            else:
                print("Invalid color. Please try again.")
                return None
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return None

# Получаем цвет с помощью голосового ввода
required_color = get_required_color_from_voice()

# Если цвет валидный, записываем его в файл
if required_color:
    with open("color.txt", "w") as file:
        file.write(required_color)
    print(f"Color '{required_color}' saved to file.")