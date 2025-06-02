import json
from collections import defaultdict
from difflib import get_close_matches
import random
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
            "🔍 Ingresa *el código o el nombre* del curso (por ejemplo, CE1101 o "
            "INTRODUCCIÓN A LA PROGRAMACIÓN) para ver sus requisitos.\n\n"
            "Si no estás seguro, escribe una parte del nombre o código y el bot te sugerirá cursos similares.\n\n"
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
        ub = data.get("ubicaciones", {})
        if ub:
            for ubicacion in ub:
                nombre = ubicacion.get("nombre", "Ubicación")
                descripcion = ubicacion.get("descripcion", "Sin descripción.")
                imagen_path = ubicacion.get("imagen")

                if imagen_path:
                    try:
                        with open(imagen_path, 'rb') as img:
                            await query.message.reply_photo(photo=img, caption=f"{nombre.upper()}\n{descripcion}")
                    except FileNotFoundError:
                        await query.message.reply_text(f"{nombre.upper()}\n{descripcion}\n\n[Imagen no encontrada]")
                else:
                    await query.message.reply_text(f"{nombre.upper()}\n{descripcion}")
        else:
            await query.message.reply_text("Ubicaciones no disponibles en el JSON.")

        # Botón para volver
        keyboard = [
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="VOLVER_MENU")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Selecciona una opción:", reply_markup=reply_markup)

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

    # -------------------- RESPUESTA EMOCIONAL AUTOMÁTICA --------------------
    respuesta_emo = detectar_emocional(text_in)
    if respuesta_emo:
        await update.message.reply_text(respuesta_emo, parse_mode="Markdown")
        return
    # -----------------------------------------------------------------------

    data = context.bot_data.get("info", {})
    plan = data.get("plan_estudios", {})
    bloques = plan.get("bloques", [])

    modo = context.user_data.get("modo", None)

    # Extraer todos los cursos
    todos_cursos = []
    for b in bloques:
        for curso in b.get("cursos", []):
            todos_cursos.append(curso)

    # Modo: esperando respuesta de una lista de sugerencias
    if modo and modo.startswith("esperando_respuesta_"):
        opciones = context.user_data.get("opciones_sugeridas", [])
        entrada = text_in.strip().lower()
        curso = None

        # Si es número (índice de la lista)
        if entrada.isdigit():
            index = int(entrada) - 1
            if 0 <= index < len(opciones):
                curso = opciones[index]
        else:
            # También acepta nombre o código exacto después de sugerencias
            for c in opciones:
                if entrada == c.get("codigo", "").lower() or entrada == c.get("nombre", "").lower():
                    curso = c
                    break

        if curso:
            msg = (
                f"*{curso['codigo']} - {curso['nombre']}*\n"
                f"Créditos: {curso['creditos']}\n"
                f"Horas: {curso['horas']}\n"
                f"Requisitos: {curso['requisitos']}\n"
                f"Correquisitos: {curso['correquisitos']}"
            )
            context.user_data["modo"] = None
            context.user_data.pop("opciones_sugeridas", None)
        else:
            msg = (
                "Entrada inválida. Por favor responde con un *número*, *código* o *nombre exacto* de la lista mostrada, "
                "o escribe /cancelar."
            )

        history[user_id].append(("bot", msg))
        await update.message.reply_text(msg)
        return

    # Modo: búsqueda normal por texto libre
    if modo == "consulta_curso":
        if text_in.lower() == "/cancelar":
            context.user_data["modo"] = None
            msg = "✅ Operación cancelada. Vuelve al menú principal."
            await update.message.reply_text(msg)
            return

        entrada = text_in.lower()
        exacto = None
        nombres_codigos = []
        mapa_cursos = {}

        for c in todos_cursos:
            cod = c.get("codigo", "").lower()
            nom = c.get("nombre", "").lower()
            nombres_codigos.append(cod)
            nombres_codigos.append(nom)
            mapa_cursos[cod] = c
            mapa_cursos[nom] = c
            if entrada == cod or entrada == nom:
                exacto = c

        if exacto:
            msg = (
                f"*{exacto['codigo']} - {exacto['nombre']}*\n"
                f"Créditos: {exacto['creditos']}\n"
                f"Horas: {exacto['horas']}\n"
                f"Requisitos: {exacto['requisitos']}\n"
                f"Correquisitos: {exacto['correquisitos']}"
            )
            context.user_data["modo"] = None
            await update.message.reply_text(msg)
            return

        # Si no se encontró exacto, buscar similares
        similares = get_close_matches(entrada, nombres_codigos, n=5, cutoff=0.4)
        if similares:
            cursos_similares = []
            vistos = set()
            for s in similares:
                curso = mapa_cursos.get(s)
                if curso and curso["codigo"] not in vistos:
                    cursos_similares.append(curso)
                    vistos.add(curso["codigo"])

            context.user_data["modo"] = f"esperando_respuesta_{entrada}"
            context.user_data["opciones_sugeridas"] = cursos_similares

            msg = "🔎 Encontré varios cursos similares:\n\n"
            for idx, c in enumerate(cursos_similares, start=1):
                msg += f"{idx}) *{c['codigo']}* - {c['nombre']}\n"
            msg += "\nPor favor responde con el *número*, *código* o *nombre exacto* del curso que deseas consultar o escribe /cancelar."
        else:
            msg = (
                f"No encontré cursos similares a '{text_in}'. "
                "Revisa la ortografía o escribe /cancelar para volver."
            )

        history[user_id].append(("bot", msg))
        await update.message.reply_text(msg)
    else:
        msg = "Usa /start para ver el menú o selecciona una opción del teclado."
        history[user_id].append(("bot", msg))
        await update.message.reply_text(msg)
        
