import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот, который может показывать города на карте 🌍\n"
        "Напиши /help для списка команд."
    )


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "/show_city <city> — показать город на карте\n"
        "/remember_city <city> — сохранить город\n"
        "/show_my_cities — показать все сохранённые города"
    )


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Используй: /show_city London")
        return

    city_name = parts[1]
    coords = manager.get_coordinates(city_name)

    if not coords:
        bot.send_message(message.chat.id, "Такого города я не знаю 😢")
        return

    path = f"map_{message.chat.id}.png"

    color = manager.get_marker_color(message.chat.id)
    manager.create_graph(path, [city_name], marker_color=color)

    with open(path, 'rb') as img:
        bot.send_photo(message.chat.id, img)


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    user_id = message.chat.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Используй: /remember_city Paris")
        return

    city_name = parts[1]
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранён ✅')
    else:
        bot.send_message(
            message.chat.id,
            'Такого города я не знаю. Убедись, что он написан на английском!'
        )


@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)

    if not cities:
        bot.send_message(message.chat.id, "У тебя пока нет сохранённых городов 🗺")
        return

    path = f"map_all_{message.chat.id}.png"
    manager.create_graph(path, cities)

    with open(path, 'rb') as img:
        bot.send_photo(message.chat.id, img)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "/show_city <city> — показать город\n"
        "/remember_city <city> — сохранить город\n"
        "/show_my_cities — показать все города\n"
        "/set_color <color> — цвет маркеров (red, blue, green, yellow, purple\n"
        "/show_country <country> — города страны\n"
        "/show_population <min> [max] — города по населению\n"
        "/show_country_population <country> <min> [max] — страна + население" \
    )


@bot.message_handler(commands=['set_color'])
def handle_set_color(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Пример: /set_color blue")
        return

    color = parts[1].lower()
    allowed = ['red', 'blue', 'green', 'yellow', 'purple', 'black']

    if color not in allowed:
        bot.send_message(
            message.chat.id,
            f"Недопустимый цвет ❌\nДоступно: {', '.join(allowed)}"
        )
        return

    manager.set_marker_color(message.chat.id, color)
    bot.send_message(
        message.chat.id,
        f"Цвет маркеров установлен: {color} 🎨"
    )

@bot.message_handler(commands=['show_country'])
def handle_show_country(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Пример: /show_country Germany")
        return

    country = parts[1]
    cities = manager.get_cities_by_country(country)

    if not cities:
        bot.send_message(message.chat.id, "Города не найдены 😢")
        return

    path = f"country_{message.chat.id}.png"
    color = manager.get_marker_color(message.chat.id)
    manager.create_graph(path, cities, marker_color=color)

    with open(path, 'rb') as img:
        bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['show_population'])
def handle_show_population(message):
    parts = message.text.split()

    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "Пример:\n/show_population 1000000\n/show_population 500000 2000000"
        )
        return

    min_pop = int(parts[1])
    max_pop = int(parts[2]) if len(parts) > 2 else None

    cities = manager.get_cities_by_population(min_pop, max_pop)

    if not cities:
        bot.send_message(message.chat.id, "Города не найдены 😢")
        return

    path = f"population_{message.chat.id}.png"
    color = manager.get_marker_color(message.chat.id)
    manager.create_graph(path, cities, marker_color=color)

    with open(path, 'rb') as img:
        bot.send_photo(message.chat.id, img)

@bot.message_handler(commands=['show_country_population'])
def handle_show_country_population(message):
    parts = message.text.split()

    if len(parts) < 3:
        bot.send_message(
            message.chat.id,
            "Пример:\n/show_country_population Japan 1000000\n"
            "/show_country_population USA 500000 3000000"
        )
        return

    country = parts[1]
    min_pop = int(parts[2])
    max_pop = int(parts[3]) if len(parts) > 3 else None

    cities = manager.get_cities_by_country_and_population(
        country, min_pop, max_pop
    )

    if not cities:
        bot.send_message(message.chat.id, "Города не найдены 😢")
        return

    path = f"country_population_{message.chat.id}.png"
    color = manager.get_marker_color(message.chat.id)
    manager.create_graph(path, cities, marker_color=color)

    with open(path, 'rb') as img:
        bot.send_photo(message.chat.id, img)

if __name__ == "__main__":
    manager = DB_Map(DATABASE)
    manager.create_user_table()
    bot.polling()
