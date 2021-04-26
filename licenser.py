from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUiType

import os
import wmi
import hashlib

import path_constants


def get_serial():
    c = wmi.WMI()
    try:
        for item in c.Win32_PhysicalMedia():
            if item.wmi_property('Tag').value == "\\\\.\\PHYSICALDRIVE0":
                ser = item.wmi_property('SerialNumber').value
                break
        serial = ""
        for ch in ser:
            if not ch == ' ':
                serial += ch
        # serial = c.Win32_PhysicalMedia()[0].SerialNumber
        return serial
    except:
        return None


def get_license(ser, art_id):
    code = art_id + "_" + ser
    key = hashlib.md5(code.encode()).hexdigest()
    upper = key.upper()
    my_license = ""
    i = 0
    for ch in upper:
        i += 1
        my_license += ch
        if (i % 4) == 0 and i < len(upper):
            my_license += "-"
    return my_license


def check_lic(my_lic):
    if os.path.exists(path_constants.license_path):
        lcs_file = open(path_constants.license_path, 'r')
        lcs = lcs_file.read()
        if lcs == my_lic:
            return True
    return False


license_class, _ = loadUiType(os.path.join(path_constants.bundle_dir, "ui\\licenser.ui"))


class LicenseClass(QMainWindow, license_class):
    def __init__(self, serial, my_license, main_ui):
        super(LicenseClass, self).__init__()
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.serial = serial
        self.my_license = my_license

        self.main_ui = main_ui

        self.handle_ui()
        self.handle_buttons()

    def handle_ui(self):
        self.serial_edit.setText(self.serial)

    def handle_buttons(self):
        self.ok_button.clicked.connect(self.ok)

    def ok(self):
        if self.serial_edit.text() == "" or self.license_edit.text() == "":
            return
        lcs = self.license_edit.text()
        if not lcs == self.my_license:
            self.license_edit.setText("")
        else:
            f = open(path_constants.license_path, 'w')
            f.write(lcs)
            self.close()
            self.main_ui.show()
