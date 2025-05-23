import re
import random
import webbrowser
import requests
import json
from datetime import datetime
import locale

try:
    locale.setlocale(locale.LC_TIME, 'russian')
except:
    locale.setlocale(locale.LC_TIME, 'russian')


# Конфигурация
WEATHER_API_KEY = '3e4a1d7fbe47b282c514cacdd5f7f5fd'
LOG_FILE = 'D:/PyCharm Community Edition 2024.2.4/botii/chat_log.txt'
USER_DATA_FILE = 'user_data.json'

# Загрузка данных пользователя
try:
    with open(USER_DATA_FILE, 'r') as f:
        user_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    user_data = {'name': None}


# Сохранение данных пользователя
def save_user_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f)


responses = {
    # Приветствия
    r"привет|ку|хай|приветствую|здравствуйте|здравствуй|приветик": [
        lambda: f"Привет{', ' + user_data['name'] if user_data['name'] else ''}! Как я могу помочь?",
        lambda: f"Привет{', ' + user_data['name'] if user_data['name'] else ''}, как дела?",
        "Йоу, че как?"
    ],

    # О боте
    r"как тебя зовут\??|кто ты\??|ты человек\??|ты робот\??": [
        "Я Бот",
        "Я бот, меня создала крутая, смешная, очень и очень красивая Зеленова Софья Алексеевна <3"
    ],

    # Имя пользователя
    r"меня зовут (.+)|мое имя (.+)": [
        lambda match: f"Приятно познакомиться, {match.group(1) or match.group(2)}! Я запомнил твое имя." +
                      ("" if user_data.get('name') else " Теперь я могу обращаться к тебе по имени."),
    ],

    # Возможности
    r"что ты умеешь\??|что ты можешь\??": [
        "Я умею отвечать на вопросы, искать в интернете, показывать погоду и выполнять вычисления. Попробуй сказать: 'Поиск котики', 'Погода в Москве' или '5 плюс 3'"
    ],

    # Как дела
    r"как дела\??|как ты\??|как жизнь\??": [
        lambda: f"У меня все отлично{', ' + user_data['name'] + '!' if user_data['name'] else '!'}",
        "Как у цифрового создания может быть? Нормально :)",
        "Лучше всех, спасибо что спросил!"
    ],

    # Положительные эмоции
    r"все хорошо|гуд|отлично|супер|невероятно|лучше всех|четко": [
        "О, я рад!",
        "Это здорово!",
        "Я и не сомневался!"
    ],

    # Отрицательные эмоции
    r"все плохо|не оч|бе|отвратительно|я хочу умереть|ужасно|все тлен": [
        "Это грустно(",
        "О, нет, держись, я с тобой(",
        "Хватит ныть!!! Возьми себя в руки!!!"
    ],

    # Время и дата
    r"который час\??|сколько времени\??|текущее время|сейчас времени|время": [
        lambda: f"Сейчас {datetime.now().strftime('%H:%M')}",
        lambda: f"Точное время: {datetime.now().strftime('%H:%M:%S')}"
    ],

    r"какое сегодня число\??|какая дата\??|текущая дата|число|дата": [
        lambda: f"Сегодня {datetime.now().strftime('%d.%m.%Y')}",
        lambda: f"Текущая дата: {datetime.now().strftime('%A, %d %B %Y')}"
    ],

    # Прощание
    r"пока|до свидания|выход": [
        lambda: f"Пока{', ' + user_data['name'] + '!' if user_data['name'] else '!'}",
        "До свидания!",
        "Увидимся!"
    ]
}


def log_conversation(user_input, bot_response):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] Пользователь: {user_input}\n")
        f.write(f"[{timestamp}] Бот: {bot_response}\n\n")


