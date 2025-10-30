"""LocTur Telegram boti uchun matnli konstantalar.

Ushbu faylda foydalanuvchiga ko‘rsatiladigan barcha matnlar tarjimani osonlashtirish uchun jamlangan.
Matnlar funksionallik va kontekst bo‘yicha tartiblangan.
"""

# Asosiy menyu va navigatsiya
MAIN_MENU_GREETING = "Salom, {name}!\nQuyidagi variantlardan birini tanlang va boshlaymiz."
MAIN_MENU_TITLE = "Asosiy menyu:"
REGISTER_FOR_TRIP = "Sayohatga ro‘yxatdan o‘tish"
MY_REGISTRATIONS = "Mening ro‘yxatlarim"
BACK_TO_MENU = "Menyuga qaytish"

# Sayohat tanlash va ko‘rsatish
TRIP_HIGHLIGHTS = "Hozirgi sayohatlar haqida qisqacha ma’lumot:\n\n"
PICK_TRIP_TO_REGISTER = "Ro‘yxatdan o‘tish uchun sayohatni tanlang:"
NO_TRIPS_AVAILABLE = "Hozircha ochiq sayohatlar yo‘q. Keyinroq qayta tekshirib ko‘ring."
UNABLE_TO_LOAD_TRIPS = "Kechirasiz, sayohatlar yuklanmadi. Birozdan so‘ng qayta urinib ko‘ring."
UNABLE_TO_LOAD_TRIP = "Bu sayohatni yuklab bo‘lmadi. Iltimos, boshqasini tanlang."

# Ro'yxatdan o'tish jarayoni
FIRST_TIME_REGISTRATION = "Birinchi marta ro'yxatdan o'tyapsiz. Keling, siz haqingizda ma'lumotlarni to'playmiz."
LETS_GET_DETAILS = "Keling, siz haqingizda ma'lumotlarni to'playmiz."
SEND_FIRST_NAME = "Iltimos, <b>ismingizni</b> yuboring (hozirgi: <code>{current}</code>)."
SEND_LAST_NAME = "Ajoyib! Endi <b>familiyangizni</b> yuboring (hozirgi: <code>{current}</code>). O'tkazib yuborish uchun '-' yuboring."
SHARE_PHONE_NUMBER = "Iltimos, telefon raqamingizni yuboring. Uni yozishingiz yoki quyidagi tugma orqali ulashishingiz mumkin."
SHARE_PHONE_BUTTON = "Telefon raqamni ulashish"
EXTRA_INFO_PROMPT = "Qo'shimcha ma'lumot bormi? (Bo'lmasa '-' yuboring.)"

# Tasdiqlash xabarlari
PLEASE_SEND_VALID_FIRST_NAME = "Iltimos, haqiqiy ism yuboring."
PHONE_NOT_CAUGHT = "Telefon raqamini tushunmadim. Qaytadan yuboring."
INVALID_PHONE_NUMBER = "Bu raqam to‘g‘ri formatda emas. Iltimos, qayta kiriting."

# To‘lov va yakuniy bosqich
PAYMENT_PROOF_PROMPT = "Deyarli tayyor! <b>{trip_title}</b> uchun to‘lov kvitansiyasining fotosurati yoki PDF faylini yuboring (miqdor: {amount})."
PLEASE_SEND_PAYMENT_PROOF = "Iltimos, to‘lov dalilini (foto yoki hujjat) yuboring."
UNSUPPORTED_FILE_TYPE = "Bu turdagi fayl qo‘llab-quvvatlanmaydi. Faqat foto yoki PDF yuboring."
PAYMENT_SUBMITTED = "Rahmat! To‘lov dalilingiz yuborildi.\nAdminlar tasdiqlagach sizga xabar beriladi."
TRIP_SUMMARY = "Sayohat haqida umumiy ma’lumot:\n{summary}"

# Ro‘yxatdan o‘tish holati va xatolar
ALREADY_REGISTERED = "Siz bu sayohatga allaqachon ro‘yxatdan o‘tgansiz."
COULDNT_SAVE_PROFILE = "Profilingizni saqlab bo‘lmadi. Keyinroq urinib ko‘ring."
COULDNT_SUBMIT_REGISTRATION = "Ro‘yxatdan o‘tish jarayonini yakunlab bo‘lmadi. Keyinroq urinib ko‘ring."

# Foydalanuvchi ro‘yxatlari
NO_REGISTRATIONS_YET = "Siz hali hech qanday sayohatga yozilmagansiz. Menyudan birinchisini tanlang!"
YOUR_REGISTRATIONS = "Sizning ro‘yxatlaringiz:"
REGISTRATION_LINE = "• <b>{title}</b>: holat={status}, to‘lov={payment}"
GET_INVITE_FOR = "{title} uchun taklif olish"
TAP_FOR_INVITE = "Taklif havolasini qayta olish uchun quyidagi tugmani bosing:"