respuestas_saludo = [
    "¡Hola! 😊 Qué gusto saludarte. Espero que tu día vaya genial.",
    "¡Hey! 🌟 ¿Cómo vas con tus cursos? Si necesitas ayuda, estoy aquí para apoyarte.",
    "¡Qué bueno verte por aquí! 💻 Recuerda que cada paso te acerca más al título. 💪",
    "¡Super bien! Ya me dieron la nota de mi TFG y me fue excelente, estoy pronto a graduarme. 🎓",
    "¡Hola futuro profesional! 🚀 ¿En qué te puedo ayudar hoy?",
    "¡Hola colega ingeniero/a en formación! Cada mensaje que envías es un paso más hacia tu meta. 💡",
    "¡Bienvenido/a! Recuerda que todo esfuerzo tiene su recompensa. Aquí estoy para ayudarte. 🤗",
    "¡Saludos desde el mundo digital! Estoy aquí para acompañarte en tu camino universitario. 📚",
    "¡Hola, crack del TEC! Nada como avanzar con inteligencia y pasión. ¿Qué necesitas hoy? 🔍",
    "¡Hola! Me emociona saber que estás comprometido/a con tu futuro. ¡A darle con todo! 💥",
    "¡Hola hola! 🌚 Siempre es un buen momento para aprender algo nuevo. 🤔",
    "¡Hola! 🙋‍♂️ Espero que estés teniendo un semestre exitoso.",
    "¡Hola estudiante estrella! 🌟 Este cuatri va a ser tuyo. Yo te acompaño."
] + [
    f"¡Hola #{i}! ¿En qué puedo asistirte hoy con tus cursos, tu plan o tus sueños? 😊"
    for i in range(1, 21)
]

respuestas_tristeza = [
    "Lo siento mucho 💔. Si necesitas hablar con alguien o ayuda con algún curso, estoy aquí para apoyarte.",
    "No estás solo/a, sigue adelante. Cada reto es una oportunidad para crecer. 🌱",
    "Las cosas mejorarán pronto 🌈. Mientras tanto, cuídate y sigue intentándolo.",
    "A veces se vale sentirse mal 😢, pero recuerda que eres fuerte y capaz de superar cualquier obstáculo.",
    "¡Ánimo! Estoy seguro de que vas a salir adelante, no te rindas. 💪",
    "Sé que los días difíciles existen, pero también sé que tú tienes la capacidad de superarlos. ❤️",
    "Todo va a estar bien. Los caminos difíciles muchas veces conducen a destinos maravillosos. 🌄",
    "Un mal día no define tu camino. Mañana es una nueva oportunidad. Respira y sigue. 🫲",
    "Si hoy estás triste, permítete sentir. Mañana volverás a brillar más fuerte. ✨",
    "Te mando un abrazo virtual gigante 🤗. Recuerda que después de la tormenta siempre sale el sol. ☀️"
] + [
    f"¡Fuerza #{i}! Cada paso aunque sea pequeño, cuenta. Estoy contigo. 💕"
    for i in range(1, 31)
]

