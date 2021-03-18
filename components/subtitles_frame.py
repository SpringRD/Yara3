from PyQt5.QtWidgets import QFrame, QFileDialog, QApplication
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUiType

import os
import multiprocessing

from autosub.constants import LANGUAGE_CODES, GOOGLE_SPEECH_API_KEY
from autosub.formatters import FORMATTERS
from autosub.converter import FLACConverter, SpeechRecognizer, extract_audio, find_speech_regions, is_same_language

import path_constants

subtitles_frame_class, _ = loadUiType(os.path.join(path_constants.bundle_dir, "ui//subtitles_frame.ui"))


class SubtitlesFrame(QFrame, subtitles_frame_class):

    def __init__(self, parent):
        super(SubtitlesFrame, self).__init__()
        QFrame.__init__(self)
        self.setupUi(self)

        self.parent = parent
        self.output = None
        self.source_path = None

        self.handle_ui()
        self.handle_buttons()

    def handle_ui(self):
        self.src_lang_combo.addItems(LANGUAGE_CODES.values())
        self.dst_lang_combo.addItems(LANGUAGE_CODES.values())
        index = self.src_lang_combo.findText('Arabic', Qt.MatchFixedString)
        self.src_lang_combo.setCurrentIndex(index)
        self.dst_lang_combo.setCurrentIndex(index)

    def handle_buttons(self):
        self.next_btn.clicked.connect(self.next)
        self.browse_input_btn.clicked.connect(self.browse_input)
        self.browse_output_btn.clicked.connect(self.browse_output)
        self.generate_btn.clicked.connect(self.generate)

    def next(self):
        self.parent.display(1)

    def browse_input(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="Select Video or Audio File",
                                           filter='Video Formats (*.mp4 *.mov *.avi *.mkv *.webm *.ogm *.wmv *.mpeg '
                                                  '*.mpg *.m4v *.avs *.asf);;'
                                                  'Audio Formats (*.mp3 *.wav *.wma *.ogg *.mka *.flac *.acc)')
        if not file[0] == '':
            self.source_path = file[0]
            self.input_edit.setText(file[0])

    def browse_output(self):
        folder_path = QFileDialog.getExistingDirectory(parent=self, caption="Select Folder")
        if not folder_path == '':
            self.output = folder_path
            self.output_edit.setText(folder_path)

    def generate(self):
        self.details_txt.clear()
        if self.source_path is None:
            self.details_txt.insertPlainText('Please select an input file\n')
            return 1

        if self.output is None:
            self.details_txt.insertPlainText('Please select an output folder\n')
            return 1

        for key, value in LANGUAGE_CODES.items():
            if value == self.src_lang_combo.currentText():
                src_language = key
                break
        for key, value in LANGUAGE_CODES.items():
            if value == self.dst_lang_combo.currentText():
                dst_language = key
                break

        audio_filename, audio_rate = extract_audio(self.source_path, self.output)
        self.details_txt.insertPlainText('{} saved\n'.format(audio_filename))
        self.progress_bar.setValue(self.progress_bar.value() + 1)

        regions = find_speech_regions(audio_filename)
        self.details_txt.insertPlainText('{} speech regions found\n'.format(len(regions)))
        self.progress_bar.setMaximum(len(regions) * 2 + 1)
        self.progress_bar.setValue(self.progress_bar.value() + 1)

        pool = multiprocessing.Pool(10)
        converter = FLACConverter(source_path=audio_filename)
        recognizer = SpeechRecognizer(language=src_language, rate=audio_rate, api_key=GOOGLE_SPEECH_API_KEY)

        transcripts = []
        if regions:
            try:
                self.details_txt.insertPlainText("Converting speech regions to FLAC files:\n")
                self.details_txt.insertPlainText("-------------------waiting------------------\n")
                extracted_regions = []
                for (i, extracted_region) in enumerate(pool.imap(converter, regions)):
                    extracted_regions.append(extracted_region)
                    QApplication.processEvents()
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    QApplication.processEvents()
                    self.repaint()
                self.details_txt.insertPlainText("Finish Converting\n")

                self.details_txt.insertPlainText("Performing speech recognition:\n")
                self.details_txt.insertPlainText("--------------waiting-------------\n")
                for i, transcript in enumerate(pool.imap(recognizer, extracted_regions)):
                    transcripts.append(transcript)
                    QApplication.processEvents()
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    QApplication.processEvents()
                    self.repaint()
                self.details_txt.insertPlainText("Finish Performing\n")

                pool.terminate()
                pool.join()

                if not is_same_language(src_language, dst_language):
                    self.details_txt.insertPlainText("Error: Subtitle translation requires specified Google Translate "
                                                     "API key. See --help for further information.")
                    return 1

            except KeyboardInterrupt:
                self.progress_bar.setValue(0)
                pool.terminate()
                pool.join()
                self.details_txt.insertPlainText("Cancelling transcription\n")
                return 1

        timed_subtitles = [(r, t) for r, t in zip(regions, transcripts) if t]
        formatter = FORMATTERS.get('srt')
        formatted_subtitles = formatter(timed_subtitles)

        filename_w_ext = os.path.basename(self.source_path)
        filename, _ = os.path.splitext(filename_w_ext)
        destination = os.path.join(self.output, filename + '.srt')

        with open(destination, 'wb') as f:
            f.write(formatted_subtitles.encode("utf-8"))

        self.parent.edit_changed_signal.emit(self.source_path, self.output, audio_filename, destination)
        self.details_txt.insertPlainText("Subtitles file created at {}\n".format(destination))

        return 0
