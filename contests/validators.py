from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import imghdr
import os

@deconstructible
class FileValidator:
    allowed_extensions = ['png', 'svg', 'jpeg']
    allowed_mime_types = ['image/png', 'image/jpeg', 'image/svg+xml']

    def __call__(self, value):
        ext = os.path.splitext(value.name)[1][1:].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(f"Unsupported file extension: .{ext}. Allowed extensions are: {', '.join(self.allowed_extensions)}")

        # Check the mime type
        mime_type = value.file.content_type
        if mime_type not in self.allowed_mime_types:
            raise ValidationError(f"Unsupported file type: {mime_type}. Allowed types are: {', '.join(self.allowed_mime_types)}")

        # Additional check for PNG using imghdr
        if ext == 'png':
            value.file.seek(0)
            file_type = imghdr.what(value.file)
            if file_type != 'png':
                raise ValidationError("The uploaded PNG file seems to be corrupted or invalid.")
        
        # Additional check for JPEG using imghdr
        if ext == 'jpeg':
            value.file.seek(0)
            file_type = imghdr.what(value.file)
            if file_type != 'jpeg':
                raise ValidationError("The uploaded PNG file seems to be corrupted or invalid.")
