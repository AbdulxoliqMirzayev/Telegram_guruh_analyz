import json
import re
from datetime import datetime, timedelta
from collections import defaultdict
from telethon.sync import TelegramClient
import pytz
import time
# ============================================
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    print("XATOLIK: google-genai kutubxonasi topilmadi!")
    print("O'rnatish uchun: pip install google-genai")
    GENAI_AVAILABLE = False

# ============================================
# ============================================

#Gemini API kaliti 
GEMINI_API_KEY = "API kalit qo'ying"

# Telegram API sozlamalari
API_ID = "telegram id qo'ying"
API_HASH = "telegram hash qo'ying"
PHONE = "raqamingiz "

#  guruh nomi 
GROUP_USERNAME = "https://t.me/amocrmhelper"

MAX_MESSAGES = 10000
TIMEZONE = "Asia/Tashkent"
TOP_THREADS_COUNT = 3
MIN_MESSAGES_IN_THREAD = 3  # Kamida 3 ta xabar bolishi kerak

# ********************************************
# YORDAMCHI FUNKSIYALAR !!!!!!!!!!!!!!!!!!!!!!
# ============================================

def tozalash_matn(matn):
    """
    Xabardan emoji sticker belgilarni olib tashlaymiz
    Faqat toza matnni qoldiramiz !!
    """
    if not matn:
        return ""
    
    # Faqat lotin, kirill, raqam va asosiy tinish belgilarni qoldirish
    tozalangan = re.sub(r'[^\w\s\.\,\!\?\-А-Яа-яЁёЎўҚқҒғҲҳ]', '', matn)
    
    # Ortiqcha bo'sh joylarni olib tashlaymiz aniq ishlashi uchun 
    tozalangan = ' '.join(tozalangan.split())
    
    return tozalangan.strip()


def gemini_mavzu_topish(dialog_xabarlari, gemini_client):
    """
    Gemini 2.5 AI ga dialogni yani habarlarni yuboramiz va mavzu nomini olamiz
    Masalan:
    Input: ["Ali: Bugun havo sovuq", "Vali: Ha rostdan", ...]
    Output: "Ob-havo"
    """
    if not dialog_xabarlari or len(dialog_xabarlari) < 2:
        return "Noma'lum mavzu"
    
    # Dialogni tayyorlash va tozalash
    tozalangan_dialog = []
    for xabar in dialog_xabarlari:
        toza_xabar = tozalash_matn(xabar)
        if toza_xabar and len(toza_xabar) > 5:
            tozalangan_dialog.append(toza_xabar)
    
    if len(tozalangan_dialog) < 2:
        return "Noma'lum mavzu"
    
    # Dialogni yani habarlarni  bitta matn qilib birlashtirramiz !!!
    dialog_matni = "\n".join(tozalangan_dialog[:15])
    
    # Juda uzun bo'lsa, qisqartirish
    if len(dialog_matni) > 2500:
        dialog_matni = dialog_matni[:2500]
    
    # Gemini uchun aniq prompt yozamiz !!
    prompt = f"""Bu Telegram guruh dialogida qanday mavzu muhokama qilinmoqda? Faqat 2-5 so'z bilan o'zbek tilida javob ber.
Dialog:
{dialog_matni}
Mavzu (faqat 2-5 so'z !!):"""
    
    # Sinash uchun model nomlari (eng yangi birinchi)
    model_nomlari = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash", 
        "gemini-1.5-pro"
    ]
    
    for model_nomi in model_nomlari:
        try:
            # Rasmiy API - 2025
            response = gemini_client.models.generate_content(
                model=model_nomi,
                contents=prompt
            )
            
            # Javobni tozalash
            if response and hasattr(response, 'text') and response.text:
                mavzu = response.text.strip()
                
                # Ortiqcha belgilarni olib tashlaymiz !!
                mavzu = re.sub(r'["\'\*]', '', mavzu)
                mavzu = re.sub(r'(Mavzu|mavzu|Javob|javob):', '', mavzu)
                mavzu = mavzu.strip()
                
                # Birinchi qatorni olamiz
                if '\n' in mavzu:
                    mavzu = mavzu.split('\n')[0].strip()
                
                # Juda uzun bo'lsa, qisqartiramiz
                if len(mavzu) > 50:
                    mavzu = mavzu[:50]
                
                # Agar bo'sh yoki juda qisqa bo'lsa
                if not mavzu or len(mavzu) < 3:
                    return "Umumiy suhbat"
                
                return mavzu
            
        except Exception as e:
            error_msg = str(e)
            # Agar model topilmasa, keyingisini sinaymiz 
            if any(x in error_msg.lower() for x in ["not found", "404", "invalid !!!"]):
                continue
            else:
                print(f"      Xatolik ({model_nomi}): {error_msg[:100]}")
                continue
    
    # Agar hech qanday model ishlamasa - fallback !!!
    if tozalangan_dialog:
        birinchi = tozalangan_dialog[0]
        if ':' in birinchi:
            matn = birinchi.split(':', 1)[1].strip()
            sozlar = matn.split()[:4]
            return ' '.join(sozlar) if sozlar else "Umumiy suhbat"
    
    return "Umumiy suhbat"