respuestas_emocionales_bonitas = [
    "¡Qué lindo mensaje! 💖 Gracias por compartirlo. ¡Te deseo lo mejor siempre!",
    "Tu buena energía se siente hasta aquí. 😊 ¡Sigue brillando!",
    "¡Me alegraste el día! 💫 Espero que el tuyo esté lleno de éxitos también.",
    "Gracias por ser tan positivo/a 🌟. El TEC necesita más personas como tú.",
    "¡Wow! Eres increíble, sigue siendo así de especial. 🌺",
    "¡Gracias por tu mensaje! Es un honor acompañarte en tu viaje académico. 🚀",
    "¡Qué emoción leerte! Con esa actitud, no hay límites. 💚",
    "Estoy feliz de ayudarte. ¡Nunca dejes de creer en ti mismo/a! ⭐",
    "Tus palabras motivan más de lo que imaginas. Gracias por ser parte de esta comunidad. 🙌",
    "¡Gracias por el cariño! Siempre estaré aquí para vos. ❤️‍🔥"
] + [
    f"¡Tu energía positiva #{i} inspira a seguir! 🎉"
    for i in range(1, 31)
]

respuestas_ayuda = [
    "¿Buscas información sobre algún curso? Ve a *REQUISITOS* en el menú 📚",
    "¿Necesitas saber cómo contactar a un profesor? Selecciona *CONTACTO* en el menú 👨‍🏫",
    "Si quieres ver los cursos de un semestre, selecciona *PLAN DE ESTUDIOS* 🗂️",
    "¿Deseás saber quiénes están en la Asociación? Dale a *CONTACTO → Asociación Estudiantil* 🎓",
    "¿Necesitás apoyo con requisitos, bloques o estructura de la carrera? El menú tiene todas las herramientas.",
    "Usa los botones del menú para navegar fácilmente por toda la información de tu plan de estudios. ¡Es sencillo! 😄",
    "Estoy para ayudarte: ya sea sobre cursos, profesores, semestres o vida estudiantil. Usá el menú o preguntame. 📘",
    "Para consultas más específicas, podés buscar por nombre o código del curso en *REQUISITOS*. ¡Proba ahora!",
    "Explora los bloques de cursos en *PLAN DE ESTUDIOS*. Te ayudará a planificar tu camino hacia la graduación. 🎓",
    "¿No sabés por dónde empezar? Probá con el botón *Menú Principal* y seguimos desde ahí juntos. 🧡"
] + [
    f"¡Explorá el menú sin miedo, está diseñado para vos #{i}! 📄"
    for i in range(1, 21)
]

palabras_tristeza = [
    "triste", "mal", "estresado", "estresada", "deprimido", "deprimida", "llorar", "cansado", "cansada", "agotado",
    "ansioso", "ansiosa", "miedo", "inseguro", "insegura", "fracaso", "estres", "colapso", "bajoneado", "agobiado",
    "solitario", "preocupado", "inquieto", "saturado", "quebrado", "solo", "llanto", "pena", "duele"
]

palabras_bonitas = [
    "gracias", "❤", "💖", "😊", "✨", "😍", "💫", "💙", "🌟", "🌈",
    "🥰", "💐", "🙌", "🤗", "👍", "👏", "felicidades", "super bien", "que bonito",
    "adorable", "precioso", "bonito", "motiva", "hermoso", "bendiciones", "alegría", "contento", "te aprecio", "vales mucho"
]

def detectar_emocional(texto):
    texto = texto.lower()
    if any(p in texto for p in ["hola", "buenas", "saludos", "hey", "hello"]):
        return random.choice(respuestas_saludo)
    elif any(p in texto for p in palabras_tristeza):
        return random.choice(respuestas_tristeza)
    elif any(p in texto for p in palabras_bonitas):
        return random.choice(respuestas_emocionales_bonitas)
    elif any(p in texto for p in ["ayuda", "necesito", "cómo hago", "información", "profesor", "consulta"]):
        return random.choice(respuestas_ayuda) + "\n\nSi estás triste o contento también podés escribirme y te acompaño. 🤗"
    return None



async def respuesta_emocional_y_ayuda(update, context):
    texto = update.message.text.lower()
    respuesta = None

    if any(p in texto for p in ["hola", "buenas", "saludos", "hey", "hello", "qué tal", "holi", "saludito"]):
        respuesta = random.choice(respuestas_saludo)
    elif any(p in texto for p in palabras_tristeza):
        respuesta = random.choice(respuestas_tristeza)
    elif any(p in texto for p in palabras_bonitas):
        respuesta = random.choice(respuestas_emocionales_bonitas)
    elif any(p in texto for p in ["ayuda", "necesito", "cómo hago", "información", "profesor", "consulta", "bloques", "requisitos", "asociación"]):
        respuesta = random.choice(respuestas_ayuda) + "\n\nSi estás triste o contento también podés escribirme y te acompaño. 🤗"

    if respuesta:
        await update.message.reply_text(respuesta, parse_mode="Markdown")
        return True
    return False
        
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
