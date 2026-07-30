import io
import zipfile
from app.models.scaffold import ScaffoldResponse

class ZipService:
    """Service responsible for compressing generated scaffold files into a downloadable ZIP archive."""

    @staticmethod
    def create_zip_archive(scaffold: ScaffoldResponse) -> io.BytesIO:
        """Takes a ScaffoldResponse and returns a BytesIO buffer containing the compressed ZIP file."""
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            for file_item in scaffold.files:
                # Ensure clean relative paths inside the zip archive
                clean_path = file_item.path.lstrip("/").lstrip("\\")
                zip_file.writestr(clean_path, file_item.content)

        zip_buffer.seek(0)
        return zip_buffer
