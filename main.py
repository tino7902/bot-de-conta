from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

with open("token.txt", "r") as f:
    token = f.readlines()

TOKEN = token[0]

NUM1, OPERATION = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Hola! Envíame el precio con IVA incluido:")
    return NUM1


async def get_num2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        context.user_data["num1"] = int(update.message.text)
    except:
        await update.message.reply_text(
            "No te entendí. Por favor asegurate el que el numero que me mandaste no tenga otras letras o puntos"
        )
        context.user_data["num1"] = int(update.message.text)
    await update.message.reply_text(
        "¿Esta cuenta tiene IVA del 5% o 10%?\n(1)- 10% de IVA\n(2)- 5% de IVA"
    )
    return OPERATION


async def get_operation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    num1 = context.user_data["num1"]
    operation = update.message.text.strip()

    if operation == "1":
        gravado = round(num1 / 1.1)
        iva = round(num1 / 11)
    elif operation == "2":
        gravado = round(num1 / 1.05)
        iva = round(num1 / 21)
    else:
        await update.message.reply_text("Operación no válida. Usa 1 o 2")
        return OPERATION

    await update.message.reply_text(f"El precio gravado es: {gravado}\nEl IVA es {iva}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NUM1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_num2)],
            OPERATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_operation)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
