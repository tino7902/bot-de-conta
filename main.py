from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)


def get_token():
    with open("token.txt", "r") as f:
        token = f.readline()
    return token


TOKEN = get_token()

NUM1, OPERATION, IVA_TYPE, NEXT_ACCOUNT = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["accounts"] = []  # Inicializa una lista para guardar las cuentas
    await update.message.reply_text(
        "Hola! Vamos a calcular la diferencia de IVA.  Envíame el precio con IVA incluido de la primera cuenta:"
    )
    return NUM1


async def get_num(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        num1 = int(update.message.text)
        context.user_data["current_account"] = {
            "price": num1
        }  # Guarda el precio en la cuenta actual
    except ValueError:
        await update.message.reply_text(
            "No te entendí.  Asegúrate de que el número que me mandaste no tenga otras letras o puntos"
        )
        return NUM1  # Volvemos a pedir el número
    await update.message.reply_text(
        "¿Esta cuenta tiene IVA CF o IVA DF?\n(1)- IVA CF\n(2)- IVA DF"
    )
    return IVA_TYPE


async def get_iva_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    iva_type = update.message.text.strip()

    if iva_type not in ("1", "2"):
        await update.message.reply_text("Opción no válida. Usa 1 o 2.")
        return IVA_TYPE

    context.user_data["current_account"]["iva_type"] = (
        "CF" if iva_type == "1" else "DF"
    )  # Guarda el tipo de IVA en la cuenta actual

    await update.message.reply_text(
        "¿Esta cuenta tiene IVA del 5% o 10%?\n(1)- 10% de IVA\n(2)- 5% de IVA"
    )
    return OPERATION


async def get_operation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    operation = update.message.text.strip()
    current_account = context.user_data["current_account"]
    num1 = current_account["price"]

    match operation:
        case "1":
            gravado = round(num1 / 1.1)
            iva = round(num1 / 11)
        case "2":
            gravado = round(num1 / 1.05)
            iva = round(num1 / 21)
        case _:
            await update.message.reply_text("Operación no válida. Usa 1 o 2")
            return OPERATION

    current_account["gravado"] = gravado
    current_account["iva"] = iva
    context.user_data["accounts"].append(
        current_account
    )  # Agrega la cuenta a la lista de cuentas

    await update.message.reply_text(f"El precio gravado es: {gravado}\nEl IVA es {iva}")
    await update.message.reply_text("¿Deseas ingresar otra cuenta?\n(1)- Sí\n(2)- No")
    return NEXT_ACCOUNT


async def next_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip()

    if answer == "1":
        await update.message.reply_text(
            "Envíame el precio con IVA incluido de la siguiente cuenta:"
        )
        return NUM1  # Volvemos al inicio para ingresar otra cuenta
    elif answer == "2":
        # Calcular la diferencia de IVA aquí
        accounts = context.user_data["accounts"]
        iva_cf = sum(
            account["iva"] for account in accounts if account["iva_type"] == "CF"
        )
        iva_df = sum(
            account["iva"] for account in accounts if account["iva_type"] == "DF"
        )
        difference = iva_cf - iva_df

        if difference < 0:
            response = f"Total IVA CF: {iva_cf}\nTotal IVA DF: {iva_df}\nDiferencia IVA CF - IVA DF: {difference}\n\nDebes {difference * -1} guaraníes en impuestos"
        else:
            response = f"Total IVA CF: {iva_cf}\nTotal IVA DF: {iva_df}\nDiferencia IVA CF - IVA DF: {difference}\n\nTenes {difference} guaraníes a favor"

        await update.message.reply_text(response)
        return ConversationHandler.END  # Fin de la conversación
    else:
        await update.message.reply_text("Opción no válida. Usa 1 o 2.")
        return NEXT_ACCOUNT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NUM1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_num)],
            IVA_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_iva_type)],
            OPERATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_operation)],
            NEXT_ACCOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, next_account)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
