import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ==================== SOZLAMALAR ====================
TOKEN = "8927695742:AAF-FnHMtsztpgLQhLX5-CLNTT7kNSnkqCc"  # @BotFather bergan token
ADMIN_ID =980170907            # O'zingizning Telegram ID raqamingiz
# ====================================================

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- DATABASE (SQLite) ---
def init_db():
    conn = sqlite3.connect("phone_shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price TEXT,
            description TEXT,
            photo TEXT
        )
    """)
    
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN photo TEXT")
    except sqlite3.OperationalError:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            user_id INTEGER,
            product_id INTEGER
        )
    """)
    conn.commit()
    
    # Bazada mahsulotlar kam bo'lsa, 50 taga yaqin mashhur telefonlarni rasmlari bilan qo'shamiz
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] < 10:
        # Ishonchli ochiq rasm havolalari va telefonlar ro'yxati
        phones = [
            ("iPhone 16 Pro Max", "$1350", "256GB, Desert Titanium, Apple A18 Pro", "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600"),
            ("iPhone 16 Pro", "$1200", "128GB, Natural Titanium, Apple A18 Pro", "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600"),
            ("iPhone 16", "$950", "128GB, Ultramarine, A18 chip", "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=600"),
            ("iPhone 15 Pro Max", "$1100", "256GB, Titanium Blue", "https://images.unsplash.com/photo-1695048065448-fbd085523a85?w=600"),
            ("iPhone 15 Pro", "$980", "128GB, Black Titanium", "https://images.unsplash.com/photo-1695048065448-fbd085523a85?w=600"),
            ("iPhone 14 Pro Max", "$900", "256GB, Deep Purple", "https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=600"),
            ("iPhone 13", "$650", "128GB, Midnight, A15 Bionic", "https://images.unsplash.com/photo-1591337676887-a217a6970a8a?w=600"),
            
            ("Samsung Galaxy S25 Ultra", "$1300", "512GB, Titanium Gray, Snapdragon 8 Elite", "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600"),
            ("Samsung Galaxy S25+", "$1050", "256GB, Onyx Black", "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600"),
            ("Samsung Galaxy S24 Ultra", "$1150", "256GB, Titanium Black", "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=600"),
            ("Samsung Galaxy S24+", "$900", "256GB, Marble Gray", "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600"),
            ("Samsung Galaxy S24", "$750", "128GB, Amber Yellow", "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600"),
            ("Samsung Galaxy A55", "$380", "8/256GB, Awesome Iceblue", "https://images.unsplash.com/photo-1546054454-aa26fc2b73d0?w=600"),
            ("Samsung Galaxy A35", "$300", "8/128GB, Awesome Navy", "https://images.unsplash.com/photo-1546054454-aa26fc2b73d0?w=600"),
            ("Samsung Galaxy Z Fold 6", "$1600", "512GB, Silver Shadow", "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600"),
            ("Samsung Galaxy Z Flip 6", "$1000", "256GB, Mint", "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600"),

            ("Xiaomi 14 Ultra", "$950", "16/512GB, Black, Leica camera", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600"),
            ("Xiaomi 14 Pro", "$800", "12/256GB, White", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600"),
            ("Xiaomi 14", "$700", "8/256GB, Green", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600"),
            ("Redmi Note 13 Pro+", "$350", "12/512GB, Midnight Black", "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600"),
            ("Redmi Note 13 Pro", "$280", "8/256GB, Forest Green", "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600"),
            ("Redmi Note 13", "$210", "6/128GB, Ice Blue", "https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=600"),
            ("POCO X6 Pro", "$320", "12/512GB, Yellow (Vegan Leather)", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600"),
            ("POCO F6 Pro", "$450", "12/512GB, Black", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600"),

            ("Google Pixel 9 Pro XL", "$1050", "256GB, Obsidian, Tensor G4", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600"),
            ("Google Pixel 9 Pro", "$950", "128GB, Porcelain", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600"),
            ("Google Pixel 8a", "$450", "128GB, Bay", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600"),
            
            ("OnePlus 12", "$750", "16/512GB, Flowy Emerald", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600"),
            ("Honor Magic 6 Pro", "$850", "12/512GB, Epic Green", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600"),
            ("Huawei Pura 70 Ultra", "$1100", "16/512GB, Green", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600")
        ]
        cursor.executemany("INSERT INTO products (name, price, description, photo) VALUES (?, ?, ?, ?)", phones)
        conn.commit()
    conn.close()

init_db()

# --- HOLATLAR (FSM) ---
class OrderState(StatesGroup):
    name = State()
    phone = State()
    address = State()

class AddProductState(StatesGroup):
    name = State()
    price = State()
    desc = State()
    photo = State()

# --- MENYULAR ---
def main_menu(user_id):
    buttons = [
        [InlineKeyboardButton(text="📱 Telefonlar katalogi", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Savatcha", callback_data="cart")],
        [InlineKeyboardButton(text="📞 Biz bilan bog'lanish", callback_data="contact")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([InlineKeyboardButton(text="⚙️ Admin Panel (Telefon qo'shish)", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- HANDLERLAR ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, **{message.from_user.first_name}**!\n"
        "Telefon do'konimiz botiga xush kelibsiz. Kerakli bo'limni tanlang:",
        reply_markup=main_menu(message.from_user.id),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "main_menu")
async def back_main_menu(callback: types.CallbackQuery):
    await callback.message.answer("Bosh menyu:", reply_markup=main_menu(callback.from_user.id))
    await callback.message.delete()
    await callback.answer()

# --- KATALOG (Rasmli ko'rinish) ---
@dp.callback_query(F.data == "catalog")
async def show_catalog(callback: types.CallbackQuery):
    conn = sqlite3.connect("phone_shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, description, photo FROM products")
    products = cursor.fetchall()
    conn.close()

    if not products:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="main_menu")]])
        await callback.message.answer("Hozircha katalogda telefonlar mavjud emas.", reply_markup=kb)
        await callback.message.delete()
        await callback.answer()
        return

    await callback.message.answer("📱 **Mavjud barcha telefonlar katalogi:**")
    
    for prod in products:
        p_id, name, price, desc, photo = prod
        caption = f"📱 <b>{name}</b>\n\n💵 <b>Narxi:</b> {price}\n📝 <b>Tavsifi:</b> {desc}"
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Savatchaga qo'shish", callback_data=f"addcart_{p_id}")]
        ])
        
        try:
            if photo:
                await callback.message.answer_photo(photo=photo, caption=caption, reply_markup=kb, parse_mode="HTML")
            else:
                await callback.message.answer(text=caption, reply_markup=kb, parse_mode="HTML")
        except Exception as e:
            print(f"Rasm yuborishda xatolik: {e}")

    back_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="main_menu")]])
    await callback.message.answer("Boshqa bo'limga o'tish uchun pastdagi tugmani bosing:", reply_markup=back_kb)
    await callback.message.delete()
    await callback.answer()

# --- SAVATCHA ---
@dp.callback_query(F.data.startswith("addcart_"))
async def add_to_cart(callback: types.CallbackQuery):
    prod_id = int(callback.data.split("_")[1])
    conn = sqlite3.connect("phone_shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cart VALUES (?, ?)", (callback.from_user.id, prod_id))
    conn.commit()
    conn.close()
    await callback.answer("✅ Mahsulot savatchaga qo'shildi!", show_alert=True)

@dp.callback_query(F.data == "cart")
async def show_cart(callback: types.CallbackQuery):
    conn = sqlite3.connect("phone_shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.name, products.price 
        FROM cart JOIN products ON cart.product_id = products.id 
        WHERE cart.user_id = ?
    """, (callback.from_user.id,))
    items = cursor.fetchall()
    conn.close()

    if not items:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="main_menu")]])
        await callback.message.answer("🛒 Savatchangiz bo'sh.", reply_markup=kb)
        await callback.message.delete()
        await callback.answer()
        return

    text = "🛒 **Savatchangizdagi telefonlar:**\n\n"
    for idx, item in enumerate(items, 1):
        text += f"{idx}. {item[0]} — {item[1]}\n"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Buyurtma berish", callback_data="checkout")],
        [InlineKeyboardButton(text="🗑 Savatchani tozalash", callback_data="clear_cart")],
        [InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="main_menu")]
    ])
    await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
    await callback.message.delete()
    await callback.answer()

@dp.callback_query(F.data == "clear_cart")
async def clear_cart(callback: types.CallbackQuery):
    conn = sqlite3.connect("phone_shop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (callback.from_user.id,))
    conn.commit()
    conn.close()
    await callback.answer("Savatcha tozalandi!")
    await show_cart(callback)

# --- BUYURTMA RASMIYLASHTIRISH (FSM) ---
@dp.callback_query(F.data == "checkout")
async def start_checkout(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Buyurtma berish uchun Ism va Familiyangizni kiriting:")
    await state.set_state(OrderState.name)
    await callback.answer()

@dp.message(OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Telefon raqamingizni kiriting (masalan: +998901234567):")
    await state.set_state(OrderState.phone)

@dp.message(OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Yetkazib berish manzilini kiriting:")
    await state.set_state(OrderState.address)

@dp.message(OrderState.address)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    
    conn = sqlite3.connect("phone_shop.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.name, products.price 
        FROM cart JOIN products ON cart.product_id = products.id 
        WHERE cart.user_id = ?
    """, (message.from_user.id,))
    items = cursor.fetchall()

    products_text = ""
    for item in items:
        products_text += f"• {item[0]} ({item[1]})\n"

    admin_msg = (
        f"🚀 **YANGI BUYURTMA!**\n\n"
        f"👤 **Mijoz:** {data['name']}\n"
        f"📞 **Tel:** {data['phone']}\n"
        f"📍 **Manzil:** {data['address']}\n"
        f"🔗 **Username:** @{message.from_user.username}\n\n"
        f"📦 **Xarid qilingan telefonlar:**\n{products_text}"
    )

    try:
        await bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Xatolik admin xabarida: {e}")

    cursor.execute("DELETE FROM cart WHERE user_id = ?", (message.from_user.id,))
    conn.commit()
    conn.close()

    await message.answer("Rahmat! Buyurtmangiz qabul qilindi. Operator siz bilan tez orada bog'lanadi. 🎉", reply_markup=main_menu(message.from_user.id))
    await state.clear()

# --- ADMIN PANEL ---
@dp.callback_query(F.data == "admin_panel")
async def admin_panel(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return
    await callback.message.answer("Yangi telefon nomini kiriting:")
    await state.set_state(AddProductState.name)
    await callback.answer()

@dp.message(AddProductState.name)
async def add_prod_name(message: types.Message, state: FSMContext):
    await state.update_data(p_name=message.text)
    await message.answer("Telefon narxini kiriting (masalan: $1300):")
    await state.set_state(AddProductState.price)

@dp.message(AddProductState.price)
async def add_prod_price(message: types.Message, state: FSMContext):
    await state.update_data(p_price=message.text)
    await message.answer("Telefon tavsifini kiriting:")
    await state.set_state(AddProductState.desc)

@dp.message(AddProductState.desc)
async def add_prod_desc(message: types.Message, state: FSMContext):
    await state.update_data(p_desc=message.text)
    await message.answer("Endi telefonning **rasmini** yuboring:")
    await state.set_state(AddProductState.photo)

@dp.message(AddProductState.photo, F.photo)
async def add_prod_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    
    conn = sqlite3.connect("phone_shop.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, description, photo) VALUES (?, ?, ?, ?)", 
                   (data['p_name'], data['p_price'], data['p_desc'], photo_id))
    conn.commit()
    conn.close()

    await message.answer("✅ Yangi telefon katalogga qo'shildi!", reply_markup=main_menu(message.from_user.id))
    await state.clear()

@dp.message(AddProductState.photo)
async def wrong_photo_type(message: types.Message):
    await message.answer("Iltimos, rasm yuboring:")

# --- ALOQA BO'LIMI ---
@dp.callback_query(F.data == "contact")
async def show_contact(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Bosh menyu", callback_data="main_menu")]])
    await callback.message.answer("📞 **Biz bilan bog'lanish:**\n\nTel: +998 90 123 45 67\nManzil: Toshkent sh., Chilonzor tumani.", reply_markup=kb, parse_mode="Markdown")
    await callback.message.delete()
    await callback.answer()

# --- ISHGA TUSHIRISH ---
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())