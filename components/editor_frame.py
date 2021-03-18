from PyQt5.QtWidgets import QFrame, QFileDialog
from PyQt5.uic import loadUiType

import os
import subprocess

import path_constants

editor_frame_class, _ = loadUiType(os.path.join(path_constants.bundle_dir, "ui//editor_frame.ui"))


class EditorFrame(QFrame, editor_frame_class):

    def __init__(self, parent):
        super(EditorFrame, self).__init__()
        QFrame.__init__(self)
        self.setupUi(self)

        self.parent = parent
        self.aegisub_exe = os.path.join(path_constants.bundle_dir, "Aegisub\\aegisub32.exe")

        self.handle_ui()
        self.handle_buttons()

    def handle_ui(self):
        pass

    def handle_buttons(self):
        self.next_btn.clicked.connect(self.next)
        self.previous_btn.clicked.connect(self.previous)
        self.browse_input_btn.clicked.connect(self.browse_input)
        self.browse_subtitle_btn.clicked.connect(self.browse_subtitle)
        self.open_btn.clicked.connect(self.open_editor)

    def next(self):
        self.parent.display(2)

    def previous(self):
        self.parent.display(0)

    def browse_input(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="Select Video or Audio File",
                                           filter='Video Formats (*.mp4 *.mov *.avi *.mkv *.webm *.ogm *.wmv *.mpeg '
                                                  '*.mpg *.m4v *.avs *.asf);;'
                                                  'Audio Formats (*.mp3 *.wav *.wma *.ogg *.mka *.flac *.acc)')
        if not file[0] == '':
            self.input_edit.setText(file[0])

    def browse_subtitle(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="Select Subtitle (.srt) File",
                                           filter='Srt Format (*.srt)')
        if not file[0] == '':
            self.subtitle_edit.setText(file[0])

    def open_editor(self):
        if self.input_edit.text() == '':
            return

        if self.subtitle_edit.text() == '':
            return

        self.parent.hide()

        command = [self.aegisub_exe, str(self.subtitle_edit.text()), str(self.input_edit.text())]
        use_shell = True if os.name == "nt" else False
        subprocess.check_output(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=use_shell)

        self.parent.show()