# Guruh bilan bog‘lash komandalar
LINK_TRIP_GROUP_ONLY = "Bu komandani sayohat guruhi ichida ishlating."
LINK_TRIP_USAGE = "Foydalanish: /link_trip <trip_id> [invite_link]"
UNABLE_TO_LINK_GROUP = "Guruhni bog‘lab bo‘lmadi. Iltimos, sayohat ID’sini tekshirib qayta urinib ko‘ring."
GROUP_SUCCESSFULLY_LINKED = "Guruh sayohat bilan muvaffaqiyatli bog‘landi. Endi tasdiqlangan sayohatchilar bu yerga taklif qilinadi."

# Guruh takliflari va qo‘shilish
JOIN_TRIP_GROUP = "Sayohat guruhiga qo‘shilish"
PAYMENT_CONFIRMED_MESSAGE = "🎉 <b>{trip_title}</b> uchun to‘lovingiz tasdiqlandi!\nGuruhga kirish uchun quyidagi tugmani bosing."
INVITE_SENT = "Taklif yuborildi! Havolani chat tarixidan topasiz."
UNABLE_TO_SEND_INVITE = "Taklif havolasini yuborib bo‘lmadi. Iltimos, yordam markaziga murojaat qiling."
REGISTRATION_NOT_CONFIRMED = "Bu ro‘yxat hali tasdiqlanmagan. Iltimos, kuting."
COULDNT_LOAD_REGISTRATION = "Ro‘yxat ma’lumotlarini yuklab bo‘lmadi. Keyinroq urinib ko‘ring."

# Guruhga kirish tasdiqlanganda
WELCOME_TO_GROUP = "{group_title} guruhiga xush kelibsiz! Endi siz guruhdasiz."

# Guruh funksiyalaridagi xatolar
TRAVELER_MISSING_TELEGRAM_ID = "Sayohatchining Telegram ID’si topilmadi."
INVALID_TELEGRAM_ID = "Noto‘g‘ri Telegram ID saqlangan."
NO_TELEGRAM_GROUP_CONFIGURED = "Sayohat uchun Telegram guruhi bog‘lanmagan. Admin /link_trip ni ishlatishi kerak."
INVALID_CHAT_ID = "Sayohat guruhi chat ID’si noto‘g‘ri. /link_trip ni qayta bajaring."
BOT_CANNOT_MESSAGE_TRAVELER = "Bot foydalanuvchiga xabar yubora olmayapti."

# Sayohat formatlash
TRIP_LOCATION = "Manzil: {location}"
TRIP_DATES = "Sana: {start} → {end}"
TRIP_STARTS = "Boshlanish sanasi: {start}"
TRIP_PRICE = "Narx: {price}"

# O‘rinbosar qiymatlar
NOT_SET = "ko‘rsatilmagan"
TRIP_DEFAULT_TITLE = "Sayohat"

# Ichki loglar (ixtiyoriy)
LOGGING_BOT_STARTED = "Telegram bot ishga tushdi."
LOGGING_BOT_STOPPED = "Telegram bot to‘xtadi."
LOGGING_UNABLE_TO_FETCH_TRIPS_START = "/start da sayohatlar yuklanmadi: {error}"
LOGGING_FAILED_TO_FETCH_TRIPS = "Sayohatlar yuklanmadi: {error}"
LOGGING_FAILED_TO_FETCH_TRIP = "{trip_id} sayohatini yuklab bo‘lmadi: {error}"
LOGGING_FAILED_TO_LINK_TRIP = "{trip_id} sayohatini {chat_id} chatiga bog‘lab bo‘lmadi: {error}"
LOGGING_FAILED_TO_UPSERT_TRAVELER = "Sayohatchini saqlab bo‘lmadi: {error}"
LOGGING_FAILED_TO_CREATE_USER_TRIP = "Foydalanuvchi sayohatini yaratib bo‘lmadi: {error}"
LOGGING_FAILED_TO_APPROVE_JOIN = "{user_trip_id} uchun guruhga qo‘shilishni tasdiqlab bo‘lmadi: {error}"
LOGGING_CANNOT_SEND_WELCOME = "{user_id} foydalanuvchiga xush kelibsiz xabarini yubora olmadik (bloklangan bo‘lishi mumkin)."
LOGGING_FAILED_TO_FETCH_USER_TRIP = "{user_trip_id} foydalanuvchi sayohatini yuklab bo‘lmadi (taklif uchun): {error}"
