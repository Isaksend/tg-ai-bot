import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import io
import logging


class VisionManager:
    def __init__(self):
        # Загрузка модели и процессора (локально)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        ).to(self.device)
        logging.info(f"Vision model loaded on {self.device}")

    async def describe_image(self, image_bytes: bytes) -> str:
        """Генерирует текстовое описание изображения [cite: 64]"""
        try:
            # Преобразование байтов в объект PIL
            raw_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Подготовка входных данных
            inputs = self.processor(raw_image, return_tensors="pt").to(self.device)

            # Генерация текста
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)

            return caption
        except Exception as e:
            logging.error(f"Error in vision pipeline: {e}")
            return "Ошибка при анализе изображения."