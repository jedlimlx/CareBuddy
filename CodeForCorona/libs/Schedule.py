import pafy
import pickle
import datetime
import traceback
from typing import List, Dict

import pygame
from functools import partial
from PyQt5.Qt import pyqtSignal as Signal
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QFileDialog, QDialog, QComboBox, QLineEdit, \
    QCalendarWidget, QSpinBox, QListWidget, QListWidgetItem
from libs.Firebase import storage


class Event:
    def __init__(self):
        self.name: str = ""
        self.type: str = "Reminder"  # Reminder / Video
        self.reminder_type: str = "Type Text"  # Type Text / Audio
        self.text: str = "Remember to Wear a Mask"
        self.media_file: str = ""
        self.media_url: str = ""
        self.timing = datetime.datetime.now()
        self.language: str = "English"

        self.translations = {}

    def load_video_file(self):
        # Open Video File
        file_name, _ = QFileDialog.getOpenFileName(caption="Load Video File",
                                                   filter="MP4 Files (*.mp4);;MOV Files (*.MOV);;All Files (*.)")
        if file_name != "": self.media_file = file_name

    def load_audio_file(self):
        # Open Audio File
        file_name, _ = QFileDialog.getOpenFileName(caption="Load Audio File",
                                                   filter="MP3 Files (*.mp3);;WAV Files (*.wav);;"
                                                          "M4A Files(*.m4a);;All Files(*.)")
        if file_name != "": self.media_file = file_name

    def play_audio(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(self.media_file)
            pygame.mixer.music.play(0)  # Play Audio
        except Exception:
            print(traceback.format_exc())

    def get_text(self):
        if self.type == "Video":
            if self.media_file == "":
                video = pafy.new(self.media_url)
                return video.title
            return self.media_file
        else:
            if self.reminder_type == "Audio":
                if self.media_file == "":
                    video = pafy.new(self.media_url)
                    return video.title
                return self.media_file
            else:
                return self.text

    def __str__(self):
        if self.type == "Video":
            return str(self.timing.strftime("%H:%M")) + " " + self.name
        else:
            if self.reminder_type == "Audio":
                return str(self.timing.strftime("%H:%M")) + " " + self.name
            else:
                return str(self.timing.strftime("%H:%M")) + " " + self.name

    def __lt__(self, other):
        return self.timing < other.timing


class EventDialog(QDialog):
    def __init__(self, timing: datetime.datetime):
        super().__init__()

        # Auto Completer Model
        """
        model = QStringListModel(["Remember to wear your mask!", "Please watch the video and exercise!",
                                  "Exercise and watch the video."])
        """

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(20)
        self.setLayout(grid)

        self.new_event = Event()
        self.new_event.timing = timing

        label_name = QLabel("Name:")
        grid.addWidget(label_name, 0, 0)

        self.name_entry = QLineEdit()
        grid.addWidget(self.name_entry, 0, 1)

        label_hour = QLabel("Hour:")
        grid.addWidget(label_hour, 1, 0)

        self.hour_spinbox = QSpinBox()  # Spinbox to Choose Hour
        self.hour_spinbox.setValue(timing.hour)
        self.hour_spinbox.setMaximum(23)
        grid.addWidget(self.hour_spinbox, 1, 1)

        label_minute = QLabel("Minute:")
        grid.addWidget(label_minute, 2, 0)

        self.minute_spinbox = QSpinBox()  # Spinbox to Choose Hour
        self.minute_spinbox.setMaximum(59)
        grid.addWidget(self.minute_spinbox, 2, 1)

        label_suggestions = QLabel("Suggestions:")
        grid.addWidget(label_suggestions, 3, 0)

        try:
            # Suggestions
            self.suggestions: Dict[str, Event] = pickle.load(open("suggestions.pickle", "rb"))
            self.suggestions_lst: List[str] = ["NIL"] + sorted(self.suggestions.keys())

            self.suggestions_combobox = QComboBox()
            self.suggestions_combobox.addItems(self.suggestions_lst)
            self.suggestions_combobox.currentIndexChanged.connect(self.load_suggestion)
            grid.addWidget(self.suggestions_combobox, 3, 1)
        except:
            print(traceback.format_exc())

        label_language = QLabel("Language:")
        grid.addWidget(label_language, 4, 0)

        # Type of Event
        self.languages = ["English", "Chinese"]
        self.language_combobox = QComboBox()
        self.language_combobox.addItems(self.languages)
        self.language_combobox.currentTextChanged.connect(self.change_language)
        grid.addWidget(self.language_combobox, 4, 1)

        label_type = QLabel("Type of Event:")
        grid.addWidget(label_type, 5, 0)

        # Type of Event
        self.types = ["Reminder", "Video"]
        self.type_combobox = QComboBox()
        self.type_combobox.addItems(self.types)
        self.type_combobox.currentTextChanged.connect(self.change_event_type)
        grid.addWidget(self.type_combobox, 5, 1)

        self.label_reminder_type = QLabel("Type of Reminder:")
        grid.addWidget(self.label_reminder_type, 6, 0)

        # Type of Reminder
        self.reminder_types = ["Type Text", "Audio"]
        self.reminder_type_combobox = QComboBox()
        self.reminder_type_combobox.addItems(self.reminder_types)
        self.reminder_type_combobox.currentTextChanged.connect(self.change_reminder_type)
        grid.addWidget(self.reminder_type_combobox, 6, 1)

        # Upload Video Button
        self.video_upload_btn = QPushButton("Upload Video")
        self.video_upload_btn.clicked.connect(self.upload_video)
        self.video_upload_btn.hide()
        grid.addWidget(self.video_upload_btn, 6, 0)

        # Url Entry
        self.video_upload_entry = QLineEdit()
        self.video_upload_entry.setToolTip("Enter Url Here")
        self.video_upload_entry.hide()
        grid.addWidget(self.video_upload_entry, 6, 1)

        # Audio Button
        self.audio_upload_btn = QPushButton("Upload Audio")
        self.audio_upload_btn.clicked.connect(self.upload_audio)
        self.audio_upload_btn.hide()
        grid.addWidget(self.audio_upload_btn, 7, 0)

        # Url Entry
        self.audio_upload_entry = QLineEdit()
        self.audio_upload_entry.setToolTip("Enter Url Here")
        self.audio_upload_entry.hide()
        grid.addWidget(self.audio_upload_entry, 7, 1)

        # Label for Type Text
        self.label_text_2_speech = QLabel("Enter Text Here:")
        grid.addWidget(self.label_text_2_speech, 7, 0)

        # Entry for Text
        self.text_entry = QLineEdit()

        """
        auto_completer = QCompleter()
        auto_completer.setModel(model)
        auto_completer.setCompletionMode(QCompleter)
        self.text_entry.setCompleter(auto_completer)  # Setting Autocompleter
        """

        grid.addWidget(self.text_entry, 7, 1)

        # Okay and Cancel Button
        okay_btn = QPushButton("Ok")
        okay_btn.clicked.connect(self.accept)
        grid.addWidget(okay_btn, 8, 0)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        grid.addWidget(cancel_btn, 8, 1)

    def change_event_type(self):
        self.new_event.type = self.types[self.type_combobox.currentIndex()]
        if self.types[self.type_combobox.currentIndex()] == "Video":
            self.video_upload_btn.show()
            self.video_upload_entry.show()
        else:
            self.video_upload_btn.hide()
            self.video_upload_entry.hide()

    def change_reminder_type(self):
        self.new_event.reminder_type = self.reminder_types[self.reminder_type_combobox.currentIndex()]
        if self.reminder_types[self.reminder_type_combobox.currentIndex()] == "Type Text":
            self.audio_upload_entry.hide()
            self.audio_upload_btn.hide()
            self.text_entry.show()
            self.label_text_2_speech.show()
        else:
            self.audio_upload_btn.show()
            self.audio_upload_entry.show()
            self.text_entry.hide()
            self.label_text_2_speech.hide()

    def upload_video(self):
        if self.video_upload_entry.text() == "":
            self.new_event.load_video_file()
            self.video_upload_entry.setText(self.new_event.media_file)
        else:
            self.new_event.media_url = self.video_upload_entry.text()

    def upload_audio(self):
        if self.audio_upload_entry.text() == "":
            self.new_event.load_audio_file()
            self.audio_upload_entry.setText(self.new_event.media_file)
        else:
            self.new_event.media_url = self.audio_upload_entry.text()

    def load_suggestion(self):
        if self.suggestions_lst[self.suggestions_combobox.currentIndex()] != "NIL":
            self.load_event(self.suggestions[self.suggestions_lst[self.suggestions_combobox.currentIndex()]],
                            load_time=False)

    def load_event(self, event: Event, load_time=True):
        self.name_entry.setText(event.name)
        try:
            self.text_entry.setText(event.translations[self.languages[self.language_combobox.currentIndex()]])
        except KeyError:
            self.text_entry.setText(event.text)

        if load_time:
            self.hour_spinbox.setValue(event.timing.hour)
            self.minute_spinbox.setValue(event.timing.minute)

        self.audio_upload_entry.setText(event.media_file if event.media_file != "" else event.media_url)
        self.video_upload_entry.setText(event.media_file if event.media_file != "" else event.media_url)

        self.type_combobox.setCurrentIndex(self.types.index(event.type))
        self.reminder_type_combobox.setCurrentIndex(self.reminder_types.index(event.reminder_type))
        self.language_combobox.setCurrentIndex(self.languages.index(event.language))

    def change_language(self):
        if self.suggestions_lst[self.suggestions_combobox.currentIndex()] != "NIL":
            self.text_entry.setText(self.suggestions[self.suggestions_lst[self.suggestions_combobox.currentIndex()]].
                                    translations[self.languages[self.language_combobox.currentIndex()]])

    def get_results(self):
        if self.exec() == QDialog.Accepted:
            self.new_event.name = self.name_entry.text()
            self.new_event.text = self.text_entry.text()
            self.new_event.timing = self.new_event.timing.replace(
                hour=self.hour_spinbox.value(), minute=self.minute_spinbox.value())
            if self.new_event.media_file == "":
                if self.reminder_types[self.reminder_type_combobox.currentIndex()] == "Audio":
                    self.upload_audio()
                if self.types[self.type_combobox.currentIndex()] == "Video":
                    self.upload_video()

            self.new_event.language = self.languages[self.language_combobox.currentIndex()]
            return self.new_event
        else:
            return None


class Details(QDialog):
    create_event_signal = Signal(int)
    delete_event_signal = Signal(int)
    edit_event_signal = Signal(Event, int)

    def __init__(self, event_lst: List[Event], starting_index: int, time: int):
        super().__init__()

        grid = QGridLayout()
        self.setLayout(grid)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.edit_event)
        grid.addWidget(self.list_widget)

        self.item_lst = []
        self.event_lst = event_lst
        self.starting_index = starting_index
        self.time = time
        for index, event in enumerate(event_lst):
            lst_item = QListWidgetItem(str(event))
            self.item_lst.append(lst_item)
            self.list_widget.addItem(lst_item)

        self.create_event = QPushButton("Create Event")  # Create the Event
        self.create_event.clicked.connect(self.create_event_func)
        grid.addWidget(self.create_event)

        delete_btn = QPushButton("Delete Event")  # Button to Delete the Event
        delete_btn.clicked.connect(self.delete_event)
        grid.addWidget(delete_btn)

    def edit_event(self, clicked_item: QListWidgetItem):
        found_index = 0
        for index, item in enumerate(self.item_lst):
            if item == clicked_item:
                found_index = index
                break

        event_dialog = EventDialog(datetime.datetime.now())
        event_dialog.load_event(self.event_lst[found_index])
        new_event = event_dialog.get_results()

        if new_event is not None:
            self.edit_event_signal.emit(new_event, self.starting_index + found_index)
            self.accept()

    def create_event_func(self):
        self.create_event_signal.emit(self.time)
        self.accept()

    def delete_event(self):
        found_index = 0
        for index, item in enumerate(self.item_lst):
            if item == self.list_widget.currentItem():
                found_index = index
                break

        self.delete_event_signal.emit(self.starting_index + found_index)
        self.accept()


