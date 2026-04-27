import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

def upload_imagem(file_bytes: bytes, filename: str) -> dict:
    resultado = cloudinary.uploader.upload(
        file_bytes,
        folder="bella_mizi/produtos",
        public_id=filename,
        overwrite=True,
        resource_type="image",
        transformation=[{"width": 800, "height": 800, "crop": "limit", "quality": "auto:good"}],
    )
    return {
        "url": resultado["secure_url"],
        "public_id": resultado["public_id"],
    }

def deletar_imagem(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id)