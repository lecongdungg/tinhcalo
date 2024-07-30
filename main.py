import telebot
import time
from keep_alive import keep_alive  # Import hàm keep_alive

API_TOKEN = '7447113607:AAEVI-fjaryupVFAotYvgsoPXBn1XvSO8W8'
bot = telebot.TeleBot(API_TOKEN)

keep_alive()  # Khởi động server Flask để giữ cho bot hoạt động liên tục


# Step 1: Ask for gender
@bot.message_handler(commands=['start'])
def ask_gender(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Nam', 'Nữ')
    msg = bot.reply_to(message,
                       "Chào mừng bạn! Vui lòng chọn giới tính của bạn:",
                       reply_markup=markup)
    bot.register_next_step_handler(msg, process_gender_step)


def process_gender_step(message):
    chat_id = message.chat.id
    gender = message.text
    if gender not in ['Nam', 'Nữ']:
        msg = bot.reply_to(message, 'Vui lòng chọn giới tính hợp lệ (Nam/Nữ).')
        bot.register_next_step_handler(msg, process_gender_step)
    else:
        bot.send_message(chat_id, f"Bạn đã chọn {gender}.")
        msg = bot.send_message(chat_id, "Vui lòng nhập cân nặng của bạn (kg):")
        bot.register_next_step_handler(msg, process_weight_step, gender)


def process_weight_step(message, gender):
    chat_id = message.chat.id
    try:
        weight = float(message.text)
        msg = bot.send_message(chat_id,
                               "Vui lòng nhập chiều cao của bạn (cm):")
        bot.register_next_step_handler(msg, process_height_step, gender,
                                       weight)
    except ValueError:
        msg = bot.reply_to(message,
                           'Vui lòng nhập cân nặng hợp lệ (số dương).')
        bot.register_next_step_handler(msg, process_weight_step, gender)


def process_height_step(message, gender, weight):
    chat_id = message.chat.id
    try:
        height = float(message.text)
        msg = bot.send_message(chat_id, "Vui lòng nhập tuổi của bạn:")
        bot.register_next_step_handler(msg, process_age_step, gender, weight,
                                       height)
    except ValueError:
        msg = bot.reply_to(message,
                           'Vui lòng nhập chiều cao hợp lệ (số dương).')
        bot.register_next_step_handler(msg, process_height_step, gender,
                                       weight)


def process_age_step(message, gender, weight, height):
    chat_id = message.chat.id
    try:
        age = int(message.text)
        bmr = calculate_bmr(gender, weight, height, age)
        bot.send_message(
            chat_id,
            f"Tỷ lệ trao đổi chất cơ bản BMR của bạn là {bmr:.2f} calo.")
        ask_activity_level(message, bmr)
    except ValueError:
        msg = bot.reply_to(message,
                           'Vui lòng nhập tuổi hợp lệ (số nguyên dương).')
        bot.register_next_step_handler(msg, process_age_step, gender, weight,
                                       height)


def calculate_bmr(gender, weight, height, age):
    if gender == 'Nam':
        return (13.397 * weight) + (4.799 * height) - (5.677 * age) + 88.362
    else:
        return (9.247 * weight) + (3.098 * height) - (4.330 * age) + 447.593


def ask_activity_level(message, bmr):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Ít vận động', 'Vận động nhẹ', 'Vận động vừa', 'Vận động nặng',
               'Vận động rất nặng')
    msg = bot.reply_to(message,
                       "Vui lòng chọn mức độ vận động của bạn:",
                       reply_markup=markup)
    bot.register_next_step_handler(msg, process_activity_level_step, bmr)


def process_activity_level_step(message, bmr):
    chat_id = message.chat.id
    activity_level = message.text
    activity_factors = {
        'Ít vận động': 1.2,
        'Vận động nhẹ': 1.375,
        'Vận động vừa': 1.55,
        'Vận động nặng': 1.725,
        'Vận động rất nặng': 1.9
    }
    if activity_level not in activity_factors:
        msg = bot.reply_to(message, 'Vui lòng chọn mức độ vận động hợp lệ.')
        bot.register_next_step_handler(msg, process_activity_level_step, bmr)
    else:
        r = activity_factors[activity_level]
        tdee = bmr * r
        bot.send_message(
            chat_id,
            f"Tổng calo mà bạn cần nạp mỗi ngày là: TDEE = {tdee:.2f} calo.")


# Add exception handling for the polling process
while True:
    try:
        bot.polling(timeout=60)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(15)  # Wait 15 seconds before retrying
