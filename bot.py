import json
from collections import defaultdict
from difflib import get_close_matches

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "7627793255:AAGagcyyYeHsNJNuWywX87mbB3yWwfbgetQ"

# Historial opcional
history = defaultdict(list)

#-------------Carga De Datos---------------------------------------------------

async def load_data_into_bot_data(application):
    """Carga datos desde 'datos.json' y los guarda en application.bot_data["info"]."""
    with open("datos.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    application.bot_data["info"] = data

# ----------------------------------------------------------------------------
# /start: Muestra el Menú principal
# ----------------------------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history[user_id].append(("user", "/start"))

    text = (
        "¡Hola! Bienvenido al Bot de CES-TEC.\n"
        "Selecciona una sección:"
    )
    

    # Menú principal con InlineKeyboard
    keyboard = [
        [InlineKeyboardButton("📄Inclusiones", callback_data="INCLUSIONES")],
        [InlineKeyboardButton("🚗 Movilidad Estudiantil", callback_data="MOVILIDAD")],
        [InlineKeyboardButton("🧾 Requisitos de Cursos", callback_data="REQUISITOS")],
        [InlineKeyboardButton("🕒 Horario Administrativos", callback_data="HORARIOS")],
        [InlineKeyboardButton("🧑‍💻 Contacto (Admins)", callback_data="CONTACTO")],
        [InlineKeyboardButton("📍 Ubicaciones CES", callback_data="UBICACIONES")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    # Guardamos en historial
    history[user_id].append(("bot", text))
    #await update.message.reply_text(text, reply_markup=markup)
    # Verificación: si es comando (/start) o botón
    if update.message:
        await update.message.reply_text(text, reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=markup)
# ----------------------------------------------------------------------------
# Maneja los botones del menú principal
# ----------------------------------------------------------------------------
async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = context.bot_data.get("info", {})  # Contiene la info del JSON

    choice = query.data
    response_text = ""
    reply_markup = None

    # ------------------------------------------------------------------------
    # INCLUSIONES -> submenú
    # ------------------------------------------------------------------------
    if choice == "INCLUSIONES":
        keyboard = [
            [InlineKeyboardButton("🗓️ Fechas importantes", callback_data="INC_FECHAS")],
            [InlineKeyboardButton("📝 Formularios", callback_data="INC_FORMULARIOS")],
            [InlineKeyboardButton("📅 Periodos de cierre", callback_data="INC_PERIODOS")],
            [InlineKeyboardButton("📊 Resultados académicos", callback_data="INC_RESULTADOS")],
            [InlineKeyboardButton("🔙 Volver al menú principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        response_text = "Selecciona una opción de Inclusiones:"

    elif choice.startswith("INC_"):
        inclusiones = data.get("inclusiones", {})
        if choice == "INC_FECHAS":
            response_text = inclusiones.get("fechas", "No hay info de fechas.")
        elif choice == "INC_FORMULARIOS":
            response_text = inclusiones.get("formularios", "No hay info de formularios.")
        elif choice == "INC_PERIODOS":
            response_text = inclusiones.get("periodos", "No hay info de periodos de cierre.")
        elif choice == "INC_RESULTADOS":
            response_text = inclusiones.get("resultados", "No hay info de resultados.")
        elif query.data == "CERRAR_MENU":
            await query.edit_message_text("Menú cerrado. ¡Gracias por usar el bot!")
        # Submenú para volver
        keyboard = [
            [InlineKeyboardButton("🔙 Volver a Inclusiones", callback_data="INCLUSIONES")],
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # ------------------------------------------------------------------------
    # MOVILIDAD
    # ------------------------------------------------------------------------
    elif choice == "MOVILIDAD":
        keyboard = [
            [InlineKeyboardButton("🧠 Info Programas", callback_data="MOV_INFO")],
            [InlineKeyboardButton("🧾 Requisitos Movilidad", callback_data="MOV_REQ")],
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        response_text = "Movilidad Estudiantil: elige una opción."

    elif choice == "MOV_INFO":
        mov = data.get("movilidad", {})
        response_text = mov.get("info", "No hay info sobre programas.")
        keyboard = [
            [InlineKeyboardButton("🔙 Volver a Movilidad", callback_data="MOVILIDAD")],
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    elif choice == "MOV_REQ":
        mov = data.get("movilidad", {})
        response_text = mov.get("requisitos", "No hay info de requisitos de movilidad.")
        keyboard = [
            [InlineKeyboardButton("🔙 Volver a Movilidad", callback_data="MOVILIDAD")],
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # ------------------------------------------------------------------------
    # REQUISITOS DE CURSOS: PREGUNTAR CÓDIGO/NOMBRE
    # ------------------------------------------------------------------------
    elif choice == "REQUISITOS":
        response_text = (
            "Ingresa *el código o el nombre* del curso (por ejemplo, CE1101 o "
            "INTRODUCCIÓN A LA PROGRAMACIÓN) para ver sus requisitos.\n\n"
            "Si deseas cancelar, escribe /cancelar."
        )
        context.user_data["modo"] = "consulta_curso"
        keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    # ------------------------------------------------------------------------
    # HORARIO DE ADMINISTRATIVOS
    # ------------------------------------------------------------------------
    elif choice == "HORARIOS":
        horarios = data.get("horarios_admin", "No hay horarios.")
        response_text = horarios
        keyboard = [
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
   # ------------------------------------------------------------------------
    # CONTACTO
    # ------------------------------------------------------------------------
    elif choice == "CONTACTO":
        response_text = "Selecciona un grupo de contactos:"
        keyboard = [
            [InlineKeyboardButton("👨‍🏫 Profesores", callback_data="CONTACTO_PROFESORES")],
            [InlineKeyboardButton("🎓 Asociación Estudiantil", callback_data="CONTACTO_ASOCIACION")],
            [InlineKeyboardButton("🧑‍💼 Administración CES", callback_data="CONTACTO_ADMIN")],
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    elif choice == "CONTACTO_ADMIN":
        contacto = data.get("contacto", {})
        director = contacto.get("director", {})
        asistente = contacto.get("asistente", {})

        text_director = (
            f"👨‍🏫 *Director:*\n"
            f"{director.get('nombre', 'N/A')}\n"
            f"📞 {director.get('telefono', 'N/A')}\n"
            f"📧 {director.get('correo', 'N/A')}\n\n"
        )
        text_asistente = (
            f"🧑‍💼 *Asistente:*\n"
            f"{asistente.get('nombre', 'N/A')}\n"
            f"📞 {asistente.get('telefono', 'N/A')}\n"
            f"📧 {asistente.get('correo', 'N/A')}\n"
        )
        response_text = text_director + text_asistente
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="CONTACTO")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    elif choice == "CONTACTO_PROFESORES":
        profesores = data.get("profesores", [])
        if profesores:
            texto = "*👨‍🏫 Lista de Profesores:*\n\n"
            for p in profesores:
                texto += (
                    f"{p.get('nombre', 'N/A')}\n"
                    f"📧 {p.get('correo', 'N/A')}\n"
                    f"📞 {p.get('telefono', p.get('tel_oficina', 'N/A'))}\n"
                    f"🏢 Oficina: {p.get('oficina', 'N/A')}\n"
                    f"🕐 Consulta: {p.get('consulta', 'N/A')}\n\n"
                )
        else:
            texto = "No hay información de profesores registrada en el JSON."
        response_text = texto
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="CONTACTO")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    elif choice == "CONTACTO_ASOCIACION":
        aso = data.get("contacto_asociacion", {})
        presidente = aso.get("presidente", {})
        vicepresidente = aso.get("vicepresidente", {})
        miembros = aso.get("miembros", [])

        texto = "*🎓 Asociación Estudiantil:*\n\n"
        texto += (
            f"👔 *Presidente:*\n{presidente.get('nombre', 'N/A')}\n"
            f"📞 {presidente.get('telefono', 'N/A')}\n"
            f"📧 {presidente.get('correo', 'N/A')}\n\n"
        )
        texto += (
            f"🤝 *Vicepresidente:*\n{vicepresidente.get('nombre', 'N/A')}\n"
            f"📞 {vicepresidente.get('telefono', 'N/A')}\n"
            f"📧 {vicepresidente.get('correo', 'N/A')}\n\n"
        )
        texto += "*🧑‍🎓 Otros miembros:*\n"
        for m in miembros:
            texto += (
                f"{m.get('nombre', 'N/A')}\n"
                f"📧 {m.get('correo', 'N/A')}\n"
                f"📱 {m.get('telefono', 'N/A')}\n"
                f"💬 {m.get('telegram', 'N/A')}\n\n"
            )
        response_text = texto
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="CONTACTO")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # ------------------------------------------------------------------------
    # UBICACIONES CES
    # ------------------------------------------------------------------------
    elif choice == "UBICACIONES":
        # Si tu JSON tuviera un campo "ubicaciones", cargarlo
        # (no está en tu snippet, pero puedes añadirlo si lo deseas)
        ub = data.get("ubicaciones", {})
        if ub:
            text_ubi = (
                f"Edificios: {ub.get('edificios','N/A')}\n\n"
                f"Laboratorios: {ub.get('laboratorios','N/A')}\n\n"
                f"Impresión 3D: {ub.get('impresion_3d','N/A')}\n\n"
            )
            response_text = text_ubi
        else:
            response_text = "Ubicaciones no disponibles en el JSON."

        keyboard = [
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # ------------------------------------------------------------------------
    # VOLVER AL MENÚ
    # ------------------------------------------------------------------------
    elif choice == "VOLVER_MENU":
        await query.message.delete()
        await start_command(update, context) # se cambio esta linea
        return

    else:
        response_text = "Opción no reconocida. Volviendo al menú principal."
        keyboard = [[InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    history[user_id].append(("bot", response_text))
    await query.message.reply_text(response_text, reply_markup=reply_markup)

# ----------------------------------------------------------------------------
# Manejador de mensajes de texto: para buscar el curso (modo = "consulta_curso")
# ----------------------------------------------------------------------------
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text_in = update.message.text.strip()
    history[user_id].append(("user", text_in))

    data = context.bot_data.get("info", {})
    plan = data.get("plan_estudios", {})
    bloques = plan.get("bloques", [])

    modo = context.user_data.get("modo", None)

    def buscar_cursos_similares(nombre_o_codigo, lista_cursos, limite=5):
        nombres = [curso["nombre"] for curso in lista_cursos]
        codigos = [curso["codigo"] for curso in lista_cursos]
        todos = nombres + codigos
        coincidencias = get_close_matches(nombre_o_codigo.upper(), todos, n=limite, cutoff=0.4)
        resultados = []
        for match in coincidencias:
            for curso in lista_cursos:
                if match == curso["nombre"] or match == curso["codigo"]:
                    resultados.append(curso)
        return resultados

    if modo == "consulta_curso":
        if text_in.lower() == "/cancelar":
            context.user_data["modo"] = None
            msg = "Operación cancelada. Vuelve al menú principal."
        else:
            todos_cursos = []
            for bloque in bloques:
                todos_cursos.extend(bloque.get("cursos", []))

            similares = buscar_cursos_similares(text_in.strip(), todos_cursos)

            if len(similares) == 1:
                c = similares[0]
                msg = (
                    f"*{c['codigo']} - {c['nombre']}*\n"
                    f"Créditos: {c['creditos']}\n"
                    f"Horas: {c['horas']}\n"
                    f"Requisitos: {c['requisitos']}\n"
                    f"Correquisitos: {c['correquisitos']}"
                )
            elif len(similares) > 1:
                msg = "🔎 Encontré varios cursos similares:\n\n"
                for c in similares:
                    msg += f"• *{c['codigo']}* - {c['nombre']}\n"
                msg += "\nEscribe nuevamente el código o nombre exacto si quieres más detalles."
            else:
                msg = (
                    f"No encontré un curso que coincida con '{text_in}'. "
                    "Prueba de nuevo o escribe /cancelar para salir."
                )
        history[user_id].append(("bot", msg))
        await update.message.reply_text(msg)
    else:
        msg = "Usa /start para ver el menú o selecciona una opción del teclado."
        history[user_id].append(("bot", msg))
        await update.message.reply_text(msg)
# ----------------------------------------------------------------------------
# main()
# ----------------------------------------------------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Cargamos datos del JSON
    async def post_init(application):
        await load_data_into_bot_data(application)
    app.post_init = post_init

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(main_menu_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    app.run_polling()

if __name__ == "__main__":
    main()
