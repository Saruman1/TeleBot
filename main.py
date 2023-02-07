import requests
from bs4 import BeautifulSoup
import telebot
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'georgekeron39@gmail.com'
app.config['MAIL_PASSWORD'] = 'sejctchsxkdefkni'

mail = Mail(app)

bot = telebot.TeleBot('5966308697:AAGjZvVTN1yQtkqbSavK-Erhk4FlPx8Gfr8')
emails = []

@bot.message_handler(commands=['start'])
def start(message):
        bot.send_message(message.chat.id, 'Привіт! Я бот, який буде перевіряти інформацію про новини на сайті tsn.ua та коротко її суммувати. Щоб отримувати інформацію, введіть /subscribe')

@bot.message_handler(commands=['subscribe'])
def handle_subscribe(message):
    def ask_for_email(message):
        bot.send_message(message.chat.id, 'Будь ласка, введіть свою електронну адресу:')
        bot.register_next_step_handler(message, process_email)

    def process_email(message):
        email = message.text
        if '@' in email:
            bot.send_message(message.chat.id, f'Ви успішно підписалися на розсилку новин на адресу {email}\nЩоб отримати новини введіть команду /send_news')
            emails.append(email)
        else:
            bot.send_message(message.chat.id, 'Некоректна адреса')

    ask_for_email(message)

def get_page():
    page = requests.get('https://tsn.ua/')
    return page

def get_news():
    page = get_page()
    soup = BeautifulSoup(page.content, 'html.parser')
    news = soup.find_all(class_='c-card c-card--log c-card--title-sm')
    summary = []
    for new in news:
        description = new.find(class_='c-card__link').text
        summary.append(f'{description}\n\n')
        summary_str = ''.join([str(elem) for elem in summary])
    return summary_str

def send_email(to, body):
    with app.app_context():
        msg = Message('Суммування новин з tsn.ua', recipients=[to])
        msg.body = body
        msg.sender = 'georgekeron39@gmail.com'
        mail.send(msg)

def send_news():
    # отримуємо суммування новин
    news = get_news()
    # перевіряємо чи є електронні адреси для розсилки
    if emails:
        # проходимося по усім електронним адресам
        for email in emails:
            # відправляємо суммування новин на електронну пошту
            send_email(email, news)
    else:
        print('Немає електронних адрес для розсилки.')

@bot.message_handler(commands=['send_news'])
def handle_send_news(message):
    news = get_news()
    # надсилаємо новини кожному адресату
    for email in emails:
        send_email(email, news)
    bot.send_message(message.chat.id, 'Новини успішно відправлені!')


bot.polling()




