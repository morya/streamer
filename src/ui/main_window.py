"""
Main window implementation for the screen streaming application.
"""

from atexit import register
import sys

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtWidgets import QLabel, QPushButton, QComboBox, QLineEdit
from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt, Signal, QTimer, QRect
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen

from .overlay_window import OverlayWindow


class MainWindow(QMainWindow):
    """Main application window with streaming controls."""
    
    # Signals
    region_changed = Signal(str)  # Region size changed
    bitrate_changed = Signal(str)  # Bitrate changed
    protocol_changed = Signal(str)  # Protocol changed (SRT/RTMP)
    streaming_toggled = Signal(bool, str)  # Streaming started/stopped with URL

    regions = [
        '1',   # 1/4
        '2',   # 2/4
        '4',   # 4/4
    ]
    
    def __init__(self) -> None:
        super().__init__()
        self._current_region_idx = 0
        self._current_region = self.regions[self._current_region_idx]
        self._screen_width = 1920
        self._screen_height = 1080
        self._overlay = None
        self._dragging = False
        self._drag_position = None
        self._setup_ui()
        self._connect_signals()
        self._setup_overlay()
        self._position_window()
        
    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        self.setWindowTitle("Screen Streamer")
        self.setFixedSize(400, 150)
        
        # Set window flags for always on top
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        
        # Set window attributes for acrylic/glass effect
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create central widget with custom styling
        central_widget = QWidget()
        central_widget.setObjectName("MainWindow")
        self.setCentralWidget(central_widget)
        
        # Apply stylesheet for acrylic/glass effect and dark theme
        self._apply_stylesheet()
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(8)
        
        # Top row: Region controls
        top_row = QHBoxLayout()
        
        # Region indicator
        self.region_label = QLabel("Full Screen (1920x1080)")
        
        if sys.platform == "darwin":
            fontname = ".AppleSystemUIFont"
        elif sys.platform == "win32":
            fontname = "Segoe UI"
        else:
            fontname = "Arial"
        self.region_label.setFont(QFont(fontname, 10, QFont.Weight.Normal))
        self.region_label.setStyleSheet("color: #FFFFFF;")
        top_row.addWidget(self.region_label)
        
        # Region minus button
        self.region_minus_btn = QPushButton("-")
        self.region_minus_btn.setFixedSize(32, 32)
        self.region_minus_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #444444;
                border-radius: 4px;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 200);
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 200);
            }
        """)
        top_row.addWidget(self.region_minus_btn)
        
        # Region plus button
        self.region_plus_btn = QPushButton("+")
        self.region_plus_btn.setFixedSize(32, 32)
        self.region_plus_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #444444;
                border-radius: 4px;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 200);
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: rgba(20, 20, 20, 200);
            }
        """)
        top_row.addWidget(self.region_plus_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #444444;")
        separator.setFixedWidth(1)
        top_row.addWidget(separator)
        
        # Bitrate selector
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["1Mbps", "2Mbps", "5Mbps", "8Mbps", "Custom"])
        self.bitrate_combo.setCurrentText("2Mbps")
        self.bitrate_combo.setFixedWidth(100)
        self.bitrate_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #444444;
                border-radius: 4px;
                color: #FFFFFF;
                padding: 4px;
                padding-left: 8px;
            }
            QComboBox:hover {
                border-color: #555555;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(30, 30, 30, 220);
                border: 1px solid #444444;
                color: #FFFFFF;
                selection-background-color: #0078D4;
            }
        """)
        top_row.addWidget(self.bitrate_combo)
        
        main_layout.addLayout(top_row)
        
        # Middle row: Protocol and URL
        middle_row = QHBoxLayout()
        
        # Protocol selector (SRT/RTMP toggle)
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["SRT", "RTMP"])
        self.protocol_combo.setFixedWidth(80)
        self.protocol_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #444444;
                border-radius: 4px;
                color: #FFFFFF;
                padding: 4px;
                padding-left: 8px;
            }
            QComboBox:hover {
                border-color: #555555;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFFFF;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(30, 30, 30, 220);
                border: 1px solid #444444;
                color: #FFFFFF;
                selection-background-color: #0078D4;
            }
        """)
        middle_row.addWidget(self.protocol_combo)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("rtmp:// 或 srt://...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #444444;
                border-radius: 4px;
                color: #FFFFFF;
                padding: 6px;
                selection-background-color: #0078D4;
            }
            QLineEdit:hover {
                border-color: #555555;
            }
            QLineEdit:focus {
                border-color: #0078D4;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        middle_row.addWidget(self.url_input)
        
        main_layout.addLayout(middle_row)
        
        # Bottom row: Start/Stop button
        bottom_row = QHBoxLayout()
        
        self.stream_btn = QPushButton("开始推流")
        self.stream_btn.setFixedHeight(36)
        self.stream_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B6A4B;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #0D7A55;
            }
            QPushButton:pressed {
                background-color: #095A3B;
            }
        """)
        self.exit_btn = QPushButton("退出")
        self.exit_btn.setFixedHeight(36)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4D4F;
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #FF6B6B;
            }
            QPushButton:pressed {
                background-color: #FF3B3B;
            }
        """)
        bottom_row.addWidget(self.stream_btn)
        bottom_row.addWidget(self.exit_btn)
        # self.exit_btn.clicked.connect(self.close)
        
        main_layout.addLayout(bottom_row)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
    def _connect_signals(self) -> None:
        """Connect UI signals to slots."""
        self.region_minus_btn.clicked.connect(self._on_region_minus)
        self.region_plus_btn.clicked.connect(self._on_region_plus)
        self.bitrate_combo.currentTextChanged.connect(self._on_bitrate_changed)
        self.protocol_combo.currentTextChanged.connect(self._on_protocol_changed)
        self.stream_btn.clicked.connect(self._on_stream_toggle)
        
        # Connect configuration change signals
        self.region_minus_btn.clicked.connect(self._on_config_changed)
        self.region_plus_btn.clicked.connect(self._on_config_changed)
        self.bitrate_combo.currentTextChanged.connect(self._on_config_changed)
        self.protocol_combo.currentTextChanged.connect(self._on_config_changed)
        self.url_input.textChanged.connect(self._on_config_changed)
        
    def _on_region_minus(self) -> None:
        """Handle region minus button click."""
        self._current_region_idx -= 1
        if self._current_region_idx < 0:
            self._current_region_idx = 0
        self._current_region = self.regions[self._current_region_idx]
            
        self._update_region_display()
        self._update_overlay_region()
        self.region_changed.emit(self._current_region)
        
    def _on_region_plus(self) -> None:
        """Handle region plus button click."""
        self._current_region_idx += 1
        if self._current_region_idx >= len(self.regions):
            self._current_region_idx = len(self.regions) - 1
        self._current_region = self.regions[self._current_region_idx]
            
        self._update_region_display()
        self._update_overlay_region()
        self.region_changed.emit(self._current_region)
        
    def _on_bitrate_changed(self, bitrate: str) -> None:
        """Handle bitrate selection change."""
        self.bitrate_changed.emit(bitrate)
        
    def _on_protocol_changed(self, protocol: str) -> None:
        """Handle protocol selection change."""
        self.protocol_changed.emit(protocol)
        
    def _on_config_changed(self) -> None:
        """Handle configuration changes and save to config manager."""
        if hasattr(self, '_config_manager') and self._config_manager:
            self.save_configuration()
        
    def _on_stream_toggle(self) -> None:
        """Handle start/stop streaming button click."""
        url = self.url_input.text().strip()
        if not url:
            self.update_status("Error: Please enter a stream URL", is_error=True)
            return
            
        if self.stream_btn.text() == "Start Streaming":
            self.stream_btn.setText("Stop Streaming")
            self.stream_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E81123;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #F82133;
                }
                QPushButton:pressed {
                    background-color: #D80113;
                }
            """)
            self.streaming_toggled.emit(True, url)
        else:
            self.stream_btn.setText("Start Streaming")
            self.stream_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B6A4B;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #0D7A55;
                }
                QPushButton:pressed {
                    background-color: #095A3B;
                }
            """)
            self.streaming_toggled.emit(False, url)
            
    def update_region_label(self, region_info: str) -> None:
        """Update the region display label."""
        self.region_label.setText(region_info)
        
    def update_status(self, status: str, is_error: bool = False) -> None:
        """Update the status label."""
        self.status_label.setText(status)
        if is_error:
            self.status_label.setStyleSheet("color: #E81123; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #CCCCCC;")
            
    def update_streaming_status(self, is_streaming: bool, fps: int = 0, bitrate: str = "") -> None:
        """Update streaming status indicator."""
        if is_streaming:
            status_text = f"▶ 推流中 {fps}fps | {bitrate}"
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet("color: #0B6A4B; font-weight: bold;")
        else:
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: #CCCCCC;")
            
    def _apply_stylesheet(self) -> None:
        """Apply the main stylesheet for acrylic/glass effect."""
        stylesheet = """
        QMainWindow {
            background-color: rgba(30, 30, 30, 204);  /* #1E1E1E with 80% opacity */
            border: 1px solid rgba(68, 68, 68, 100);
            border-radius: 8px;
        }
        
        QWidget#MainWindow {
            background-color: transparent;
        }
        
        QLabel {
            color: #FFFFFF;
        }
        
        QLabel#StatusLabel {
            color: #CCCCCC;
            font-size: 11px;
        }
        """
        
        self.setStyleSheet(stylesheet)
        
    def paintEvent(self, event):
        """Override paint event for custom background with acrylic effect."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw rounded rectangle with acrylic effect
        brush = QBrush(QColor(30, 30, 30, 204))  # #1E1E1E with 80% opacity
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 8, 8)
        
        # Draw border
        pen = QPen(QColor(68, 68, 68, 100))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 8, 8)
        
    def _setup_overlay(self) -> None:
        """Setup the overlay window for region selection."""
        self._overlay = OverlayWindow()
        
    def _update_overlay_region(self) -> None:
        """Update the overlay region based on current settings."""
        if self._overlay:
            self._overlay.update_region_from_screen(
                self._screen_width,
                self._screen_height,
                self._current_region
            )

    def _update_region_display(self) -> None:
        """Update the region display label."""
        label = f'{self._current_region}/4'
        self.region_label.setText(label)
        
    def show_overlay(self) -> None:
        """Show the region selection overlay."""
        if self._overlay:
            self._update_overlay_region()
            self._overlay.show_overlay()
            
    def hide_overlay(self) -> None:
        """Hide the region selection overlay."""
        if self._overlay:
            self._overlay.hide_overlay()
            
    def set_screen_resolution(self, width: int, height: int) -> None:
        """Set screen resolution for region calculations.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self._screen_width = width
        self._screen_height = height
        self._update_region_display()
        self._update_overlay_region()
        
    def get_capture_region(self) -> tuple:
        """Get the current capture region as tuple.
        
        Returns:
            Tuple of (left, top, width, height)
        """
        if self._overlay:
            return self._overlay.get_region_tuple()
        else:
            # Fallback to calculated region
            if self._current_region == "4":
                return (0, 0, self._screen_width, self._screen_height)
            elif self._current_region == "2":
                return (0, 0, self._screen_width // 2, self._screen_height // 2)
            else:
                return (0, 0, self._screen_width // 4, self._screen_height // 4)

            if self._current_region == "full":
                return (0, 0, self._screen_width, self._screen_height)
            elif self._current_region == "1/2":
                width = self._screen_width // 2
                height = self._screen_height // 2
                x = (self._screen_width - width) // 2
                y = (self._screen_height - height) // 2
                return (x, y, width, height)
            else:  # "1/4"
                width = self._screen_width // 4
                height = self._screen_height // 4
                x = (self._screen_width - width) // 2
                y = (self._screen_height - height) // 2
                return (x, y, width, height)
                
    def _position_window(self) -> None:
        """Position window at top center of screen."""
        screen_geometry = self.screen().geometry()
        window_width = self.width()
        window_height = self.height()
        
        x = (screen_geometry.width() - window_width) // 2
        y = 10  # 10 pixels from top
        
        self.move(x, y)
        
    def mousePressEvent(self, event):
        """Handle mouse press event for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move event for window dragging."""
        if self._dragging and self._drag_position:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release event for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._drag_position = None
            event.accept()
            
    def load_configuration(self, config_manager) -> None:
        """Load configuration into UI controls.
        
        Args:
            config_manager: ConfigManager instance
        """
        # Load region setting
        region = config_manager.get_capture_region()
        if region in ["1/4", "1/2", "full"]:
            self._current_region = region
            self._update_region_display()
            
        # Load bitrate setting
        bitrate = config_manager.get_bitrate()
        if bitrate in ["1Mbps", "2Mbps", "5Mbps", "8Mbps", "Custom"]:
            index = self.bitrate_combo.findText(bitrate)
            if index >= 0:
                self.bitrate_combo.setCurrentIndex(index)
                
        # Load protocol setting
        protocol = config_manager.get_protocol()
        if protocol in ["srt", "rtmp"]:
            protocol_text = protocol.upper()
            index = self.protocol_combo.findText(protocol_text)
            if index >= 0:
                self.protocol_combo.setCurrentIndex(index)
                
        # Load stream URL
        stream_url = config_manager.get_stream_url()
        if stream_url:
            self.url_input.setText(stream_url)
            
        # Load window position
        window_pos = config_manager.get_window_position()
        if len(window_pos) == 2:
            self.move(window_pos[0], window_pos[1])
            
        # Store config manager reference
        self._config_manager = config_manager
        
    def save_configuration(self, config_manager=None) -> None:
        """Save UI configuration.
        
        Args:
            config_manager: Optional ConfigManager instance (uses stored if None)
        """
        if config_manager is None:
            config_manager = getattr(self, '_config_manager', None)
            
        if not config_manager:
            return
            
        # Save region setting
        config_manager.set_capture_region(self._current_region)
        
        # Save bitrate setting
        bitrate = self.bitrate_combo.currentText()
        config_manager.set_bitrate(bitrate)
        
        # Save protocol setting
        protocol = self.protocol_combo.currentText().lower()
        config_manager.set_protocol(protocol)
        
        # Save stream URL
        stream_url = self.url_input.text().strip()
        config_manager.set_stream_url(stream_url)
        
        # Save window position
        window_pos = self.pos()
        config_manager.set_window_position(window_pos.x(), window_pos.y())
        
        # Save configuration
        config_manager.save()