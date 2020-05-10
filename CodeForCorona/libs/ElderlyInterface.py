import os
import datetime
import pickle
import time
from typing import List

import pygame
from gtts import gTTS
from selenium.webdriver import Chrome

from libs.Firebase import storage
from libs.Schedule import Event

from PyQt5.Qt import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel


class ClientInterface(QWidget):
    def __init__(self):
        super().__init__()

        grid = QGridLayout()
        self.setLayout(grid)

        self.label_date = QLabel(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M"))
        self.label_date.setFont(QFont("Segeo UI", 25))
        grid.addWidget(self.label_date)

        self.label_text = QLabel("")
        self.label_text.setFont(QFont("Segeo UI", 25))
        grid.addWidget(self.label_text)


def start(user_id: str, client_interface: ClientInterface):
    storage.child(f"schedules/{user_id}.pickle").download("", f"temp.pickle")
    events: List[Event] = pickle.load(open("temp.pickle", "rb"))
    temp: List[Event] = []
    for event in events:
        if event.timing.date() >= datetime.datetime.now().date() and \
                event.timing.hour >= datetime.datetime.now().hour and \
                event.timing.minute >= datetime.datetime.now().minute:
            temp.append(event)

    events = temp[:]
    while len(events) != 0:
        print(events[0].timing, datetime.datetime.now())
        client_interface.label_date.setText(datetime.datetime.now().strftime("%a, %d %b %Y %H:%M"))
        if events[0].timing.date() == datetime.datetime.now().date() and \
                events[0].timing.hour == datetime.datetime.now().hour and \
                events[0].timing.minute == datetime.datetime.now().minute:
            if events[0].reminder_type == "Type Text":
                client_interface.label_text.setText(events[0].text)
                tts = gTTS(events[0].text, lang='zh-CN' if events[0].language == "Chinese" else "en")
                with open('temp.mp3', 'wb') as f:
                    tts.write_to_fp(f)

                pygame.mixer.init()
                pygame.mixer.music.load(open("temp.mp3", "rb"))
                pygame.mixer.music.play(0)  # Play Audio
                if events[0].type == "Video":
                    if events[0].media_file == "":
                        driver = Chrome()
                        driver.get(events[0].media_url)
                    else:
                        storage.child(f"schedules/{events[0].media_file}").download("", f"temp.mp4")
                        os.system("temp.mp4")

                events.pop(0)

            elif events[0].reminder_type == "Audio":
                storage.child(f"schedules/{events[0].media_file}").download("", f"temp.mp3")

                pygame.mixer.init()
                pygame.mixer.music.load(open("temp.mp3", "rb"))
                pygame.mixer.music.play(0)  # Play Audio

                events.pop(0)

        time.sleep(10)

    print("DONE FOR TODAY!")
