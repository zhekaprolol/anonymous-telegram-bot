from keep_alive import keep_alive
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, ConversationHandler, ContextTypes)
import threading
import re

TOKEN = "7698674555:AAGuTIwQXn7NhfS5ZAGG7HQsD5gOkXB94eM"
ADMIN_ID = 802324311

ASK, REPORT, MESSAGE = range(3)
messages_storage = {}
message_counter = 0


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""<b>Гражданин,</b>

Вы подключены к <b>Анонимному Каналу Связи</b>.
Данный канал предназначен для передачи вопросов, замечаний и иной информации, <i>не подлежащей</i> открытой огласке.

<b>Вы вправе:</b>
<code>— Задать вопрос;
— Сообщить о нарушении порядка;
— Передать обращение к Управлению "Поставщика Решимости".</code>

<b>Предупреждение:</b>
<blockquote expandable>Все сообщения регистрируются.

Личность не устанавливается, если только вы сами не сделаете это возможным.

Злоупотребление каналом, намеренное искажение фактов, распространение панических слухов или проявление неуважения к органам власти рассматриваются как подрыв дисциплины и караются в соответствии с внутренним Уставом Состава.</blockquote>

/help - Инструкция по использованию.

<b>Слава Вождю!</b>
— Министерство связи.""",
                                    parse_mode="HTML")


async def start_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Задайте свой вопрос. Мы сохраним анонимность.")
    return ASK


async def received_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_counter
    user_text = update.message.text
    message_counter += 1
    messages_storage[message_counter] = (update.effective_user.id, user_text)
    await update.message.reply_text("Ваш вопрос передан, ожидайте ответа.")
    await context.bot.send_message(
        ADMIN_ID,
        f"<b>Вопрос #{message_counter}</b>:\n{user_text}",
        parse_mode="HTML")
    return ConversationHandler.END


async def start_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Опишите нарушение и юзернейм того кто нарушил.")
    return REPORT


async def received_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_counter
    user_text = update.message.text
    message_counter += 1
    messages_storage[message_counter] = (update.effective_user.id, user_text)
    await update.message.reply_text(
        "Ваш рапорт передан. Можете быть спокойны, мы разберемся.")
    await context.bot.send_message(
        ADMIN_ID,
        f"<b>Рапорт #{message_counter}</b>:\n{user_text}",
        parse_mode="HTML")
    return ConversationHandler.END


async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Передайте обращение или замечание нам.")
    return MESSAGE


async def received_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global message_counter
    user_text = update.message.text
    message_counter += 1
    messages_storage[message_counter] = (update.effective_user.id, user_text)
    await update.message.reply_text("Ваше сообщение передано.")
    await context.bot.send_message(
        ADMIN_ID,
        f"<b>Обращение #{message_counter}</b>:\n{user_text}",
        parse_mode="HTML")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отмена.")
    return ConversationHandler.END


async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Использование: /reply <номер_сообщения> <текст_ответа>")
        return

    try:
        msg_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Номер сообщения должен быть числом.")
        return

    answer_text = " ".join(context.args[1:])
    if msg_id not in messages_storage:
        await update.message.reply_text("Сообщение с таким номером не найдено."
                                        )
        return

    user_id, _ = messages_storage[msg_id]
    await context.bot.send_message(user_id, f"Ответ:\n{answer_text}")
    await update.message.reply_text(
        f"Ответ отправлен пользователю (сообщение #{msg_id}).")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Инструкция:\n"
                                    "/ask — Задать вопрос анонимно\n"
                                    "/report — Сообщить о нарушении\n"
                                    "/message — Передать обращение\n"
                                    "/rules — Ознакомиться с Уставом\n"
                                    "/praise — Слава Вождю!")


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Устав Состава:
1. Обязанности гражданина
— При обнаружении подозрительных действий, нарушений или высказываний незамедлительно сообщать об этом через Анонимный Канал Связи.
— Проявлять уважение к Вождю, Представителям власти и служащим.

2. Что запрещено
— Распространение слухов, подрывающих доверие к Управлению или Вождю.
— Ложные сообщения и злоупотребление Анонимным Каналом Связи.
— Пропаганда, агитация, хранение или обсуждение запрещённых материалов.

3. Ответственность
Каждое нарушение регистрируется.
В зависимости от степени тяжести, нарушителю может быть вынесено предупреждение, ограничение в передвижении, временное отключение от систем снабжения, понижение статуса или коррекционная мера.
Повторные или злонамеренные действия рассматриваются как попытка дестабилизации порядка.

4. Терпение и ожидание
За работой Анонимного Канала Связи следят реальные люди, и не всегда они могут ответить немедленно. Терпение и понимание — обязательны.
Любое проявление нетерпимости или агрессии в адрес служащих считается нарушением дисциплины.
""")


async def praise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Слава Вождю!")


async def handle_admin_reply(update: Update,
                             context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        original_text = update.message.reply_to_message.text
        match = re.search(r"#(\d+)", original_text)
        if match:
            msg_id = int(match.group(1))
            if msg_id in messages_storage:
                user_id, _ = messages_storage[msg_id]
                await context.bot.send_message(
                    user_id, f"Ответ:\n{update.message.text}")
                await update.message.reply_text(
                    f"Ответ на сообщение #{msg_id} отправлен.")
            else:
                await update.message.reply_text("Сообщение не найдено.")


def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    ask_conv = ConversationHandler(
        entry_points=[CommandHandler("ask", start_ask)],
        states={
            ASK:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, received_ask)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    report_conv = ConversationHandler(
        entry_points=[CommandHandler("report", start_report)],
        states={
            REPORT:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, received_report)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    message_conv = ConversationHandler(
        entry_points=[CommandHandler("message", start_message)],
        states={
            MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               received_message)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(ask_conv)
    app.add_handler(report_conv)
    app.add_handler(message_conv)
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("praise", praise))
    app.add_handler(
        MessageHandler(filters.REPLY & filters.TEXT, handle_admin_reply))

    print("Анонимный Канал Связи запущен.")
    app.run_polling()


if __name__ == "__main__":
    import threading
    threading.Thread(target=keep_alive).start()
    run_bot()
