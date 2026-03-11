"""
Overlay window for region selection with red dashed border.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRegion


class OverlayWindow(QWidget):
    """Overlay window that shows capture region with red dashed border."""
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._setup_window()
        self._region = QRect(0, 0, 0, 0)
        self._dash_offset = 0
        self._animation_timer = QTimer()
        self._setup_animation()
        
    def _setup_window(self) -> None:
        """Configure overlay window properties."""
        # Make window transparent and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Make window transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Cover entire screen
        self.setGeometry(0, 0, 1, 1)  # Will be updated later
        
    def _setup_animation(self) -> None:
        """Setup animation for dashed border."""
        self._animation_timer.timeout.connect(self._update_dash_offset)
        self._animation_timer.start(50)  # Update every 50ms for smooth animation
        
    def _update_dash_offset(self) -> None:
        """Update dash offset for animated border."""
        self._dash_offset = (self._dash_offset + 2) % 15
        self.update()
        
    def set_region(self, region: QRect) -> None:
        """Set the capture region to display.
        
        Args:
            region: Rectangle defining the capture region
        """
        self._region = region
        
        # Update window geometry to cover entire screen
        screen_geometry = self.screen().geometry()
        self.setGeometry(screen_geometry)
        
        # Create mask to make only the border area visible
        self._update_window_mask()
        self.update()
        
    def _update_window_mask(self) -> None:
        """Update window mask to create transparent area inside border."""
        if self._region.isNull():
            # Show full overlay if no region
            self.clearMask()
            return
            
        # Create region that covers entire screen except the capture area
        screen_region = QRegion(self.rect())
        inner_region = QRegion(
            self._region.adjusted(2, 2, -2, -2)  # Slightly smaller to show border
        )
        mask_region = screen_region.subtracted(inner_region)
        self.setMask(mask_region)
        
    def paintEvent(self, event) -> None:
        """Paint the overlay with red dashed border and semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill entire screen with semi-transparent black (60% opacity)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 200))  # 60% opacity
        
        if not self._region.isNull():
            # Clear the capture area (make it fully transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(self._region, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            
            # Draw red dashed border
            pen = QPen(QColor(232, 17, 35))  # #E81123
            pen.setWidth(2)
            
            # Create dashed pattern: 10px solid, 5px blank
            dash_pattern = [10, 5]
            pen.setDashPattern(dash_pattern)
            pen.setDashOffset(self._dash_offset)
            
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Draw dashed rectangle
            painter.drawRect(self._region)
            
            # Draw corner handles (optional)
            self._draw_corner_handles(painter)
            
    def _draw_corner_handles(self, painter: QPainter) -> None:
        """Draw corner resize handles.
        
        Args:
            painter: QPainter instance
        """
        if self._region.isNull():
            return
            
        # Draw small squares at corners
        handle_size = 8
        half_handle = handle_size // 2
        
        corners = [
            self._region.topLeft(),      # Top-left
            self._region.topRight(),     # Top-right
            self._region.bottomLeft(),   # Bottom-left
            self._region.bottomRight()   # Bottom-right
        ]
        
        painter.setBrush(QBrush(QColor(232, 17, 35)))  # Red fill
        painter.setPen(QPen(QColor(255, 255, 255), 1))  # White border
        
        for corner in corners:
            handle_rect = QRect(
                corner.x() - half_handle,
                corner.y() - half_handle,
                handle_size,
                handle_size
            )
            painter.drawRect(handle_rect)
            
    def show_overlay(self) -> None:
        """Show the overlay window."""
        self.showFullScreen()
        
    def hide_overlay(self) -> None:
        """Hide the overlay window."""
        self.hide()
        
    def is_overlay_visible(self) -> bool:
        """Check if overlay is currently visible."""
        return self.isVisible()
        
    def update_region_from_screen(self, screen_width: int, screen_height: int, 
                                 region_type: str = "1") -> None:
        """Update region based on screen size and region type.
        
        Args:
            screen_width: Screen width
            screen_height: Screen height
            region_type: Region type ("1", "2", "4")
        """
        if region_type not in ["1", "2", "4"]:
            region_type = "1"
        

        if region_type == "1":
            width = screen_width // 4
            height = screen_height // 4
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            region = QRect(x, y, width, height)
        elif region_type == "2":
            width = screen_width // 2
            height = screen_height // 2
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            region = QRect(x, y, width, height)
        elif region_type == "4":
            region = QRect(0, 0, screen_width, screen_height)

        # if region_type == "4":
        #     region = QRect(0, 0, screen_width, screen_height)
        # elif region_type == "2":
        #     width = screen_width // 2
        #     height = screen_height // 2
        #     x = (screen_width - width) // 2
        #     y = (screen_height - height) // 2
        #     region = QRect(x, y, width, height)
        # elif region_type == "1/4":
        #     width = screen_width // 4
        #     height = screen_height // 4
        #     x = (screen_width - width) // 2
        #     y = (screen_height - height) // 2
        #     region = QRect(x, y, width, height)
        # else:
        #     # Default to full screen
        #     region = QRect(0, 0, screen_width, screen_height)
            
        self.set_region(region)
        
    def get_region(self) -> QRect:
        """Get the current capture region.
        
        Returns:
            Current capture region as QRect
        """
        return self._region
        
    def get_region_tuple(self) -> tuple:
        """Get the current capture region as tuple.
        
        Returns:
            Tuple of (left, top, width, height)
        """
        return (
            self._region.x(),
            self._region.y(),
            self._region.width(),
            self._region.height()
        )