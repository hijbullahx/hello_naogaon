import os
import uuid
from django.core.files.storage import FileSystemStorage
from django.utils.text import slugify


class SafeFileSystemStorage(FileSystemStorage):
    """
    Robust FileSystemStorage that prevents 500 errors in deployment:
    1. Sanitizes filenames: converts non-ASCII / Unicode / Bengali filenames
       and removes spaces/special characters to prevent UnicodeEncodeError
       and path errors on Linux/cPanel filesystems.
    2. Ensures the destination subfolder exists with proper permissions (0o755)
       before saving.
    3. Guarantees safe and unique filenames.
    """

    def get_available_name(self, name, max_length=None):
        dir_name, file_name = os.path.split(name)
        base_name, ext = os.path.splitext(file_name)

        ext = ext.lower().strip()
        # Clean extension: only allow alphanumeric extension
        ext = "".join(c for c in ext if c.isalnum() or c == ".")

        # Convert base_name to ASCII slug
        safe_base = slugify(base_name)
        if not safe_base:
            safe_base = f"file_{uuid.uuid4().hex[:8]}"
        else:
            safe_base = safe_base[:40]

        unique_suffix = uuid.uuid4().hex[:6]
        clean_name = f"{safe_base}_{unique_suffix}{ext}"
        new_name = os.path.join(dir_name, clean_name).replace("\\", "/")

        return super().get_available_name(new_name, max_length=max_length)

    def _save(self, name, content):
        full_path = self.path(name)
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, mode=0o755, exist_ok=True)
            except OSError:
                pass
        return super()._save(name, content)
