import sys
import os
import ffmpeg
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup, 
                             QFileDialog, QMessageBox, QFrame, QProgressBar, QDialog)
from PyQt5.QtCore import Qt, QMimeData, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QIcon, QColor, QPalette

class FileExistsDialog(QDialog):
    """Custom dialog for when output file already exists"""
    
    OVERWRITE = 0
    RENAME = 1
    SKIP = 2
    
    def __init__(self, parent=None, filename=""):
        super().__init__(parent)
        self.setWindowTitle("File Already Exists! 📁")
        self.setMinimumWidth(500)
        self.result_action = self.SKIP  # Default action
        
        # Set up the layout
        layout = QVBoxLayout()
        
        # Message
        message = QLabel(f"<b>{os.path.basename(filename)}</b> already exists!")
        message.setStyleSheet("font-size: 14px; color: #404080;")
        layout.addWidget(message)
        
        question = QLabel("What would you like to do?")
        question.setStyleSheet("font-size: 14px; color: #404080;")
        layout.addWidget(question)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        overwrite_btn = QPushButton("Overwrite ✍️")
        overwrite_btn.setStyleSheet("""
            background-color: #ff7070;
            color: white;
            border-radius: 10px;
            padding: 8px 15px;
            font-weight: bold;
            min-height: 30px;
            font-size: 13px;
        """)
        overwrite_btn.clicked.connect(self.overwrite)
        
        rename_btn = QPushButton("Auto Rename 🏷️")
        rename_btn.setStyleSheet("""
            background-color: #70a0ff;
            color: white;
            border-radius: 10px;
            padding: 8px 15px;
            font-weight: bold;
            min-height: 30px;
            font-size: 13px;
        """)
        rename_btn.clicked.connect(self.rename)
        
        skip_btn = QPushButton("Skip ⏭️")
        skip_btn.setStyleSheet("""
            background-color: #70b070;
            color: white;
            border-radius: 10px;
            padding: 8px 15px;
            font-weight: bold;
            min-height: 30px;
            font-size: 13px;
        """)
        skip_btn.clicked.connect(self.skip)
        
        button_layout.addWidget(overwrite_btn)
        button_layout.addWidget(rename_btn)
        button_layout.addWidget(skip_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f5ff;
            }
        """)
    
    def overwrite(self):
        self.result_action = self.OVERWRITE
        self.accept()
    
    def rename(self):
        self.result_action = self.RENAME
        self.accept()
    
    def skip(self):
        self.result_action = self.SKIP
        self.accept()

class ConversionProgressDialog(QDialog):
    """Custom progress dialog for conversion"""
    
    def __init__(self, parent=None, input_file="", output_format=""):
        super().__init__(parent)
        self.setWindowTitle("Converting... 🔄")
        self.setMinimumWidth(450)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setModal(True)
        
        # Setup layout
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Working on your conversion!")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #404080;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Message
        message = QLabel(f"Converting {os.path.basename(input_file)} to {output_format.upper()}...")
        message.setStyleSheet("font-size: 14px; color: #404080; margin: 10px;")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Progress animation (indeterminate)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #c0c0ff;
                border-radius: 10px;
                background-color: #e0e8ff;
                height: 20px;
                text-align: center;
                margin: 10px;
            }
            QProgressBar::chunk {
                background-color: #8080ff;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Please wait message
        wait = QLabel("Please wait... This might take a moment depending on the file size.")
        wait.setStyleSheet("font-size: 12px; color: #606080; font-style: italic;")
        wait.setAlignment(Qt.AlignCenter)
        layout.addWidget(wait)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f5ff;
            }
        """)

