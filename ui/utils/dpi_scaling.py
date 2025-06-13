from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QFontMetrics

def enable_dpi_scaling():
    """
    Enable DPI scaling for the application.
    """
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def get_dpi_scale():
    """
    Get the current DPI scale factor.
    
    Returns:
        float: The DPI scale factor
    """
    return QApplication.primaryScreen().logicalDotsPerInch() / 96.0

def scale_font(font, scale_factor):
    """
    Scale a font based on the DPI scale factor.
    
    Args:
        font (QFont): The font to scale
        scale_factor (float): The DPI scale factor
    
    Returns:
        QFont: The scaled font
    """
    new_font = QFont(font)
    new_font.setPointSizeF(font.pointSizeF() * scale_factor)
    return new_font

def scale_size(size, scale_factor):
    """
    Scale a size based on the DPI scale factor.
    
    Args:
        size (int): The size to scale
        scale_factor (float): The DPI scale factor
    
    Returns:
        int: The scaled size
    """
    return int(size * scale_factor)

def scale_point(point, scale_factor):
    """
    Scale a QPoint based on the DPI scale factor.
    
    Args:
        point (QPoint): The point to scale
        scale_factor (float): The DPI scale factor
    
    Returns:
        QPoint: The scaled point
    """
    return QPoint(int(point.x() * scale_factor), int(point.y() * scale_factor))

def get_scaled_font_metrics(font, scale_factor):
    """
    Get scaled font metrics based on the DPI scale factor.
    
    Args:
        font (QFont): The font to use
        scale_factor (float): The DPI scale factor
    
    Returns:
        QFontMetrics: The scaled font metrics
    """
    scaled_font = scale_font(font, scale_factor)
    return QFontMetrics(scaled_font)