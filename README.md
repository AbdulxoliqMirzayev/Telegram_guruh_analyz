# Telegram_guruh_analyz
# Telegram Guruh Tahlilchi (AI bilan mavzularni aniqlovchi bot)

Bu dastur **Telegram guruhidagi so‘nggi 7 kunlik xabarlarni** o‘qib, har bir muhokamani **AI yordamida tahlil qiladi** va **eng ko‘p muhokama qilingan mavzularni** aniqlaydi.

Ushbu loyiha kichik, lekin juda foydali:
Telegram guruhdagi odamlar **nima haqida gaplashayotganini avtomatik aniqlaydi**
Har bir kun uchun **TOP 3 mavzuni** chiqaradi
Natijani **JSON fayl** ko‘rinishida saqlaydi (`result.json`)

---

## Asosiy ishlash logikasi

1. **Telegram bilan ulanadi**
   `Telethon` kutubxonasi orqali siz kiritgan `API_ID`, `API_HASH` va `PHONE` orqali Telegram hisobingizga ulanadi.
   So‘ngra berilgan guruhdagi (`GROUP_USERNAME`) xabarlarni o‘qiydi.

2. **Xabarlarni tozalaydi**
   `tozalash_matn()` funksiyasi har bir xabardan emoji, sticker va keraksiz belgilarni olib tashlaydi,
   faqat matnni qoldiradi — shunda AI tahlil qilishni osonroq qiladi.

3. **Dialoglarni aniqlaydi (muhokamalarni)**
   Agar bir nechta foydalanuvchi bitta xabarga javob yozgan bo‘lsa, bu xabarlar **bitta “thread” (mavzu)** deb qaraladi.
   Har bir thread uchun xabarlar soni, userlar soni va matnlar yig‘iladi.

4. **AI yordamida mavzuni topadi (Gemini 2.5)**
   Har bir muhokamadagi matnlar Gemini AI ga yuboriladi.
   Modeldan so‘raladi:

   > “Bu suhbatda qanday mavzu muhokama qilinmoqda? 2–5 so‘z bilan ayting.”

   Masalan:

   ```
   Ali: Bugun havo sovuq  
   Vali: Ha, rostdan ham sovuq  
   Natija: "Ob-havo"
   ```

5. **Eng faol mavzularni tanlaydi**
   Har bir kun uchun eng ko‘p xabar yozilgan 3 ta mavzuni topadi.
   Bu sizga guruhda kim nima haqida ko‘p gaplashayotganini ko‘rsatadi.

6. **Natijani saqlaydi**
   Yakuniy tahlil `result.json` faylida saqlanadi, masalan:

   ```json
   {
     "timezone": "Asia/Tashkent",
     "days": [
       {
         "date": "2025-10-17",
         "threads": [
           {"topic": "AI va dasturlash", "messages": 34, "users": 9},
           {"topic": "Telegram botlar", "messages": 27, "users": 5},
           {"topic": "Ob-havo", "messages": 12, "users": 4}
         ]
       }
     ]
   }
   ```

---

## ⚙️ Ishga tushirish bosqichlari

1. **Kutubxonalarni o‘rnatish:**

   ```bash
   pip install telethon google-genai pytz
   ```

2. **Sozlamalarni kiriting:**
   Fayl boshida quyidagilarni to‘ldiring:

   ```python
   GEMINI_API_KEY = " bu yerga Gemini API kalitingizni yozing"
   API_ID = "Telegram API ID"
   API_HASH = " Telegram API Hash"
   PHONE = " Telefon raqamingiz"
   GROUP_USERNAME = " Guruh havolasi yoki username"
   ```

3. **Dastur ishga tushiring:**

   ```bash
   python telegram_tahlil.py
   ```

4. **Natija:**

   * `result.json` fayl hosil bo‘ladi
   * Terminalda TOP mavzular chiroyli tarzda ko‘rsatiladi


Bu loyiha AI yordamida **Telegramdagi muhokamalarni tahlil qilishni avtomatlashtiradi.**
Ushbu kodni yanada rivojlantirib:

* Mavzularni vaqt bo‘yicha grafikda ko‘rsatish
* Har bir user faolligini hisoblash
* CSV yoki Dashboard ko‘rinishida eksport qilish
  kabi funksiyalar qo‘shish mumkin.

---

##  Muallif
 **Abdulxoliq Mirzayev**