class MP4Converter(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set application font
        self.app_font = QFont()
        self.app_font.setPointSize(12)  # Bigger font size
        QApplication.setFont(self.app_font)
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle("✨ MP4 to Audio Converter ✨")
        self.setGeometry(300, 300, 700, 350)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f5ff;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #404080;
            }
            QLineEdit {
                border: 2px solid #c0c0ff;
                border-radius: 10px;
                padding: 8px;
                background-color: #ffffff;
                selection-background-color: #a0a0ff;
                font-size: 13px;
                min-height: 25px;
            }
            QPushButton {
                background-color: #7070ff;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-weight: bold;
                min-height: 30px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8080ff;
            }
            QPushButton:pressed {
                background-color: #6060ff;
            }
            QRadioButton {
                font-size: 14px;
                color: #404080;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QFrame {
                border-radius: 15px;
                background-color: #e0e8ff;
                margin: 5px;
                padding: 10px;
            }
            #convertButton {
                background-color: #ff70b0;
                font-size: 16px;
                padding: 12px;
                margin: 10px 50px;
                min-height: 40px;
            }
            #convertButton:hover {
                background-color: #ff80c0;
            }
            #titleLabel {
                font-size: 20px;
                color: #7070ff;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        title_label = QLabel("Convert Your Videos to Audio! 🎵")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Input file section
        input_frame = QFrame()
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        input_label = QLabel("🎬 Input MP4 file:")
        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("Select your video file...")
        browse_button = QPushButton("Browse 📂")
        browse_button.clicked.connect(self.browse_file)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(browse_button)
        
        # Output format section
        format_frame = QFrame()
        format_layout = QHBoxLayout(format_frame)
        format_layout.setContentsMargins(15, 15, 15, 15)
        
        format_label = QLabel("🎧 Output format:")
        self.mp3_radio = QRadioButton("MP3 🎵")
        self.wav_radio = QRadioButton("WAV 🔊")
        self.mp3_radio.setChecked(True)
        
        # Group radio buttons
        self.format_group = QButtonGroup()
        self.format_group.addButton(self.mp3_radio, 1)
        self.format_group.addButton(self.wav_radio, 2)
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.mp3_radio)
        format_layout.addWidget(self.wav_radio)
        format_layout.addStretch()
        
        # Output location section
        output_frame = QFrame()
        output_layout = QHBoxLayout(output_frame)
        output_layout.setContentsMargins(15, 15, 15, 15)
        
        output_label = QLabel("💾 Save location:")
        self.output_entry = QLineEdit()
        self.output_entry.setPlaceholderText("Choose where to save...")
        output_browse_button = QPushButton("Browse 📁")
        output_browse_button.clicked.connect(self.browse_save_location)
        
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_entry)
        output_layout.addWidget(output_browse_button)
        
        # Convert button
        convert_button = QPushButton("✨ Convert Now! ✨")
        convert_button.setObjectName("convertButton")
        convert_button.clicked.connect(self.convert_file)
        
        # Drag and drop instruction
        drag_label = QLabel("💡 Tip: You can also drag and drop your MP4 file here!")
        drag_label.setAlignment(Qt.AlignCenter)
        drag_label.setStyleSheet("color: #808080; font-style: italic;")
        
        # Add all components to main layout
        main_layout.addWidget(input_frame)
        main_layout.addWidget(format_frame)
        main_layout.addWidget(output_frame)
        main_layout.addWidget(convert_button)
        main_layout.addWidget(drag_label)
        
        # Setup drag and drop
        self.setAcceptDrops(True)
        
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select MP4 File", "", "MP4 Files (*.mp4)")
        if file_path:
            self.input_entry.setText(file_path)
            # Update default save location to same folder as input file
            if not self.output_entry.text():
                self.output_entry.setText(os.path.dirname(file_path))
    
    def browse_save_location(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder_path:
            self.output_entry.setText(folder_path)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toLocalFile().lower().endswith('.mp4'):
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        file_url = event.mimeData().urls()[0]
        self.input_entry.setText(file_url.toLocalFile())
        # Update default save location to same folder as input file
        if not self.output_entry.text():
            self.output_entry.setText(os.path.dirname(file_url.toLocalFile()))
    
    def convert_file(self):
        input_file = self.input_entry.text()
        save_location = self.output_entry.text()
        
        if not os.path.isfile(input_file) or not input_file.lower().endswith('.mp4'):
            QMessageBox.critical(self, "Invalid Input", "Please provide a valid MP4 file.")
            return
        
        if not os.path.isdir(save_location):
            QMessageBox.critical(self, "Invalid Save Location", "Please provide a valid save location.")
            return
        
        output_format = 'mp3' if self.mp3_radio.isChecked() else 'wav'
        output_filename = f"{os.path.splitext(os.path.basename(input_file))[0]}.{output_format}"
        output_file = os.path.join(save_location, output_filename)
        
        # Check if file already exists
        if os.path.exists(output_file):
            dialog = FileExistsDialog(self, output_file)
            dialog.exec_()
            
            if dialog.result_action == FileExistsDialog.SKIP:
                # User chose to skip this file
                QMessageBox.information(
                    self, 
                    "Conversion Skipped", 
                    f"Skipped conversion as file already exists: {output_filename}"
                )
                return
            elif dialog.result_action == FileExistsDialog.RENAME:
                # Auto-rename the file by adding a number
                counter = 1
                name_without_ext = os.path.splitext(output_filename)[0]
                ext = os.path.splitext(output_filename)[1]
                
                while True:
                    new_name = f"{name_without_ext}_{counter}{ext}"
                    new_path = os.path.join(save_location, new_name)
                    if not os.path.exists(new_path):
                        output_file = new_path
                        break
                    counter += 1
            # If OVERWRITE, we'll just continue with the original path
        
        # Create a custom progress dialog
        progress_dialog = ConversionProgressDialog(self, input_file, output_format)
        progress_dialog.show()
        QApplication.processEvents()
        
        # Disable main window interaction during conversion
        self.setEnabled(False)
        
        conversion_successful = False
        conversion_error = None
        
        try:
            # Perform the conversion
            stream = ffmpeg.input(input_file)
            stream = ffmpeg.output(stream, output_file)
            ffmpeg.run(stream, overwrite_output=True)
            conversion_successful = True
        except Exception as e:
            conversion_error = str(e)
        finally:
            # Re-enable the main window
            self.setEnabled(True)
            
            # Close and destroy the progress dialog
            progress_dialog.reject()
            progress_dialog.deleteLater()
            QApplication.processEvents()
        
        # Display appropriate message based on conversion result
        if conversion_successful:
            success_msg = QMessageBox(self)
            success_msg.setWindowTitle("Success! 🎉")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setText("Conversion Complete! 🥳")
            success_msg.setInformativeText(f"File has been converted to {output_format.upper()} successfully!\nSaved to: {output_file}")
            success_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #f0f5ff;
                    font-size: 14px;
                }
                QLabel {
                    color: #404080;
                    font-size: 14px;
                    min-width: 400px;
                }
                QPushButton {
                    background-color: #7070ff;
                    color: white;
                    border-radius: 10px;
                    padding: 8px 15px;
                    font-weight: bold;
                    min-height: 30px;
                    font-size: 13px;
                }
            """)
            success_msg.exec_()
        else:
            error_msg = QMessageBox(self)
            error_msg.setWindowTitle("Error 😢")
            error_msg.setIcon(QMessageBox.Critical)
            error_msg.setText("Conversion Failed")
            error_msg.setInformativeText(f"Failed to convert file: {conversion_error}")
            error_msg.setStyleSheet("""
                QMessageBox {
                    background-color: #fff0f0;
                    font-size: 14px;
                }
                QLabel {
                    color: #800000;
                    font-size: 14px;
                    min-width: 400px;
                }
                QPushButton {
                    background-color: #ff7070;
                    color: white;
                    border-radius: 10px;
                    padding: 8px 15px;
                    font-weight: bold;
                    min-height: 30px;
                    font-size: 13px;
                }
            """)
            error_msg.exec_()

def main():
    app = QApplication(sys.argv)
    window = MP4Converter()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

