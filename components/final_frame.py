from PyQt5.QtWidgets import QFrame, QFileDialog
from PyQt5.uic import loadUiType

import os
import subprocess

from agents.helper import clean_srt, get_regions
from agents.buckwalter2unicode import buckwalter2unicode
import path_constants

final_frame_class, _ = loadUiType(os.path.join(path_constants.bundle_dir, "ui//final_frame.ui"))


class FinalFrame(QFrame, final_frame_class):

    def __init__(self, parent):
        super(FinalFrame, self).__init__()
        QFrame.__init__(self)
        self.setupUi(self)

        self.parent = parent
        self.ffmpeg_exe = os.path.join(path_constants.bundle_dir, "FFmpeg\\bin\\ffmpeg.exe")

        self.handle_ui()
        self.handle_buttons()

    def handle_ui(self):
        pass

    def handle_buttons(self):
        self.previous_btn.clicked.connect(self.previous)
        self.browse_input_btn.clicked.connect(self.browse_input)
        self.browse_subtitle_btn.clicked.connect(self.browse_subtitle)
        self.browse_output_btn.clicked.connect(self.browse_output)
        self.generate_btn.clicked.connect(self.generate_results)

    def previous(self):
        self.parent.display(1)

    def browse_input(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="Select Audio(.wav) File",
                                           filter='Audio Format (*.wav)')
        if not file[0] == '':
            self.input_edit.setText(file[0])

    def browse_subtitle(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="Select Subtitle (.srt) File",
                                           filter='Srt Format (*.srt)')
        if not file[0] == '':
            self.subtitle_edit.setText(file[0])

    def browse_output(self):
        folder_path = QFileDialog.getExistingDirectory(parent=self, caption="Select Folder")
        if not folder_path == '':
            self.output_edit.setText(folder_path)

    def generate_results(self):
        self.details_txt.clear()

        if self.input_edit.text() == '':
            self.details_txt.insertPlainText('Please select an input file\n')
            return 1

        if self.subtitle_edit.text() == '':
            self.details_txt.insertPlainText('Please select a subtitle(.srt) file\n')
            return 1

        if self.output_edit.text() == '':
            self.details_txt.insertPlainText('Please select an output folder\n')
            return 1

        filename_w_ext = os.path.basename(self.subtitle_edit.text())
        filename, _ = os.path.splitext(filename_w_ext)

        clips_folder = os.path.join(self.output_edit.text(), filename + '_clips')
        if not os.path.isdir(clips_folder):
            os.mkdir(clips_folder)

        regions = get_regions(self.subtitle_edit.text())
        if len(regions) == 0:
            self.details_txt.insertPlainText('No regions of time found at {}\n'.format(self.subtitle_edit.text()))
            return

        self.progress_bar.setMaximum(len(regions) + 2)
        self.progress_bar.setValue(0)

        self.details_txt.insertPlainText('Splitting audio by srt file:\n')
        self.details_txt.insertPlainText("-----------waiting----------\n")
        i = 1
        try:
            for region in regions:
                command = [self.ffmpeg_exe, "-v", "warning", "-i", str(self.input_edit.text()), "-strict",
                           "-2", "-ss", str(region[0]), "-t", str(region[1]), "-y",
                           str(os.path.join(clips_folder, '{}_{}.wav'.format(i, filename)))]
                use_shell = True if os.name == "nt" else False
                subprocess.check_output(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=use_shell)
                self.progress_bar.setValue(self.progress_bar.value() + 1)
                self.repaint()
                i += 1
            self.details_txt.insertPlainText('Finish Splitting\n{} files available at {}\n'.format(len(regions), clips_folder))
        except Exception as e:
            self.details_txt.insertPlainText('Error at Splitting\n')
            self.progress_bar.setValue(0)
            self.repaint()
            return

        self.details_txt.insertPlainText('Removing timestamps and empty lines from the file:\n')
        destination_clean = os.path.join(self.output_edit.text(), filename + '_clean.txt')
        clean_srt(self.subtitle_edit.text(), destination_clean)
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.details_txt.insertPlainText('The cleaned file is at path: {}\n'.format(destination_clean))
        self.repaint()

        self.details_txt.insertPlainText('Transforming the cleaned file to ASCII buckwalter format:\n')
        destination_buckwalter = os.path.join(self.output_edit.text(), filename + '_buckwalter.txt')
        result = buckwalter2unicode(destination_clean, destination_buckwalter, reverse=1)
        if result:
            self.progress_bar.setValue(0)
            self.details_txt.insertPlainText('Error at buckwlater\n')
            self.repaint()
            return
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.details_txt.insertPlainText('The transformed file is at path: {}\n'.format(destination_buckwalter))
        self.repaint()
