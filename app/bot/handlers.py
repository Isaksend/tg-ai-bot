import io
from aiogram import Router, types, F
from aiogram.filters import Command
from app.vision import vision_manager
from app.llm import llm_manager
from app.config import config

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветственное сообщение [cite: 49]"""
    await message.answer("Привет! Я твой локальный AI-ассистент. Я могу понимать текст и анализировать изображения.")


@router.message(Command("reset"))
async def cmd_reset(message: types.Message):
    """Сброс контекста диалога [cite: 51]"""
    llm_manager.reset_context(message.from_user.id)
    await message.answer("Контекст диалога успешно сброшен.")


@router.message(F.photo)
async def handle_photo(message: types.Message):
    """Обработка изображений и текста к ним [cite: 57-74]"""
    # 1. Получаем файл изображения
    photo = message.photo[-1]

    # Проверка размера [cite: 40, 62]
    if photo.file_size > config.MAX_IMAGE_MB * 1024 * 1024:
        return await message.answer(f"Файл слишком большой. Максимум {config.MAX_IMAGE_MB} МБ.")

    processing_msg = await message.answer("Анализирую изображение...")

    # 2. Скачиваем изображение в память [cite: 61]
    file_info = await message.bot.get_file(photo.file_id)
    photo_bytes = await message.bot.download_file(file_info.file_path)
    img_content = photo_bytes.read()

    # 3. Computer Vision: получаем описание [cite: 63-64, 85]
    image_description = await vision_manager.describe_image(img_content)

    # 4. Формируем промпт (описание картинки + текст пользователя) [cite: 72-73]
    user_text = message.caption if message.caption else "Что на этом изображении?"
    full_prompt = f"[Изображение: {image_description}]\nВопрос пользователя: {user_text}"

    # 5. LLM: получаем финальный ответ [cite: 65, 75]
    response = await llm_manager.get_response(message.from_user.id, full_prompt)

    await processing_msg.edit_text(response)


@router.message(F.text)
async def handle_text(message: types.Message):
    """Обработка обычных текстовых сообщений [cite: 52-56]"""
    response = await llm_manager.get_response(message.from_user.id, message.text)
    await message.answer(response)