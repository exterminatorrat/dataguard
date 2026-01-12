"""
File Cleaner Module
Strips metadata from images and PDFs.
100% local processing - no external services.
"""

import io
from typing import Optional
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter


class FileCleaner:
    """Removes sensitive metadata from files"""
    
    @staticmethod
    def clean_image(file_bytes: bytes) -> bytes:
        """
        Remove EXIF and XMP metadata from images.
        
        Args:
            file_bytes: Raw image bytes
            
        Returns:
            Clean image bytes without metadata
        """
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(file_bytes))
            
            # Create a new image without metadata
            # Convert to RGB if necessary (handles RGBA, P, etc.)
            if image.mode not in ('RGB', 'L'):
                if image.mode == 'RGBA':
                    # Create white background for transparency
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[3] if len(image.split()) == 4 else None)
                    image = background
                else:
                    image = image.convert('RGB')
            
            # Save to bytes without metadata
            output = io.BytesIO()
            
            # Determine format (default to JPEG for compatibility)
            format_map = {
                'JPEG': 'JPEG',
                'JPG': 'JPEG', 
                'PNG': 'PNG',
                'GIF': 'GIF',
                'BMP': 'BMP',
                'WEBP': 'WEBP'
            }
            
            original_format = image.format if image.format else 'JPEG'
            save_format = format_map.get(original_format.upper(), 'JPEG')
            
            # Save without EXIF data
            if save_format == 'JPEG':
                image.save(output, format=save_format, quality=95, optimize=True)
            elif save_format == 'PNG':
                image.save(output, format=save_format, optimize=True)
            else:
                image.save(output, format=save_format)
            
            output.seek(0)
            return output.getvalue()
            
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
    
    @staticmethod
    def clean_pdf(file_bytes: bytes) -> bytes:
        """
        Remove metadata from PDF files.
        
        Args:
            file_bytes: Raw PDF bytes
            
        Returns:
            Clean PDF bytes without metadata
        """
        try:
            # Read PDF from bytes
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            pdf_writer = PdfWriter()
            
            # Copy all pages without metadata
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Remove metadata by not copying it
            # (PdfWriter creates fresh PDFs without old metadata)
            
            # Write to bytes
            output = io.BytesIO()
            pdf_writer.write(output)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    def clean_file(file_bytes: bytes, content_type: str) -> bytes:
        """
        Route file to appropriate cleaner based on content type.
        
        Args:
            file_bytes: Raw file bytes
            content_type: MIME type of the file
            
        Returns:
            Clean file bytes
        """
        content_type_lower = content_type.lower()
        
        # Image types
        if any(img_type in content_type_lower for img_type in ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']):
            return FileCleaner.clean_image(file_bytes)
        
        # PDF type
        elif 'pdf' in content_type_lower:
            return FileCleaner.clean_pdf(file_bytes)
        
        else:
            raise ValueError(f"Unsupported file type: {content_type}")


# Singleton instance
cleaner = FileCleaner()
