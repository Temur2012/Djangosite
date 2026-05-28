"""Seed database with sample content. Run: python manage.py shell < seed.py"""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Category, Tag, Post, Profile

# Superuser
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
    Profile.objects.get_or_create(user=admin, defaults={'bio': 'Sayt administratori'})
    print("✓ Admin yaratildi: admin / admin12345")

# Categories
cats_data = [
    ('Texnologiya', 'Yangi texnologiyalar va dasturlash'),
    ('Biznes', 'Tadbirkorlik va biznes maslahatlari'),
    ('Sayohat', 'Dunyo bo\'ylab sayohat hikoyalari'),
    ('Taom', 'Eng mazali retseptlar'),
    ('Sport', 'Sport yangiliklari va tahlillar'),
    ('Sanat', 'Madaniyat, kino, musiqa'),
]
for name, desc in cats_data:
    Category.objects.get_or_create(name=name, defaults={'description': desc})
print(f"✓ {Category.objects.count()} ta kategoriya")

# Tags
for t in ['Django', 'Python', 'JavaScript', 'AI', 'Startup', 'Hayot', 'Til', 'Kitob']:
    Tag.objects.get_or_create(name=t)
print(f"✓ {Tag.objects.count()} ta teg")

# Posts
admin = User.objects.get(username='admin')
tech = Category.objects.get(name='Texnologiya')
biz = Category.objects.get(name='Biznes')
sayohat = Category.objects.get(name='Sayohat')

posts_data = [
    {
        'title': 'Django bilan zamonaviy veb-saytlar yaratish',
        'category': tech,
        'excerpt': 'Django — Python uchun eng kuchli veb-freymvork. Uning yordamida tez va xavfsiz saytlar yaratish mumkin.',
        'body': """Django — bu Python tilida yozilgan ochiq kodli veb-freymvork. U 2005-yilda paydo bo'lgan va hozirgi kunda Instagram, Pinterest, Mozilla kabi yirik kompaniyalar tomonidan ishlatiladi.

Django'ning afzalliklari:
- Tez ishlab chiqish (rapid development)
- Xavfsizlik (SQL injection, XSS, CSRF himoyasi)
- Kuchli admin panel — avtomatik generatsiya qilinadi
- ORM — ma'lumotlar bazasi bilan ishlash oson
- Katta jamiyat va boy ekotizim

Sayt yaratishni boshlash uchun siz Python o'rnatasiz, keyin `pip install django` buyrug'i bilan Django'ni o'rnatasiz. So'ngra `django-admin startproject mysite` orqali yangi loyiha yaratasiz.

Bu maqolada biz Django arxitekturasini, MVT (Model-View-Template) paradigmasini va eng yaxshi amaliyotlarni ko'rib chiqamiz.""",
        'featured': True,
    },
    {
        'title': "Startup'ni qanday boshlash kerak: 10 ta amaliy maslahat",
        'category': biz,
        'excerpt': "Yangi biznesni boshlash qo'rqinchli, lekin to'g'ri yondashuv bilan har kim muvaffaqiyatga erisha oladi.",
        'body': """Startup yaratish — bu kichik bir g'oyadan boshlanib, dunyoni o'zgartirishi mumkin bo'lgan jarayon. Lekin har bir tadbirkor xato qilishi mumkin.

Mana 10 ta muhim maslahat:

1. Muammoni hal qiling, mahsulot yaratmang
2. Mijozlar bilan gaplashing — ko'p
3. MVP yarating, perfekt mahsulot emas
4. Jamoa muhim — yolg'iz boshlamang
5. Pulingizni saqlang — har dollar muhim
6. Marketing kodlash bilan baravar muhim
7. Rad etishdan qo'rqmang
8. Sekin o'sing, lekin barqaror
9. Mentor toping
10. Hech qachon taslim bo'lmang

Eng muhimi — boshlang. Mukammal payt hech qachon kelmaydi.""",
        'featured': True,
    },
    {
        'title': "Samarqand: O'zbekistonning marvaridi",
        'category': sayohat,
        'excerpt': "Buyuk Ipak Yo'li bo'ylab eng go'zal shahar — Samarqand bilan tanishuv.",
        'body': """Samarqand — bu nafaqat shahar, balki tarixning o'zi. 2750 yildan ortiq yoshga ega bo'lgan bu shahar Amir Temur saltanatining markazi bo'lgan.

Sayohat paytida ko'rishingiz kerak bo'lgan joylar:

- Registon maydoni — uchta madrasa bilan o'ralgan
- Go'ri Amir — Amir Temur maqbarasi
- Bibi-Xonim masjidi
- Shohizinda nekropoli
- Ulug'bek rasadxonasi

Eng yaxshi vaqt — bahor (aprel-may) yoki kuz (sentyabr-oktyabr). Yoz juda issiq bo'ladi.

Mahalliy taomlardan plov, manti, somsa va shashlikni albatta tatib ko'ring!""",
        'featured': True,
    },
    {
        'title': "Python'da Async dasturlash: asyncio kirish",
        'category': tech,
        'excerpt': "Asinxron dasturlash bilan tezroq va samaraliroq dasturlar yarating.",
        'body': "Async dasturlash zamonaviy Python'ning eng kuchli xususiyatlaridan biri. asyncio kutubxonasi yordamida siz minglab so'rovlarni parallel bajara olasiz...",
    },
    {
        'title': "Sun'iy intellekt: kelajak shu yerda",
        'category': tech,
        'excerpt': "AI dunyoni o'zgartirmoqda. Lekin biz nimaga tayyor bo'lishimiz kerak?",
        'body': "GPT, Claude, Gemini — bu nomlar har kuni eshitiladi. Sun'iy intellekt endi fantastika emas, balki real vosita...",
    },
    {
        'title': "Eng yaxshi 5 ta Python kutubxonasi 2026 yilda",
        'category': tech,
        'excerpt': "Har bir dasturchi bilishi kerak bo'lgan kutubxonalar ro'yxati.",
        'body': "1. FastAPI — yuqori unumdorlikdagi API uchun\n2. Polars — Pandas'dan tezroq\n3. Pydantic — ma'lumotlarni validatsiya qilish\n4. Rich — chiroyli terminal chiqishlari\n5. LangChain — LLM ilovalar uchun",
    },
]

for data in posts_data:
    if not Post.objects.filter(title=data['title']).exists():
        post = Post.objects.create(author=admin, **data)
        # Add random tags
        post.tags.set(Tag.objects.all()[:3])

print(f"✓ {Post.objects.count()} ta maqola")
print("\n=== Tayyor! ===")
print("URL: http://localhost:8000")
print("Admin: http://localhost:8000/admin (admin / admin12345)")