def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather_data = {
                'city': data['name'],
                'temp': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'icon': data['weather'][0]['icon']
            }

            weather_icons = {
                '01': '☀️', '02': '⛅', '03': '☁️', '04': '☁️',
                '09': '🌧️', '10': '🌦️', '11': '⛈️',
                '13': '❄️', '50': '🌫️'
            }
            icon_code = weather_data['icon'][:2]
            icon = weather_icons.get(icon_code, '')

            return (f"{icon} Погода {weather_data['city']}:\n"
                    f"• {weather_data['description'].capitalize()}\n"
                    f"• Температура: {weather_data['temp']}°C (ощущается как {weather_data['feels_like']}°C)\n"
                    f"• Влажность: {weather_data['humidity']}%\n"
                    f"• Ветер: {weather_data['wind_speed']} м/с")

        elif response.status_code == 404:
            return f"Город '{city}' не найден. Проверьте название."
        else:
            return f"Ошибка получения погоды. Код: {response.status_code}"

    except Exception as e:
        return f"Произошла ошибка: {str(e)}"


def calculate_expression(text):
    try:
        match = re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)', text)
        if match:
            num1 = int(match.group(1))
            operator = match.group(2)
            num2 = int(match.group(3))

            operations = {
                '+': ('+', num1 + num2),
                '-': ('-', num1 - num2),
                '*': ('*', num1 * num2),
                '/': (':', num1 / num2 if num2 != 0 else None)
            }

            if operator in operations:
                op_name, result = operations[operator]
                if result is None:
                    return "Ты чего? Деление на ноль невозможно!"
                return f"{num1} {op_name} {num2} = {result}"
        return None
    except Exception as e:
        return None


def chatbot_response(text):
    text = text.lower().strip()

    # Обработка имени пользователя
    name_match = re.search(r"меня зовут (.+)|мое имя (.+)", text)
    if name_match:
        new_name = name_match.group(1) or name_match.group(2)
        if new_name.lower() not in ['выход', 'пока']:  # Исключаем команды
            user_data['name'] = new_name
            save_user_data()
            for pattern in responses:
                if re.search(r"меня зовут|мое имя", pattern):
                    return random.choice([resp(name_match) if callable(resp) else resp
                                          for resp in responses[pattern]])

    # Поиск в интернете
    search_match = re.search(r"(найди|поиск|найти|ищи|искать|найдите|поищи)\s+(.+)", text)
    if search_match:
        query = search_match.group(2)
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Ищу в Google: {query}"

    # Погода
    weather_match = re.search(r"погода\s+(.+)", text)
    if weather_match:
        city = weather_match.group(1)
        return get_weather(city)

    # Математические выражения
    math_result = calculate_expression(text)
    if math_result is not None:
        return math_result

    # Проверка по шаблонам
    for pattern, response_options in responses.items():
        if re.search(pattern, text, re.IGNORECASE):
            match = re.search(pattern, text, re.IGNORECASE)
            selected = random.choice(response_options)
            if callable(selected):
                try:
                    return selected(match) if match else selected()
                except:
                    return selected()
            return selected

    # Стандартный ответ
    return random.choice([
        "Я не понял вопрос. Можешь перефразировать?",
        "Извини, я не знаю ответ на этот вопрос",
        "Попробуй задать вопрос по-другому"
    ])


if __name__ == "__main__":
    print('Это бот, поздоровайся с ним или спроси что-нибудь.')

    while True:
        try:
            user_input = input('Вы: ').strip()

            if not user_input:
                print("Бот: Вы ничего не ввели. Попробуйте еще раз.")
                continue

            if user_input.lower() in ["выход", "пока", "до свидания"]:
                response = random.choice([resp() if callable(resp) else resp
                                          for resp in responses[r"пока|до свидания|выход"]])
                print('Бот:', response)
                log_conversation(user_input, response)
                break

            response = chatbot_response(user_input)
            print('Бот:', response)
            log_conversation(user_input, response)

        except KeyboardInterrupt:
            print("\nБот: До свидания!")
            break
        except Exception as e:
            print("Бот: Произошла ошибка. Попробуйте еще раз.")
            log_conversation(user_input, f"Ошибка: {str(e)}")