class Schedule(QWidget):
    def __init__(self, user_id: str):
        super().__init__()

        self.user_id = user_id

        grid = QGridLayout()
        self.setLayout(grid)

        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.new_date)
        grid.addWidget(self.calendar)

        self.events = []

        current_date = self.calendar.selectedDate()
        self.date_label = QLabel(datetime.datetime(
            current_date.year(), current_date.month(), current_date.day()).strftime("%a, %d %b %Y"))
        grid.addWidget(self.date_label)

        timings = QWidget()
        timings_grid = QGridLayout()
        timings.setLayout(timings_grid)

        self.create_btn_lst: List[QPushButton] = []
        self.details_label_lst: List[QLabel] = []
        for hour in range(6, 24):  # Adding Widgets for Each Timing
            label = QLabel(f"{hour}:00")
            timings_grid.addWidget(label, (hour - 6) % 9, (hour - 6) // 9 * 3)

            create_event_btn = QPushButton()
            create_event_btn.setToolTip("Click to Create Event!")
            create_event_btn.clicked.connect(partial(self.get_details, time=hour))
            self.create_btn_lst.append(create_event_btn)
            timings_grid.addWidget(create_event_btn, (hour - 6) % 9, (hour - 6) // 9 * 3 + 1)

            details_label = QLabel()
            self.details_label_lst.append(details_label)
            timings_grid.addWidget(details_label, (hour - 6) % 9, (hour - 6) // 9 * 3 + 2)

        grid.addWidget(timings)

        save_btn = QPushButton("Save and Upload to Database")
        save_btn.clicked.connect(self.upload_to_firebase)
        grid.addWidget(save_btn)

        # Download the Schedule from Firebase
        try:
            storage.child(f"schedules/{self.user_id}.pickle").download("", f"temp.pickle")
            self.events = pickle.load(open("temp.pickle", "rb"))
            self.reload()

        except FileNotFoundError:
            print("File Not Found in Firebase!")

    def create_new_event(self, time):
        date = self.calendar.selectedDate()
        event_dialog = EventDialog(datetime.datetime(date.year(), date.month(), date.day(), time, 0, 0))
        event = event_dialog.get_results()
        if event is not None:
            self.events.append(event)
            self.events.sort()  # Sorting by Timing

            print([str(event) for event in self.events])

            self.reload()

            """
            new_num: int = int(self.details_btn_lst[event.timing.hour].text().split('(')[1][0]) + 1
            self.details_btn_lst[event.timing.hour].setText(
                f"Details ({new_num} {'Events' if new_num != 1 else 'Event'})")  # Prevent Grammatical Errors
            """

    def get_details(self, time):
        new_events_lst = []
        date = self.calendar.selectedDate()
        lower_bound = datetime.datetime(date.year(), date.month(), date.day(), time, 0, 0)
        upper_bound = datetime.datetime(date.year(), date.month(), date.day(), time + 1, 0, 0)
        starting_index = -1
        for index, event in enumerate(self.events):
            if lower_bound <= event.timing < upper_bound:
                if starting_index == -1: starting_index = index
                new_events_lst.append(event)

        detail_dialog = Details(new_events_lst, starting_index, time)
        detail_dialog.edit_event_signal.connect(self.edit_event)
        detail_dialog.create_event_signal.connect(self.create_new_event)
        detail_dialog.delete_event_signal.connect(self.delete_event)
        detail_dialog.exec()

    def new_date(self):
        date = self.calendar.selectedDate()
        self.date_label.setText(datetime.datetime(
            date.year(), date.month(), date.day()).strftime("%a, %d %b %Y"))

        self.reload()

    def edit_event(self, edited_event, index):
        if edited_event is not None:
            self.events[index] = edited_event
            self.events.sort()  # Sorting by Timing
            self.reload()

    def delete_event(self, index):
        self.events.pop(index)
        self.reload()

    def reload(self):
        date = self.calendar.selectedDate()
        for time, btn in enumerate(self.create_btn_lst):
            new_events_lst: List[Event] = []
            lower_bound = datetime.datetime(date.year(), date.month(), date.day(), time + 6, 0, 0)
            upper_bound = datetime.datetime(date.year(), date.month(), date.day(), time + 6, 59, 0)
            for event in self.events:
                if lower_bound <= event.timing <= upper_bound:
                    new_events_lst.append(event)

            if len(new_events_lst) != 0:
                btn.setText("\n".join([str(event) for event in new_events_lst]))
                self.details_label_lst[time].setText("\n".join([event.get_text() for event in new_events_lst]))
            else:
                btn.setText("")
                self.details_label_lst[time].setText("")

    def upload_to_firebase(self):
        try:
            for event in self.events:
                if event.media_file != "":
                    storage.child(f"schedules/{event.media_file}").put(event.media_file)

            pickle.dump(self.events, open("temp.pickle", "wb"))
            storage.child(f"schedules/{self.user_id}.pickle").put("temp.pickle")
        except Exception:
            print(traceback.format_exc())
