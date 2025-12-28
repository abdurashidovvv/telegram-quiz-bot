import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from parser import parse_tests  # parse_tests fayl ichida har bir test: (question, options, correct)

# =====================
# BOT TOKEN
# =====================
BOT_TOKEN = "8393381535:AAF3ypspBhTXYLpTWN8B4JWJq8V13w1jb4I"

# =====================
# BOT & DISPATCHER
# =====================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =====================
# MA'LUMOTLAR SAQLASH
# =====================
user_results = {}   # {user_id: {"total": int, "correct": int}}
active_poll = {}    # {user_id: {"current_index": int, "tests": list, "poll_id": int}}

# =====================
# START BUYRUG‘I
# =====================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "📄 Word (.docx) formatdagi test faylni yuboring.\n"
        "✏️ Format:\n"
        "1. Savol matni\n"
        "+ To‘g‘ri javob\n"
        "- Noto‘g‘ri javob\n\n"
        "📊 Test tugagach /result buyrug‘ini yozing"
    )

# =====================
# WORD FAYL QABUL QILISH
# =====================
@dp.message(F.document)
async def handle_doc(message: types.Message):
    document = message.document

    if not document.file_name.endswith(".docx"):
        await message.answer("❌ Iltimos, faqat .docx formatdagi Word fayl yuboring")
        return

    file = await bot.get_file(document.file_id)
    await bot.download_file(file.file_path, "tests.docx")

    tests = parse_tests("tests.docx")

    if not tests:
        await message.answer("❌ Word fayldan test topilmadi")
        return

    user_id = message.from_user.id

    # Natijalarni saqlash
    user_results[user_id] = {"total": len(tests), "correct": 0}
    active_poll[user_id] = {"current_index": 0, "tests": tests, "poll_id": None}

    await message.answer(f"📝 Test boshlandi!\nSavollar soni: {len(tests)}\nHar bir savolga javob berish bilan keyingi savol keladi.")

    # Birinchi savolni yuborish
    await send_next_poll(message.chat.id, user_id)

# =====================
# KEYINGI SAVOLNI YUBORISH
# =====================
async def send_next_poll(chat_id, user_id):
    poll_info = active_poll[user_id]
    index = poll_info["current_index"]
    tests = poll_info["tests"]

    if index >= len(tests):
        # Barcha savollar tugadi
        await bot.send_message(chat_id, "✅ Test tugadi! /result buyrug‘ini yozib natijani ko‘ring.")
        active_poll.pop(user_id)
        return

    question, options, correct = tests[index]

    msg = await bot.send_poll(
        chat_id=chat_id,
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct,
        is_anonymous=False
    )

    poll_info["poll_id"] = msg.poll.id

# =====================
# POLL JAVOBINI QABUL QILISH
# =====================
@dp.poll_answer()
async def poll_answer_handler(poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id

    if user_id not in active_poll:
        return

    poll_info = active_poll[user_id]

    if poll_info["poll_id"] != poll_answer.poll_id:
        return

    # tuple indeks bilan ishlash
    current_test = poll_info["tests"][poll_info["current_index"]]
    correct = current_test[2]  # 0=question, 1=options, 2=correct

    selected = poll_answer.option_ids[0]
    if selected == correct:
        user_results[user_id]["correct"] += 1

    # Keyingi savolga o‘tish
    poll_info["current_index"] += 1
    await send_next_poll(poll_answer.user.id, user_id)

# =====================
# NATIJANI KO‘RISH
# =====================
@dp.message(Command("result"))
async def show_result(message: types.Message):
    result = user_results.get(message.from_user.id)
    if not result:
        await message.answer("❗ Siz hali test topshirmagansiz")
        return

    total = result["total"]
    correct = result["correct"]
    wrong = total - correct
    percent = round(correct / total * 100, 1)

    await message.answer(
        "📊 TEST YAKUNI\n\n"
        f"Jami savollar: {total}\n"
        f"To‘g‘ri javoblar: {correct}\n"
        f"Noto‘g‘ri javoblar: {wrong}\n\n"
        f"Natija: {percent}%"
    )

# =====================
# BOTNI ISHGA TUSHIRISH
# =====================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