def telegram_tahlil():
    """
    Telegram guruhni  tahlil qilamiz 
    """
    print("\n" + "="*70)
    print("TELEGRAM GURUH TAHLILI - DIALOGLARNI AI BILAN TAHLIL QILAMIZ")
    print("="*70 + "\n")
    
    # Gemini 2.5 sozlash
    if not GENAI_AVAILABLE:
        print("google-genai kutubxonasi topilmadi!")
        print("\nO'rnatish uchun quyidagi komandani bajaring:")
        print("  pip install google-genai")
        return
    
    print(" Gemini 2.5 AI sozlanmoqda...!")
    try:
        # gemiini  API
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Test qilamiz qaysi model ishlaydi bilish uchun 
        print("   Ulanish tekshirilmoqda...")
        test_models = ["gemini-2.0-flash-exp", "gemini-1.5-flash", "gemini-1.5-pro"]
        ishlagan_model = None
        
        for model_nomi in test_models:
            try:
                test_response = gemini_client.models.generate_content(
                    model=model_nomi,
                    contents="Test"
                )
                if test_response and test_response.text:
                    ishlagan_model = model_nomi
                    break
            except:
                continue
        
        if ishlagan_model:
            print(f"    Gemini 2.5 tayyor")
            print(f"    Model: {ishlagan_model}")
            print(f"    Status: BEPUL ")
        else:
            print("   Hech qanday Gemini modeli ishlamadi!")
            print("\n Tekshiring:")
            print("   1. Internet ulanishi")
            print("   2. API kaliti: https://aistudio.google.com/app/apikey")
            print("   3. google-genai versiyasi: pip install --upgrade google-genai")
            return
        
        print()
        
    except Exception as e:
        print(f"   Gemini sozlashda xatolik: {e}")
        print("\n  Yechim:")
        print("   pip install --upgrade google-genai")
        return
    
    
    tz = pytz.timezone(TIMEZONE)
    hozir = datetime.now(tz)
    yetti_kun_oldin = hozir - timedelta(days=7)
    
    print(f" Tahlil qilinadigan kunlar : {yetti_kun_oldin.date()} → {hozir.date()}\n")
    
    # Telegram client
    telegram_client = TelegramClient("session", API_ID, API_HASH)
    
    try:
        
        print(" Telegram ga ulanilmoqda...")
        telegram_client.start(phone=PHONE)
        print("   Ulandi\n")
        
        # Guruhni topish
        print(f" Guruh qidirilmoqda: {GROUP_USERNAME}")
        guruh = telegram_client.get_entity(GROUP_USERNAME)
        print(f"   Topildi: {guruh.title}\n")
        
        # Ma'lumotlar
        kunlik_threadlar = defaultdict(lambda: defaultdict(lambda: {
            'xabarlar_soni': 0,
            'userlar': set(),
            'dialog': []
        }))
        
        # Xabarlarni o'qish
        print(f" Xabarlar o'qilmoqda (max {MAX_MESSAGES} ta)...")
        print("-" * 70)
        
        xabar_soni = 0
        
        for msg in telegram_client.iter_messages(guruh, limit=MAX_MESSAGES):
            xabar_soni += 1
            
            if xabar_soni % 1000 == 0:
                print(f"   {xabar_soni} ta o'qildi...")
            
            if not msg.date:
                continue
            
            msg_vaqt = msg.date.astimezone(tz)
            if msg_vaqt < yetti_kun_oldin:
                break
            
            kun = msg_vaqt.date().isoformat()
            
            # Thread ID
            if msg.reply_to and msg.reply_to.reply_to_msg_id:
                thread_root = msg.reply_to.reply_to_msg_id
            else:
                thread_root = msg.id
            
            thread = kunlik_threadlar[kun][thread_root]
            thread['xabarlar_soni'] += 1
            
            if msg.sender_id:
                thread['userlar'].add(msg.sender_id)
            
            # Faqat matnli xabarlarni saqlash
            if msg.message and len(msg.message.strip()) > 0:
                try:
                    sender = msg.sender
                    if sender:
                        if hasattr(sender, 'first_name') and sender.first_name:
                            ism = sender.first_name
                        elif hasattr(sender, 'title') and sender.title:
                            ism = sender.title
                        else:
                            ism = "User"
                    else:
                        ism = "User"
                except:
                    ism = "User"
                
                dialog_qator = f"{ism}: {msg.message}"
                thread['dialog'].append(dialog_qator)
        
        print("-" * 70)
        print(f"    Jami {xabar_soni} ta xabar o'qildi\n")
        
        # Gemini bilan tahlil
        print(" Gemini 2.5 bilan dialoglar tahlil qilinmoqda...")
        print("="*70)
        
        natija = {
            'timezone': TIMEZONE,
            'days': []
        }
        
        kunlar = sorted(kunlik_threadlar.keys(), reverse=True)
        
        for kun in kunlar:
            print(f"\n {kun}")
            print("-"*70)
            
            threadlar = kunlik_threadlar[kun]
            thread_list = []
            
            dialog_num = 0
            for thread_id, data in threadlar.items():
                msg_count = data['xabarlar_soni']
                user_count = len(data['userlar'])
                
                # Faqat kamida MIN_MESSAGES_IN_THREAD ta xabor bo'lgan dialoglar
                if msg_count >= MIN_MESSAGES_IN_THREAD and len(data['dialog']) >= 2:
                    dialog_num += 1
                    
                    print(f"\n  Dialog #{dialog_num}:")
                    print(f"    Xabarlar: {msg_count}, Userlar: {user_count}")
                    
                    # Birinchi 3 ta xabarni ko'rsatish
                    for i, line in enumerate(data['dialog'][:3]):
                        qisqa = line[:80] + "..." if len(line) > 80 else line
                        print(f"      {qisqa}")
                    
                    if len(data['dialog']) > 3:
                        print(f"      ... (yana {len(data['dialog'])-3} ta xabar)")
                    
                    print("  Gemini 2.5 dan mavzu so'ralmoqda...", end=" ", flush=True)
                    
                    # Gemini dan mavzu aniqlash
                    mavzu = gemini_mavzu_topish(data['dialog'], gemini_client)
                    
                    print(f"Tayyor")
                    print(f"    Mavzu: \"{mavzu}\"")
                    
                    thread_list.append({
                        'mavzu': mavzu,
                        'messages': msg_count,
                        'users': user_count
                    })
                    
                    # Rate limit uchun kutish
                    time.sleep(2)
            
            # Saralash
            thread_list.sort(key=lambda x: (x['messages'], x['users']), reverse=True)
            
            # Top dialoglar yani eng kop muhokama qilingan mavzular
            top = thread_list[:TOP_THREADS_COUNT]
            
            if top:
                print(f"\n  {'='*66}")
                print(f"  TOP {len(top)} ENG KO'P MUHOKAMA QILINGAN MAVZU:")
                print(f"  {'='*66}")
                
                for i, t in enumerate(top, 1):
                    print(f"  {i}. \"{t['mavzu']}\"")
                    print(f"     └─ Xabarlar: {t['messages']}, Userlar: {t['users']}")
                
                natija['days'].append({
                    'date': kun,
                    'threads': [
                        {
                            'topic': t['mavzu'],
                            'messages': t['messages'],
                            'users': t['users']
                        }
                        for t in top
                    ]
                })
        
        # JSON ga saqlash
        print("\n" + "="*70)
        print(" Natija saqlanmoqda...")
        
        with open('result.json', 'w', encoding='utf-8') as f:
            json.dump(natija, f, ensure_ascii=False, indent=2)
        
        print("  'result.json' fayliga saqlandi")
        
        # Ekranda ko'rsatish
        print("\n" + "="*70)
        print(" YAKUNIY NATIJA:")
        print("="*70)
        print(json.dumps(natija, ensure_ascii=False, indent=2))
        
        print("\n" + "="*70)
        print(" TAHLIL MUVAFFAQIYATLI YAKUNLANDI !!!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n XATOLIK !!! : {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        telegram_client.disconnect()


if __name__ == '__main__':
    telegram_tahlil()