'''
File QR Code Maker and Reader v0
By: Terence
ASSUMPTIONS:
- File path is not changed
'''

from tkinter.constants import ACTIVE, BOTH, BOTTOM, DISABLED, END, LEFT, NONE, NORMAL, TOP, X
from pyzbar import pyzbar
from PIL import Image
import pyqrcode

import tkinter as tk
from tkinter import filedialog as fdialog

import os
import subprocess

APP_TITLE = "File QR Code Maker and Reader"
APP_ICON_PATH = "qr_app.ico"
APP_WIDTH = 600
APP_HEIGHT = 400
APP_VERSION = "0"

DIR_ICON_PATH = "directory_button_icon.png"
FILE_ICON_PATH = "filepath_button_icon.png"

MAKER_TITLE = "File QR Code Maker"
MAKER_TARGET = 0
MAKER_LABEL_NAME = "File/Folder Path"
MAKER_TARGET_DIR = "/__generated_qr/"

READER_TITLE = "File QR Code Reader"
READER_TARGET = 1
READER_LABEL_NAME = "File Path"

LOG_SUCCESS = 0
LOG_ERROR = 1

SHELL_PATH = "powershell"
SHELL_COMMAND = "Invoke-Item -Path"

class FileEngineer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        # self.root.iconbitmap(APP_ICON_PATH)
        self.root.geometry(str(APP_WIDTH) + "x" + str(APP_HEIGHT))
        self.root.resizable(0, 0)

        # QR Code Maker
        self.code_maker()
        self.code_reader()
        self.log_updater()

    def tooltip_engine(self):
        # TODO: Make tooltips for almost everything?
        pass

    def text_input_check(self, target):
        '''
        For self.maker_text_box:
        Check if it is empty or not to deactivate self.
        '''
        if target == MAKER_TARGET:
            if self.maker_text_box.get():
                self.maker_start_button.configure(state=ACTIVE)
            else:
                self.maker_start_button.configure(state=DISABLED)
        elif target == READER_TARGET:
            if self.reader_text_box.get():
                self.reader_start_button.configure(state=ACTIVE)
            else:
                self.reader_start_button.configure(state=DISABLED)

    def text_highlight_all(self, target):
        if target == MAKER_TARGET:
            self.maker_text_box.selection_range(0, END)
        elif target == READER_TARGET:
            self.reader_text_box.selection_range(0, END)

    def log_msg_entry(self, message):
        self.log_msg_box.configure(state=NORMAL)
        message = message + "\n"
        self.log_msg_box.insert(END, message)
        self.log_msg_box.see(END)
        self.log_msg_box.configure(state=DISABLED)


    def maker_filepath_engine(self):
        file_names = fdialog.askopenfilenames(initialdir=".", title="Select file(s)", 
                                             filetypes=(("All Files", "*.*"),))
        if file_names:
            file_names = ", ".join(file_names)
            self.maker_text_box.delete(0, END)
            self.maker_text_box.insert(0, file_names)
            self.maker_start_button.configure(state=ACTIVE)

    def maker_dirpath_engine(self):
        dir_name = fdialog.askdirectory(initialdir=".", title="Select directory")
        if dir_name:
            self.maker_text_box.delete(0, END)
            self.maker_text_box.insert(0, dir_name)
            self.maker_start_button.configure(state=ACTIVE)

    def reader_filepath_engine(self):
        file_names = fdialog.askopenfilenames(initialdir=".", title="Select file(s)", 
                                             filetypes=(("PNG image(s)", "*.png"),))
        if file_names:
            file_names = ", ".join(file_names)
            self.reader_text_box.delete(0, END)
            self.reader_text_box.insert(0, file_names)
            self.reader_start_button.configure(state=ACTIVE)


    def code_maker_engine(self):
        '''
        Dealing with the main components of QR code making
        '''
        make_status_msg = "----- QR Code Maker -----"
        self.log_msg_entry(make_status_msg)

        file_names = self.maker_text_box.get()
        file_names = [file_name.strip() for file_name in file_names.split(",")]

        for file_path in file_names:
            # IF: The file path is a directory
            # Only accounts for files in the current folder, not subfolders
            if os.path.isdir(file_path):
                for file_name in os.listdir(file_path):
                    target_path = file_path + "/" + file_name
                    if os.path.isfile(target_path):
                        # print(file_path, file_name)
                        if not os.path.isdir(file_path + MAKER_TARGET_DIR):
                            os.mkdir(file_path + MAKER_TARGET_DIR)

                        qr_path = file_path + MAKER_TARGET_DIR + file_name
                        file_link = pyqrcode.create(target_path)
                        file_link.png(qr_path + ".png", scale=6)

                        make_status_msg = "[SUCCESS] " + target_path + ": QR code is generated."
                        self.log_msg_entry(make_status_msg)
            # ELSE: The file path is a file
            else:
                if not os.path.isfile(file_path):
                    make_status_msg = "[ERROR] " + file_path + ": File path not found."
                    self.log_msg_entry(make_status_msg)
                else:
                    # Making QR code for that particular file path
                    current_dir, file_name = file_path.rsplit("/", maxsplit=1)
                    # print(current_dir, file_name)
                    if not os.path.isdir(current_dir + MAKER_TARGET_DIR):
                        os.mkdir(current_dir + MAKER_TARGET_DIR)

                    qr_path = current_dir + MAKER_TARGET_DIR + file_name
                    file_link = pyqrcode.create(file_path)
                    file_link.png(qr_path + ".png", scale=6)

                    make_status_msg = "[SUCCESS] " + file_path + ": QR code is generated."
                    self.log_msg_entry(make_status_msg)

    def code_reader_engine(self):
        '''
        Dealing with the main components of QR code reading
        '''
        make_status_msg = "----- QR Code Reader -----"
        self.log_msg_entry(make_status_msg)

        file_names = self.reader_text_box.get()
        file_names = [file_name.strip() for file_name in file_names.split(",")]

        for file_path in file_names:
            if not os.path.isfile(file_path):
                make_status_msg = "[ERROR] " + file_path + ": Image not found."
                self.log_msg_entry(make_status_msg)
            else:
                # Reading QR code using pyzbar
                image_file = Image.open(file_path)
                decoded = pyzbar.decode(image_file)

                if decoded:
                    for obj in decoded:
                        file_path = obj.data.decode("utf-8")
                        # print(file_path)

                        if os.path.isfile(file_path):
                            make_status_msg = "[SUCCESS] " + file_path + ": QR code decoded. Opening file..."
                            self.log_msg_entry(make_status_msg)

                            open_command = SHELL_PATH + " " + SHELL_COMMAND + " \\\"" + file_path + "\\\""
                            subprocess.run(open_command, shell=True)
                        else:
                            make_status_msg = "[ERROR] " + file_path + ": QR code decoded, however file path not found."
                            self.log_msg_entry(make_status_msg)
                else:
                    make_status_msg = "[ERROR] " + file_path + ": QR code in target image not found."
                    self.log_msg_entry(make_status_msg)


    def code_maker(self):
        # QR Code Maker Frame
        self.maker_frame = tk.LabelFrame(self.root, text=MAKER_TITLE)
        self.maker_frame.pack(side=TOP, fill=BOTH, expand=True, padx=5, pady=5)

        # (1) Handling file or folder path
        self.maker_handle_frame = tk.Frame(self.maker_frame)
        self.maker_handle_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.maker_label = tk.Label(self.maker_handle_frame, text=MAKER_LABEL_NAME)
        self.maker_label.pack(side=LEFT, ipadx=5, fill=X)
        self.maker_text_box = tk.Entry(self.maker_handle_frame, bd=3)
        self.maker_text_box.bind("<KeyRelease>", lambda x: self.text_input_check(target=MAKER_TARGET))
        self.maker_text_box.bind("<FocusIn>", lambda x: self.text_highlight_all(target=MAKER_TARGET))
        self.maker_text_box.pack(side=LEFT, expand=True, padx=5, fill=X)

        self.maker_dirpath_button = tk.Button(self.maker_handle_frame, text="Dir", command=self.maker_dirpath_engine)
        self.maker_dirpath_button.pack(side=LEFT, fill=X, ipadx=5)

        self.maker_filepath_button = tk.Button(self.maker_handle_frame, text="File", command=self.maker_filepath_engine)
        self.maker_filepath_button.pack(side=LEFT, padx=5, fill=X, ipadx=5)

        # (2) Start Making Button
        self.maker_start_button_frame = tk.Frame(self.maker_frame)
        self.maker_start_button_frame.pack(expand=True, fill=BOTH)

        self.maker_start_button = tk.Button(self.maker_start_button_frame, text="Start Making", state=DISABLED,
                                            command=self.code_maker_engine)
        self.maker_start_button.pack()


    def code_reader(self):
        self.reader_frame = tk.LabelFrame(self.root, text="File QR Code Reader")
        self.reader_frame.pack(expand=True, fill=BOTH, padx=5, pady=5)

        # (1) File handler
        self.reader_handle_frame = tk.Frame(self.reader_frame)
        self.reader_handle_frame.pack(side=TOP, expand=True, fill=BOTH)

        self.reader_label = tk.Label(self.reader_handle_frame, text=READER_LABEL_NAME)
        self.reader_label.pack(side=LEFT, ipadx=5, fill=X)
        self.reader_text_box = tk.Entry(self.reader_handle_frame, bd=3)
        self.reader_text_box.bind("<KeyRelease>", lambda x: self.text_input_check(target=READER_TARGET))
        self.reader_text_box.bind("<FocusIn>", lambda x: self.text_highlight_all(target=READER_TARGET))
        self.reader_text_box.pack(side=LEFT, expand=True, padx=5, fill=X)

        self.reader_filepath_button = tk.Button(self.reader_handle_frame, text="File", command=self.reader_filepath_engine)
        self.reader_filepath_button.pack(side=LEFT, padx=5, fill=X, ipadx=5)

        # (2) Read QR Code Button
        self.reader_start_button_frame = tk.Frame(self.reader_frame)
        self.reader_start_button_frame.pack(expand=True, fill=BOTH)

        self.reader_start_button = tk.Button(self.reader_start_button_frame, text="Read QR Code", state=DISABLED,
                                             command=self.code_reader_engine)
        self.reader_start_button.pack()
        

    def log_updater(self):
        # Log Message Box
        self.log_msg_box_frame = tk.Frame(self.root)
        self.log_msg_box_frame.pack(side=BOTTOM, expand=True, fill=BOTH, padx=5, pady=5)

        self.log_msg_box = tk.Text(self.log_msg_box_frame, font=("", 8), height=6, wrap=NONE)
        self.log_msg_box.pack(expand=True, fill=BOTH)

        self.log_msg_box.configure(state=DISABLED)

        welcome_script = "File QR Code Maker/Reader v" + APP_VERSION + " by Terence" + "\n"
        welcome_script += "[Maker]: Indicate file(s) or folder path to start making the QR codes of the files." + "\n"
        welcome_script += "If folder is selected, all files in the current folder will be selected instead except the subfolders." + "\n"
        welcome_script += "Any successfully generated QR code is saved in __generated_qr folder." + "\n"
        welcome_script += "[Reader]: Indicate file(s) path to decode the QR codes and open the file(s) if successfully decoded."
        self.log_msg_entry(welcome_script)


main_app = FileEngineer()
main_app.root.mainloop()
