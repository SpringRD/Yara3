from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUiType

import os
import sys
import subprocess
import multiprocessing
import re
import codecs

from datetime import datetime

from agents.helper import clean
import languages
import path_constants

from pygoogletranslation import Translator

main_class, _ = loadUiType(os.path.join(path_constants.bundle_dir, "ui//main.ui"))


class MainClass(QMainWindow, main_class):
    def __init__(self):
        super(MainClass, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)

        lice = self.checkTime()
        if not lice:
            msgbox = QMessageBox()
            msgbox.setIcon(QMessageBox.Critical)
            msgbox.setText("صلاحية البرنامج منتهية")
            msgbox.setWindowTitle("الصلاحية")
            msgbox.exec()
            sys.exit()

        ffmpeg_exe = os.path.join(path_constants.bundle_dir, "FFmpeg\\bin\\ffmpeg.exe")
        ffprobe_exe = os.path.join(path_constants.bundle_dir, "FFmpeg\\bin\\ffprobe.exe")
        os.environ['FFMPEG_PATH'] = ffmpeg_exe
        os.environ['FFPROBE_PATH'] = ffprobe_exe

        self.source_type = None
        self.output_type = None

        self.handle_ui()
        self.handle_buttons()

    def checkTime(self):
        dt = datetime.now()
        if dt.year == 2021:
            if dt.month < 4:
                return True
            else:
                return False
        else:
            return False

    def handle_ui(self):
        self.setFixedSize(700, 500)
        self.src_lang_combo.addItems(languages.SPEECH_TO_TEXT_LANGUAGE_CODES.values())
        self.dst_lang_combo.addItems(languages.TRANSLATION_LANGUAGE_CODES.values())
        index = self.src_lang_combo.findText('Arabic (Lebanon)', Qt.MatchFixedString)
        self.src_lang_combo.setCurrentIndex(index)
        index = self.dst_lang_combo.findText('Arabic', Qt.MatchFixedString)
        self.dst_lang_combo.setCurrentIndex(index)

        self.output_type_comboBox.currentTextChanged.connect(self.output_type_comboBox_changed)
        self.output_type_comboBox.setCurrentText("srt")

    def handle_buttons(self):
        self.browse_file_btn.clicked.connect(self.browse_file)
        self.browse_folder_btn.clicked.connect(self.browse_folder)
        self.srt_btn.clicked.connect(self.browse_srt)
        self.subtitles_btn.clicked.connect(self.detect)
        self.editor_btn.clicked.connect(self.open_editor)

    def output_type_comboBox_changed(self):
        if self.source_type == 'file':
            if self.srt_edit.text() is not None or not self.srt_edit.text() == '':
                ext = os.path.splitext(self.srt_edit.text())[1]
                if not ext == str(self.output_type_comboBox.currentText()):
                    self.srt_edit.setText(os.path.splitext(self.srt_edit.text())[0] + '.' + str(self.output_type_comboBox.currentText()))

    def browse_file(self):
        file = QFileDialog.getOpenFileName(parent=self, caption="اختر فيديو أو ملف صوتي",
                                           filter='Video Formats (*.mp4 *.mov *.avi *.mkv *.webm *.ogm *.wmv *.mpeg '
                                                  '*.mpg *.m4v *.avs *.asf);;'
                                                  'Audio Formats (*.mp3 *.wav *.wma *.ogg *.mka *.flac *.acc)')
        if not file[0] == '':
            self.source_type = 'file'
            srt = os.path.splitext(file[0])[0] + '.' + str(self.output_type_comboBox.currentText())
            self.source_edit.setText(file[0])
            self.srt_edit.setText(srt)

    def browse_folder(self):
        file = str(QFileDialog.getExistingDirectory(parent=self, caption="اختر مجلد"))
        if not file == '':
            self.source_type = 'folder'
            self.source_edit.setText(file)
            self.srt_edit.setText(file)

    def browse_srt(self):
        if self.source_type is None:
            self.details_txt.append('الرجاء اختيار ملف أو مجلد المصدر')
            self.repaint()
            return 1
        if self.source_type == 'file':
            file = QFileDialog.getOpenFileName(parent=self, caption="اختر ملف الترجمة (srt.)",
                                               filter='Subs Format (*.{})'.format(str(self.output_type_comboBox.currentText())))
            if not file[0] == '':
                self.srt_edit.setText(file[0])
        else:
            file = str(QFileDialog.getExistingDirectory(parent=self, caption="اختر مجلد للنتائج"))
            if not file == '':
                self.srt_edit.setText(file)

    def translate(self, file, src_language, dst_language):
        try:
            if src_language == dst_language:
                self.details_txt.append('   لغة الادخال ولغة الاخراج متساويان')
                self.details_txt.append('انتهاء العمل على الملف')
                self.repaint()
                return

            '''
            lines, count = clean(file)
            translator = Translator()
            args = file.split('.')
            fname = ''
            i = 0
            for n in args:
                if i == (len(args) - 1):
                    break
                fname += (n + '.')
                i += 1
            trans_file = '{}{}-{}.{}'.format(fname, src_language, dst_language, args[len(args) - 1])
            f_out = codecs.open(trans_file, 'w', "utf_8")
            if self.source_type == 'file':
                self.progress_bar.setMaximum(count)
                self.repaint()
            for line in lines:
                translated = translator.translate(line, src=src_language, dest=dst_language)
                f_out.write(translated.text + "\n")
                if self.source_type == 'file':
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    self.repaint()
            '''

            self.details_txt.append('   بدء الترجمة')
            self.repaint()
            lines, count = clean(file)
            translated_lines = []
            translator = Translator()
            if self.source_type == 'file':
                self.progress_bar.setMaximum(count + count + 1)
                self.repaint()
            for line in lines:
                translated = translator.translate(line, src=src_language, dest=dst_language)
                translated_lines.append(translated.text)
                if self.source_type == 'file':
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    self.repaint()

            f_in = codecs.open(file, 'r', "utf_8")

            i = 0
            j = 0
            data = []
            for d in f_in:
                data.append(d)
                match1 = re.match('^[0-9]+\s$', d)
                match2 = re.match('^\s$', d)
                match3 = re.match('^[0-9]{2}:', d)
                match4 = re.match('^﻿', d)
                if not (match1 or match2 or match3 or match4):
                    data[i] = translated_lines[j] + '\n'
                    j += 1
                    if self.source_type == 'file':
                        self.progress_bar.setValue(self.progress_bar.value() + 1)
                        self.repaint()
                i += 1

            f_out = codecs.open(file, 'w', "utf_8")
            for d in data:
                f_out.write(d)
                if self.source_type == 'file':
                    self.progress_bar.setValue(self.progress_bar.value() + 1)
                    self.repaint()
            f_in.close()
            f_out.close()

        except Exception as e:
            self.details_txt.append(e)
            self.repaint()
            print(e)
            return
        print('finish translating')
        self.details_txt.append('   انتهاء الترجمة')
        self.details_txt.append('انتهاء العمل على الملف')
        self.repaint()

    def detect(self):
        self.progress_bar.setValue(0)
        self.details_txt.clear()
        self.repaint()
        if self.source_edit.text() is None or self.source_edit.text() == '':
            self.details_txt.append('الرجاء اختيار ملف أو مجلد المصدر')
            self.repaint()
            return 1

        for key, value in languages.SPEECH_TO_TEXT_LANGUAGE_CODES.items():
            if value == self.src_lang_combo.currentText():
                src_language = key
                break
        for key, value in languages.TRANSLATION_LANGUAGE_CODES.items():
            if value == self.dst_lang_combo.currentText():
                dst_language = key
                break

        autosub_exe = os.path.join(path_constants.bundle_dir, "autosub\\autosub.exe")
        # autosub_exe = os.path.join(os.path.dirname(sys.executable), "Scripts\\autosub.exe")

        output = self.srt_edit.text()
        if self.source_type == 'file':
            self.details_txt.append('جاري العمل على الملف {}'.format(self.source_edit.text()))
            self.details_txt.append('   تحويل الصوت الى نص')
            self.repaint()
            command = "{} -i {} -S {} -y -o {}".format(str(autosub_exe), self.source_edit.text(), src_language, output)
            os.system(command)
            self.details_txt.append('   انتهاء التحويل')
            self.repaint()
            try:
                args = output.split('.')
                fname = ''
                i = 0
                for n in args:
                    if i == (len(args) - 1):
                        break
                    fname += (n + '.')
                    i += 1
                outp = '{}{}.{}'.format(fname, src_language, args[len(args) - 1])
                if os.path.exists(output):
                    os.remove(output)
                os.rename(outp, output)
            except Exception as e:
                print(e)
                self.details_txt.append(e)
                self.repaint()
                return 1
            self.translate(output, src_language.split('-')[0], dst_language)
        else:
            input_files = []
            for root, dirs, files in os.walk(self.source_edit.text()):
                for file in files:
                    if file.endswith(".mp4") or file.endswith(".mov ") or file.endswith(".avi") or file.endswith(".mkv") \
                            or file.endswith(".webm") or file.endswith(".ogm") or file.endswith(".wmv") \
                            or file.endswith(".mpeg") or file.endswith(".mpg") or file.endswith(".m4v") \
                            or file.endswith(".avs") or file.endswith(".asf") or file.endswith(".mp3") \
                            or file.endswith(".wav") or file.endswith(".wma") or file.endswith(".ogg") \
                            or file.endswith(".mka") or file.endswith(".flac") or file.endswith(".acc"):
                        input_files.append(os.path.join(root, file))
            if len(input_files) == 0:
                self.details_txt.append('المجلد المختار لا يحتوي على فيديهات او ملفات صوتية')
                self.repaint()
                return 1
            else:
                self.details_txt.append('عدد الملفات المدخلة = {}'.format(str(len(input_files))))
                self.progress_bar.setMaximum(len(input_files))
                self.repaint()
                for file in input_files:
                    self.details_txt.append('جاري العمل على الملف {}'.format(file))
                    self.details_txt.append('   تحويل الصوت الى نص')
                    self.repaint()
                    srt = os.path.splitext(file)[0] + '.' + str(self.output_type_comboBox.currentText())
                    command = "{} -i {} -S {} -y -o {}".format(str(autosub_exe), file, src_language, srt)
                    os.system(command)
                    self.details_txt.append('   انتهاء التحويل')
                    self.repaint()
                    try:
                        args = srt.split('.')
                        fname = ''
                        i = 0
                        for n in args:
                            if i == (len(args) - 1):
                                break
                            fname += (n + '.')
                            i += 1
                        outp = '{}{}.{}'.format(fname, src_language, args[len(args) - 1])
                        if os.path.exists(srt):
                            os.remove(srt)
                        os.rename(outp, srt)
                        self.translate(srt, src_language.split('-')[0], dst_language)
                        self.progress_bar.setValue(self.progress_bar.value() + 1)
                        self.details_txt.append('انتهاء العمل على الملف {}'.format(file))
                        self.repaint()
                    except Exception as e:
                        print(e)
                        self.details_txt.append(e)
                        self.repaint()
        return 0

    def open_editor(self):
        self.details_txt.clear()
        if self.source_edit.text() is None or self.source_edit.text() == '':
            self.details_txt.append("الرجاء تحديد ملف الصوت")
            return

        if self.source_type == 'folder':
            self.details_txt.append("الرجاء تحديد ملف الصوت وليس مجلد")
            return

        if not self.output_type_comboBox.currentText() == 'srt':
            self.details_txt.append("الرجاء تحديد ملف srt")
            return

        if not os.path.isfile(self.srt_edit.text()):
            self.details_txt.append("الرجاء تحديد ملف ترجمة موجود")
            return

        self.hide()

        aegisub_exe = os.path.join(path_constants.bundle_dir, "Aegisub\\aegisub32.exe")

        try:
            command = [aegisub_exe, self.srt_edit.text(), self.source_edit.text()]
            use_shell = True if os.name == "nt" else False
            subprocess.check_output(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=use_shell)
        except:
            pass

        self.show()


def main():
    app = QApplication(sys.argv)
    ex = MainClass()
    ex.show()
    app.exec_()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
