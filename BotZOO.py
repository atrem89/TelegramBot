import telebot
from telebot import types
from collections import defaultdict
from questions import questions
from zoo import TOKEN

bot = telebot.TeleBot(TOKEN)

# Следим за выборами пользователя
user_choices = defaultdict(lambda: defaultdict(int))
user_current_question = defaultdict(int)

@bot.message_handler(commands=['start', 'restart'])
def send_welcome(message):
    greeting = (" Привет! \n"
                "Хочешь узнать свое тотемное животное, своего 'ДЕЙМОНА'🐾‍?\n"
                "Нажми кнопку ниже 'Начать тест'")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Начать тест')  # Кнопка для начала теста
    bot.send_message(message.chat.id, greeting, reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == 'Начать тест':
        start_quiz(message)
    elif message.text == 'Начать тест заново':
        start_quiz(message)
    else:
        process_answer(message)

def contact_zoo_staff(call):
    user_id = call.from_user.id
    user_username = call.from_user.username if call.from_user.username else "анонимный пользователь"
    # Логируем попытку отправки для отладки
    print(f"Попытка отправить сообщение от {user_id} (@{user_username}) сотруднику.")
    try:
        # Попытка отправить сообщение сотруднику
        bot.send_message(1885951903, f"Запрос на связь от @{user_username} (ID: {user_id})")
        # Ответ пользователю
        bot.send_message(user_id, "Ваш запрос отправлен сотруднику. Ожидайте ответа.")
        print(f"Сообщение отправлено успешно.")
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")

def start_quiz(message):
    user_choices[message.chat.id].clear()
    user_current_question[message.chat.id] = 0
    ask_question(message)

def ask_question(message):
    question_idx = user_current_question[message.chat.id]
    if question_idx < len(questions):
        question, answers = questions[question_idx]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in answers.keys():
            markup.add(option)
        markup.add('Начать тест заново')  # Добавляем возможность начать заново
        bot.send_message(message.chat.id, question, reply_markup=markup)
    else:
        show_result(message)

def process_answer(message):
    question_idx = user_current_question[message.chat.id]
    if question_idx < len(questions):
        answers = questions[question_idx][1]
        user_choice = answers.get(message.text)
        if user_choice:
            user_choices[message.chat.id][user_choice] += 1
            user_current_question[message.chat.id] += 1
            ask_question(message)
        else:
            bot.send_message(message.chat.id, "Пожалуйста, выберите один из предложенных вариантов ответа.")
            ask_question(message)

def calculate_result(user_id):
    choices_count = user_choices[user_id]
    counts = {'А': 0, 'Б': 0, 'В': 0, 'Г': 0}
    for category in choices_count:
        counts[category] += choices_count[category]

    max_count = max(counts.values())
    max_categories = [cat for cat, count in counts.items() if count == max_count]

    totem_info = {
        'А': ("Волк - символизирует свободу и интуицию. Волки известны своей социальной организованностью, живут и охотятся в стаях, что говорит о их глубоких социальных связях. Они обладают выдающимися интуитивными способностями, помогающими им выживать в дикой природе. Волк также является символом свободы духа, смелости и независимости, он не боится идти своим путем.", "https://media.istockphoto.com/id/177794699/ru/%D1%84%D0%BE%D1%82%D0%BE/%D1%81%D0%B5%D1%80%D1%8B%D0%B9-%D0%B2%D0%BE%D0%BB%D0%BA-%D0%BF%D0%BE%D1%80%D1%82%D1%80%D0%B5%D1%82.jpg?s=612x612&w=0&k=20&c=zTMmfuCxFPLGdvQkmS3Xb6MVY7E-wk5nf3lnuVbTc4Q="),
        'Б': ("Медведь🐻 - олицетворяет силу и уверенность. Медведь — мощное и внушающее уважение животное, которое символизирует лидерство и силу. Он также ассоциируется с защитой, внутренней уверенностью и самодостаточностью. Медведи способны к глубокому размышлению и медитации, особенно во время зимней спячки, что отражает их связь с более глубокими уровнями сознания и интуицией.", "https://img.freepik.com/free-photo/majestic-large-mammal-walking-in-snowy-forest-generative-ai_188544-36924.jpg"),
        'В': ("Лошадь🐴 - символ свободы и мощи. Лошади — существа, излучающие элегантность и мощь, способные быстро двигаться и преодолевать препятствия. Они также ассоциируются со свободой, поскольку их грациозное движение и сила духа вдохновляют на освобождение от ограничений и следование своим желаниям.", "https://basetop.ru/wp-content/uploads/2019/03/itrttzwr.jpg"),
        'Г': ("Сова🦉 - мудрость и загадочность. Совы, с их способностью видеть в темноте, символизируют глубокую интуицию и знание тайного. Эти птицы часто ассоциируются с мудростью, поскольку их предполагаемая способность видеть то, что скрыто от других, делает их символом знания и загадочности.", "https://img.freepik.com/premium-photo/beautiful-owl_254845-8286.jpg"),
        ('А', 'Б'): ("Олень🦌 - изящество и спокойствие. Олени — элегантные животные, движения которых наполнены грацией и спокойствием. Они напоминают о важности быть легким на подъем и способным адаптироваться к изменениям, сохраняя при этом внутреннее спокойствие и достоинство.", "https://media.istockphoto.com/id/140157656/ru/%D1%84%D0%BE%D1%82%D0%BE/%D0%BF%D0%BE%D1%80%D1%82%D1%80%D0%B5%D1%82-%D0%B2%D0%B5%D0%BB%D0%B8%D1%87%D0%B5%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9-%D0%BA%D1%80%D0%B0%D1%81%D0%BD%D1%8B%D0%B9-%D0%BE%D0%BB%D0%B5%D0%BD%D1%8C-%D0%BE%D0%BB%D0%B5%D0%BD%D1%8C-%D0%B2-%D0%BE%D1%81%D0%B5%D0%BD%D1%8C-%D0%BE%D1%81%D0%B5%D0%BD%D1%8C.jpg?s=612x612&w=0&k=20&c=rCL1dxZz0DdUgcxYEH5a9VZzSpRV15Wx4RY9A_91ovE="),
        ('А', 'В'): ("Дельфин🐬 - игривость и гармония. Дельфины известны своей дружелюбностью, интеллектом и любопытством. Они напоминают о важности поддерживать легкость бытия, наслаждаться общением и находить радость в простых вещах, поддерживая при этом гармонию с окружающим миром.", "https://img.freepik.com/free-photo/beautiful-dolphin-jumping-out-of-water_23-2150770795.jpg"),
        ('А', 'Г'): ("Пума🐈 - решительность и независимость. Пумы — сильные и независимые хищники, которые руководствуются своей интуицией и имеют сильный дух. Они олицетворяют смелость идти своим", "https://media.istockphoto.com/id/1392544996/ru/%D1%84%D0%BE%D1%82%D0%BE/%D0%BF%D1%83%D0%BC%D0%B0-%D0%BF%D0%BE%D1%80%D1%82%D1%80%D0%B5%D1%82-%D0%BA%D1%80%D1%83%D0%BF%D0%BD%D1%8B%D0%BC-%D0%BF%D0%BB%D0%B0%D0%BD%D0%BE%D0%BC.jpg?s=612x612&w=0&k=20&c=6O2DD9DtRtRcjrlrZjXdONhEZK67Bn_rhjFG8YKAfP4="),
        ('Б', 'В'): ("Орёл🦅 - символизирует остроту зрения и свободу духа. Орлы обладают уникальной способностью видеть цели на большом расстоянии, не теряя при этом связи с землёй. Это животные, которые сочетают в себе как мощь, так и красоту, способные приспосабливаться к изменениям и преодолевать препятствия.", "https://static6.depositphotos.com/1000847/647/i/450/depositphotos_6474531-stock-photo-eagle-close-up.jpg"),
        ('Б', 'Г'): ("Лиса🦊 - метафора хитрости и адаптивности. Лисы известны своей способностью выживать в различных условиях, используя острый ум и изобретательность. Они символизируют способность находить нестандартные решения и легко адаптироваться к новым обстоятельствам, сохраняя при этом уверенность и силу.", "https://media.istockphoto.com/id/516318760/ru/%D1%84%D0%BE%D1%82%D0%BE/red-fox-vulpes-vulpes.jpg?s=612x612&w=0&k=20&c=6ZbE9z2TK2Jf7ZuRzwZmm1p89jJebHCBe112cisRuj4="),
        ('В', 'Г'): ("Черепаха🐢 - представляет мудрость, долголетие и стойкость. Черепахи живут долго, двигаются медленно, но всегда достигают своей цели благодаря непоколебимой уверенности в себе и своих силах. Они напоминают о важности терпения, устойчивости перед лицом трудностей и способности сохранять спокойствие в любой ситуации.", "https://st.depositphotos.com/2021333/2715/i/450/depositphotos_27155705-stock-photo-green-sea-turtle.jpg"),
    }

    if len(max_categories) == 1:
        return totem_info[max_categories[0]]
    else:
        # Убедитесь, что вы добавили все необходимые URL в totem_info
        return totem_info[tuple(sorted(max_categories))]


def show_result(message):
    try:
        result_text, photo_url = calculate_result(message.chat.id)

        # Формируем текст сообщения с результатом и призывом к действию
        caption_text = (f"Ваше тотемное животное🐾:\n{result_text}\n\n"
                        "А какое животное как ты? Хочешь узнать?\n\nПрими участие в викторине https://t.me/zoo_mskbot ⬇️")

        # Создаем InlineKeyboardMarkup для добавления кнопки прямо под сообщением
        markup_inline = types.InlineKeyboardMarkup()
        start_button = types.InlineKeyboardButton(text="Присоединяйся к викторине",
                                                  url="https://t.me/zoo_mskbot")
        markup_inline.add(start_button)

        # Отправляем фотографию с результатом, подписью и кнопкой
        bot.send_photo(message.chat.id, photo_url, caption=caption_text, reply_markup=markup_inline, parse_mode='HTML')

        # Первое сообщение о программе опеки
        program_text = ("Спасибо за уделенное время!\n\n"
                        "Предлагаем Вам принять участие в программе «Возьми животное под опеку».\n\n"
                        "Это возможность ощутить свою причастность к сохранению природы, участвовать в жизни Московского зоопарка и его обитателей, "
                        "видеть конкретные результаты своей деятельности. Опекать – значит помогать любимым животным.")
        markup_inline_zoo = types.InlineKeyboardMarkup()
        zoo_url = "https://moscowzoo.ru/my-zoo/become-a-guardian/"
        more_button = types.InlineKeyboardButton(text="Узнать подробнее", url=zoo_url)
        markup_inline_zoo.add(more_button)
        bot.send_message(message.chat.id, program_text, reply_markup=markup_inline_zoo, parse_mode="Markdown")

        # Создаем ReplyKeyboardMarkup для добавления кнопок непосредственно в клавиатуру чата
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        restart_button = types.KeyboardButton('Пройти тест заново')
        contact_button = types.KeyboardButton('Связаться с сотрудником зоопарка')
        markup_reply.add(restart_button, contact_button)

        bot.send_message(message.chat.id, "При желании вы можете пройти тест заново, задать вопросы сотруднику зоопарка или оставить отзыв:", reply_markup=markup_reply)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")

# Новый обработчик callback_query для обработки нажатий на inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "restart_quiz":
        start_quiz(call.message)
    elif call.data == "contact_zoo":
        contact_zoo_staff(call.message)
    bot.answer_callback_query(call.id)

# Пример использования
if __name__ == '__main__':
    bot.infinity_polling()
