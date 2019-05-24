from __future__ import division

import re
import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # QIcon
from PyQt5.QtCore import *  # pyqtSlot
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets




from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
from google.oauth2 import service_account
import websockets
from threading import Thread
# from PyQt5.QtCore import QEvent

# HOST = "localhost"
# PORT = 5500

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    print("listen - called")
    global ex
    global stri
    num_chars_printed = 0
    for response in responses:
        # print("Inside For")
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            # sys.stdout.write(transcript + overwrite_chars + '\r')
            # sys.stdout.write(transcript + overwrite_chars )
            # sys.stdout.flush()
            # print("Inside If - called")
            num_chars_printed = len(transcript)
            # ex.focused_box.setText(stri + transcript + overwrite_chars + '\r') 
            ex.focused_box.setText(transcript) 
            ex.focused_box.setFont(ex.myFont)
            # ex.focused_box.setText(transcript + overwrite_chars + '\r') 

            # ex.focused_box.setText(str(ex.focused_box.text) + transcript + overwrite_chars + '\r') 
        else:
            # stri += transcript
            # ex.focused_box.setText(stri)
            # ex.focused_box.text += transcript
            # ex.focused_box.setText(str(ex.focused_box.text) 
            # print(transcript + overwrite_chars)
            ex.focused_box.setText(transcript) 
            ex.focused_box.setFont(ex.myFontNormal)
            # ex.focused_box.setText(transcript + overwrite_chars + '\r') 


            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break
            num_chars_printed = 0

def main():
    try:
        # language_code = 'en-US'  # a BCP-47 language tag te-IN en-IN
        language_code = 'en-IN'  # a BCP-47 language tag te-IN en-IN
        credentials = service_account.Credentials. from_service_account_file('googleKeys.json')
        client = speech.SpeechClient(credentials=credentials)
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        with MicrophoneStream(RATE, CHUNK) as stream:
            print("inside stream")
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            listen_print_loop(responses)
    except Exception as e: 
        print(str(e))
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt")


class App(QMainWindow):
    c1fnx = 15  # column 1 FieldName x - coordinates
    c2fnx = 375  # column 2 FieldName x - coordinates
    c3fnx = 735  # column 3 FieldName x - coordinates
    c4fnx = 1110  # column 4 FieldName x - coordinates

    c1tbx = 160  # column 1 TextBox x - coordinates
    c2tbx = 520  # column 2 TextBox x - coordinates
    c3tbx = 900  # column 3 TextBox x - coordinates
    c4tbx = 1250  # column 3 TextBox x - coordinates

    tbx = 175  # TextBox x/width
    tby = 30  # TextBox y/height

    def __init__(self):
        super().__init__()
        self.title = 'Bank Form | Speech - Text integration'
        self.left = 10
        self.top = 10
        self.width = 1500
        self.height = 800
        self.initUI()
        # self.setupUi(QMainWindow)

    # def setupUi(self, Interface):

    #     self.centralWidget = QtWidgets.QWidget(Interface)
    #     layout = QtWidgets.QVBoxLayout(self.centralWidget)

    #     self.scrollArea = QtWidgets.QScrollArea(self.centralWidget)

    #     layout.addWidget(self.scrollArea)

    #     self.scrollAreaWidgetContents = QtWidgets.QWidget()
    #     self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1112, 932))

    #     self.scrollArea.setWidget(self.scrollAreaWidgetContents)
    #     layout = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
    

    #     Interface.setCentralWidget(self.centralWidget)

    def initUI(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.myFont = QtGui.QFont()
        self.myFont.setBold(True)
        self.myFontNormal = QtGui.QFont()
        self.myFontNormal.setBold(False)

        # Coulmn 1 
        self.c1FieldName = QLabel(self)
        self.c1FieldName.setText('Scheme Code')
        self.c1FieldName.move(App.c1fnx, 20)

        self.c1TextBox = QLineEdit(self)
        self.c1TextBox.installEventFilter(self)
        self.c1TextBox.move(App.c1tbx, 20)
        self.c1TextBox.resize(App.tbx, App.tby)
        self.c1TextBoxs = ""

        self.c1FieldName1 = QLabel(self)
        self.c1FieldName1.setText('Customer ID')
        self.c1FieldName1.move(App.c1fnx, 60)

        self.c1TextBox1 = QLineEdit(self)
        self.c1TextBox1.installEventFilter(self)
        self.c1TextBox1.move(App.c1tbx, 60)
        self.c1TextBox1.resize(App.tbx, App.tby)
        # self.c1TextBox1s = "newn"
        # self.c1TextBox1.setText(self.c1TextBox1s)

        self.c1FieldName2 = QLabel(self)
        self.c1FieldName2.setText('Account No.')
        self.c1FieldName2.move(App.c1fnx, 100)

        self.c1TextBox2 = QLineEdit(self)
        self.c1TextBox2.installEventFilter(self)
        self.c1TextBox2.move(App.c1tbx, 100)
        self.c1TextBox2.resize(App.tbx, App.tby)
        self.c1TextBox2s = ""

        self.c1FieldName3 = QLabel(self)
        self.c1FieldName3.setText('Date')
        self.c1FieldName3.move(App.c1fnx, 140)

        self.c1TextBox3 = QLineEdit(self)
        self.c1TextBox3.installEventFilter(self)
        self.c1TextBox3.move(App.c1tbx, 140)
        self.c1TextBox3.resize(App.tbx, App.tby)
        self.c1TextBox3s = ""

        self.c1FieldName4 = QLabel(self)
        self.c1FieldName4.setText('Label Code')
        self.c1FieldName4.move(App.c1fnx, 180)

        self.c1TextBox4 = QLineEdit(self)
        self.c1TextBox4.installEventFilter(self)
        self.c1TextBox4.move(App.c1tbx, 180)
        self.c1TextBox4.resize(App.tbx, App.tby)

        self.c1FieldName5 = QLabel(self)
        self.c1FieldName5.setText('Telex Code')
        self.c1FieldName5.move(App.c1fnx, 220)

        self.c1TextBox5 = QLineEdit(self)
        self.c1TextBox5.installEventFilter(self)
        self.c1TextBox5.move(App.c1tbx, 220)
        self.c1TextBox5.resize(App.tbx, App.tby)

        self.c1FieldName6 = QLabel(self)
        self.c1FieldName6.setText('Name & No. of BC')
        # self.c1FieldName6.move(App.c1fnx, 260)
        self.c1FieldName6.setGeometry(QtCore.QRect(App.c1fnx, 260, 120, 30))  # (x, y, width, height)

        self.c1TextBox6 = QLineEdit(self)
        self.c1TextBox6.installEventFilter(self)
        self.c1TextBox6.move(App.c1tbx, 260)
        self.c1TextBox6.resize(App.tbx, App.tby)

        self.c1FieldName7 = QLabel(self)
        self.c1FieldName7.setText('Name of the Branch')
        # self.c1FieldName7.move(App.c1fnx, 300)
        self.c1FieldName7.setGeometry(QtCore.QRect(App.c1fnx, 300, 120, 30))  # (x, y, width, height)

        self.c1TextBox7 = QLineEdit(self)
        self.c1TextBox7.installEventFilter(self)
        self.c1TextBox7.move(App.c1tbx, 300)
        self.c1TextBox7.resize(App.tbx, App.tby)

        self.c1FieldName8 = QLabel(self)
        self.c1FieldName8.setText('Village / Town')
        self.c1FieldName8.move(App.c1fnx, 340)

        self.c1TextBox8 = QLineEdit(self)
        self.c1TextBox8.installEventFilter(self)
        self.c1TextBox8.move(App.c1tbx, 340)
        self.c1TextBox8.resize(App.tbx, App.tby)

        self.c1FieldName9 = QLabel(self)
        self.c1FieldName9.setText('Sub District / Block')
        # self.c1FieldName9.move(App.c1fnx, 380)
        self.c1FieldName9.setGeometry(QtCore.QRect(App.c1fnx, 380, 120, 30))  # (x, y, width, height)

        self.c1TextBox9 = QLineEdit(self)
        self.c1TextBox9.installEventFilter(self)
        self.c1TextBox9.move(App.c1tbx, 380)
        self.c1TextBox9.resize(App.tbx, App.tby)

        self.c1FieldName10 = QLabel(self)
        self.c1FieldName10.setText('District')
        self.c1FieldName10.move(App.c1fnx, 420)

        self.c1TextBox10 = QLineEdit(self)
        self.c1TextBox10.installEventFilter(self)
        self.c1TextBox10.move(App.c1tbx, 420)
        self.c1TextBox10.resize(App.tbx, App.tby)
    
        self.c1FieldName11 = QLabel(self)
        self.c1FieldName11.setText('State')
        self.c1FieldName11.move(App.c1fnx, 460)

        self.c1TextBox11 = QLineEdit(self)
        self.c1TextBox11.installEventFilter(self)
        self.c1TextBox11.move(App.c1tbx, 460)
        self.c1TextBox11.resize(App.tbx, App.tby)

        self.c1FieldName12 = QLabel(self)
        self.c1FieldName12.setText('SSA Code / Ward No.')
        # self.c1FieldName12.move(App.c1fnx, 500)
        self.c1FieldName12.setGeometry(QtCore.QRect(App.c1fnx, 500, 130, 30))  # (x, y, width, height)

        self.c1TextBox12 = QLineEdit(self)
        self.c1TextBox12.installEventFilter(self)
        self.c1TextBox12.move(App.c1tbx, 500)
        self.c1TextBox12.resize(App.tbx, App.tby)

        self.c1FieldName13 = QLabel(self)
        self.c1FieldName13.setText('Area Code')
        self.c1FieldName13.move(App.c1fnx, 540)

        self.c1TextBox13 = QLineEdit(self)
        self.c1TextBox13.installEventFilter(self)
        self.c1TextBox13.move(App.c1tbx, 540)
        self.c1TextBox13.resize(App.tbx, App.tby)

        self.c1FieldName14 = QLabel(self)
        self.c1FieldName14.setText('Name of Applicant')
        # self.c1FieldName14.move(App.c1fnx, 580)
        self.c1FieldName14.setGeometry(QtCore.QRect(App.c1fnx, 580, 120, 30))  # (x, y, width, height)

        self.c1TextBox14 = QLineEdit(self)
        self.c1TextBox14.installEventFilter(self)
        self.c1TextBox14.move(App.c1tbx, 580)
        self.c1TextBox14.resize(App.tbx, App.tby)

        self.c1FieldName15 = QLabel(self)
        self.c1FieldName15.setText('Father / Husband')
        # self.c1FieldName15.move(App.c1fnx, 620)
        self.c1FieldName15.setGeometry(QtCore.QRect(App.c1fnx, 620, 150, 30))  # (x, y, width, height)

        self.c1TextBox15 = QLineEdit(self)
        self.c1TextBox15.installEventFilter(self)
        self.c1TextBox15.move(App.c1tbx, 620)
        self.c1TextBox15.resize(App.tbx, App.tby)

        self.c1FieldName16 = QLabel(self)
        self.c1FieldName16.setText("Mother's maiden Name")
        # self.c1FieldName16.move(App.c1fnx, 660)
        self.c1FieldName16.setGeometry(QtCore.QRect(App.c1fnx, 660, 150, 30))  # (x, y, width, height)

        self.c1TextBox16 = QLineEdit(self)
        self.c1TextBox16.installEventFilter(self)
        self.c1TextBox16.move(App.c1tbx, 660)
        self.c1TextBox16.resize(App.tbx, App.tby)

        self.c1FieldName17 = QLabel(self)
        self.c1FieldName17.setText('Gender')
        self.c1FieldName17.move(App.c1fnx, 700)

        self.c1TextBox17 = QLineEdit(self)
        self.c1TextBox17.installEventFilter(self)
        self.c1TextBox17.move(App.c1tbx, 700)
        self.c1TextBox17.resize(App.tbx, App.tby)

        self.c1FieldName18 = QLabel(self)
        self.c1FieldName18.setText('Marital Status')
        self.c1FieldName18.move(App.c1fnx, 740)

        self.c1TextBox18 = QLineEdit(self)
        self.c1TextBox18.installEventFilter(self)
        self.c1TextBox18.move(App.c1tbx, 740)
        self.c1TextBox18.resize(App.tbx, App.tby)

        # Column 2

        self.c2FieldName = QLabel(self)
        self.c2FieldName.setText('Date of Birth')
        self.c2FieldName.move(App.c2fnx, 20)

        self.c2TextBox = QLineEdit(self)
        self.c2TextBox.installEventFilter(self)
        self.c2TextBox.move(App.c2tbx, 20)
        self.c2TextBox.resize(App.tbx, App.tby)
        self.c2TextBoxs = ""

        self.c2FieldName1 = QLabel(self)
        self.c2FieldName1.setText('Religion')
        self.c2FieldName1.move(App.c2fnx, 60)

        self.c2TextBox1 = QLineEdit(self)
        self.c2TextBox1.installEventFilter(self)
        self.c2TextBox1.move(App.c2tbx, 60)
        self.c2TextBox1.resize(App.tbx, App.tby)
        # self.c2TextBox1s = "newn"
        # self.c2TextBox1.setText(self.c2TextBox1s)

        self.c2FieldName2 = QLabel(self)
        self.c2FieldName2.setText('Caste')
        self.c2FieldName2.move(App.c2fnx, 100)

        self.c2TextBox2 = QLineEdit(self)
        self.c2TextBox2.installEventFilter(self)
        self.c2TextBox2.move(App.c2tbx, 100)
        self.c2TextBox2.resize(App.tbx, App.tby)
        self.c2TextBox2s = ""

        self.c2FieldName3 = QLabel(self)
        self.c2FieldName3.setText('Address:')
        self.c2FieldName3.move(App.c2fnx - 10, 140)
        self.c2FieldName3.setFont(self.myFont)

        # self.c2TextBox3 = QLineEdit(self)
        # self.c2TextBox3.installEventFilter(self)
        # self.c2TextBox3.move(App.c2tbx, 140)
        # self.c2TextBox3.resize(App.tbx, App.tby)
        # self.c2TextBox3s = ""

        self.c2FieldName4 = QLabel(self)
        self.c2FieldName4.setText('Building')
        self.c2FieldName4.move(App.c2fnx, 180)

        self.c2TextBox4 = QLineEdit(self)
        self.c2TextBox4.installEventFilter(self)
        self.c2TextBox4.move(App.c2tbx, 180)
        self.c2TextBox4.resize(App.tbx, App.tby)

        self.c2FieldName5 = QLabel(self)
        self.c2FieldName5.setText('Street No. / Name')
        # self.c2FieldName5.move(App.c2fnx, 220)
        self.c2FieldName5.setGeometry(QtCore.QRect(App.c2fnx, 220, 120, 30))  # (x, y, width, height)

        self.c2TextBox5 = QLineEdit(self)
        self.c2TextBox5.installEventFilter(self)
        self.c2TextBox5.move(App.c2tbx, 220)
        self.c2TextBox5.resize(App.tbx, App.tby)

        self.c2FieldName6 = QLabel(self)
        self.c2FieldName6.setText('Locality')
        self.c2FieldName6.move(App.c2fnx, 260)

        self.c2TextBox6 = QLineEdit(self)
        self.c2TextBox6.installEventFilter(self)
        self.c2TextBox6.move(App.c2tbx, 260)
        self.c2TextBox6.resize(App.tbx, App.tby)

        self.c2FieldName7 = QLabel(self)
        self.c2FieldName7.setText('Landmark')
        self.c2FieldName7.move(App.c2fnx, 300)

        self.c2TextBox7 = QLineEdit(self)
        self.c2TextBox7.installEventFilter(self)
        self.c2TextBox7.move(App.c2tbx, 300)
        self.c2TextBox7.resize(App.tbx, App.tby)

        self.c2FieldName8 = QLabel(self)
        self.c2FieldName8.setText('Village / City')
        self.c2FieldName8.move(App.c2fnx, 340)

        self.c2TextBox8 = QLineEdit(self)
        self.c2TextBox8.installEventFilter(self)
        self.c2TextBox8.move(App.c2tbx, 340)
        self.c2TextBox8.resize(App.tbx, App.tby)

        self.c2FieldName9 = QLabel(self)
        self.c2FieldName9.setText('District')
        self.c2FieldName9.move(App.c2fnx, 380)

        self.c2TextBox9 = QLineEdit(self)
        self.c2TextBox9.installEventFilter(self)
        self.c2TextBox9.move(App.c2tbx, 380)
        self.c2TextBox9.resize(App.tbx, App.tby)

        self.c2FieldName10 = QLabel(self)
        self.c2FieldName10.setText('State')
        self.c2FieldName10.move(App.c2fnx, 420)

        self.c2TextBox10 = QLineEdit(self)
        self.c2TextBox10.installEventFilter(self)
        self.c2TextBox10.move(App.c2tbx, 420)
        self.c2TextBox10.resize(App.tbx, App.tby)
    
        self.c2FieldName11 = QLabel(self)
        self.c2FieldName11.setText('Pincode')
        self.c2FieldName11.move(App.c2fnx, 460)

        self.c2TextBox11 = QLineEdit(self)
        self.c2TextBox11.installEventFilter(self)
        self.c2TextBox11.move(App.c2tbx, 460)
        self.c2TextBox11.resize(App.tbx, App.tby)

        self.c2FieldName12 = QLabel(self)
        self.c2FieldName12.setText('Mobile No.')
        self.c2FieldName12.move(App.c2fnx, 500)

        self.c2TextBox12 = QLineEdit(self)
        self.c2TextBox12.installEventFilter(self)
        self.c2TextBox12.move(App.c2tbx, 500)
        self.c2TextBox12.resize(App.tbx, App.tby)

        self.c2FieldName13 = QLabel(self)
        self.c2FieldName13.setText('Landline No.')
        self.c2FieldName13.move(App.c2fnx, 540)

        self.c2TextBox13 = QLineEdit(self)
        self.c2TextBox13.installEventFilter(self)
        self.c2TextBox13.move(App.c2tbx, 540)
        self.c2TextBox13.resize(App.tbx, App.tby)

        self.c2FieldName14 = QLabel(self)
        self.c2FieldName14.setText('E-mail ID')
        self.c2FieldName14.move(App.c2fnx, 580)

        self.c2TextBox14 = QLineEdit(self)
        self.c2TextBox14.installEventFilter(self)
        self.c2TextBox14.move(App.c2tbx, 580)
        self.c2TextBox14.resize(App.tbx, App.tby)

        self.c2FieldName15 = QLabel(self)
        self.c2FieldName15.setText('PAN No.')
        self.c2FieldName15.move(App.c2fnx, 620)

        self.c2TextBox15 = QLineEdit(self)
        self.c2TextBox15.installEventFilter(self)
        self.c2TextBox15.move(App.c2tbx, 620)
        self.c2TextBox15.resize(App.tbx, App.tby)

        self.c2FieldName16 = QLabel(self)
        self.c2FieldName16.setText('Aadhar No. / EID No.')
        # self.c2FieldName16.move(App.c2fnx, 660)
        self.c2FieldName16.setGeometry(QtCore.QRect(App.c2fnx, 660, 150, 30))  # (x, y, width, height)

        self.c2TextBox16 = QLineEdit(self)
        self.c2TextBox16.installEventFilter(self)
        self.c2TextBox16.move(App.c2tbx, 660)
        self.c2TextBox16.resize(App.tbx, App.tby)

        self.c2FieldName17 = QLabel(self)
        self.c2FieldName17.setText('Link Aadhar')
        self.c2FieldName17.move(App.c2fnx, 700)

        self.c2TextBox17 = QLineEdit(self)
        self.c2TextBox17.installEventFilter(self)
        self.c2TextBox17.move(App.c2tbx, 700)
        self.c2TextBox17.resize(App.tbx, App.tby)

        self.c2FieldName18 = QLabel(self)
        self.c2FieldName18.setText('MNREGA Job Card No.')
        self.c2FieldName18.move(App.c2fnx, 740)
        self.c2FieldName18.setGeometry(QtCore.QRect(App.c2fnx, 740, 150, 30))  # (x, y, width, height)

        self.c2TextBox18 = QLineEdit(self)
        self.c2TextBox18.installEventFilter(self)
        self.c2TextBox18.move(App.c2tbx, 740)
        self.c2TextBox18.resize(App.tbx, App.tby)

        # Column 3

        self.c3FieldName = QLabel(self)
        self.c3FieldName.setText('Occupation')
        self.c3FieldName.move(App.c3fnx, 20)

        self.c3TextBox = QLineEdit(self)
        self.c3TextBox.installEventFilter(self)
        self.c3TextBox.move(App.c3tbx, 20)
        self.c3TextBox.resize(App.tbx, App.tby)
        self.c3TextBoxs = ""

        self.c3FieldName1 = QLabel(self)
        self.c3FieldName1.setText('Annual Income')
        self.c3FieldName1.move(App.c3fnx, 60)

        self.c3TextBox1 = QLineEdit(self)
        self.c3TextBox1.installEventFilter(self)
        self.c3TextBox1.move(App.c3tbx, 60)
        self.c3TextBox1.resize(App.tbx, App.tby)
        # self.c3TextBox1s = "newn"
        # self.c3TextBox1.setText(self.c3TextBox1s)

        self.c3FieldName2 = QLabel(self)
        self.c3FieldName2.setText('No. of Dependents')
        self.c3FieldName2.move(App.c3fnx, 100)

        self.c3TextBox2 = QLineEdit(self)
        self.c3TextBox2.installEventFilter(self)
        self.c3TextBox2.move(App.c3tbx, 100)
        self.c3TextBox2.resize(App.tbx, App.tby)
        self.c3TextBox2s = ""

        self.c3FieldName3 = QLabel(self)
        self.c3FieldName3.setText('Owning house')
        self.c3FieldName3.move(App.c3fnx, 140)

        self.c3TextBox3 = QLineEdit(self)
        self.c3TextBox3.installEventFilter(self)
        self.c3TextBox3.move(App.c3tbx, 140)
        self.c3TextBox3.resize(App.tbx, App.tby)
        self.c3TextBox3s = ""

        self.c3FieldName4 = QLabel(self)
        self.c3FieldName4.setText('Owning Farm')
        self.c3FieldName4.move(App.c3fnx, 180)

        self.c3TextBox4 = QLineEdit(self)
        self.c3TextBox4.installEventFilter(self)
        self.c3TextBox4.move(App.c3tbx, 180)
        self.c3TextBox4.resize(App.tbx, App.tby)

        self.c3FieldName5 = QLabel(self)
        self.c3FieldName5.setText('No. of Animals')
        self.c3FieldName5.move(App.c3fnx, 220)

        self.c3TextBox5 = QLineEdit(self)
        self.c3TextBox5.installEventFilter(self)
        self.c3TextBox5.move(App.c3tbx, 220)
        self.c3TextBox5.resize(App.tbx, App.tby)

        self.c3FieldName6 = QLabel(self)
        self.c3FieldName6.setText('Existing Bank A/c.')
        # self.c3FieldName6.move(App.c3fnx, 260)
        self.c3FieldName6.setGeometry(QtCore.QRect(App.c3fnx, 260, 120, 30))  # (x, y, width, height)

        self.c3TextBox6a = QLineEdit(self)
        self.c3TextBox6a.installEventFilter(self)
        self.c3TextBox6a.move(App.c3tbx, 260)
        self.c3TextBox6a.resize(App.tbx - 135, App.tby)

        self.c3TextBox6b = QLineEdit(self)
        self.c3TextBox6b.installEventFilter(self)
        self.c3TextBox6b.move(App.c3tbx + 50, 260)
        self.c3TextBox6b.resize(App.tbx - 50, App.tby)

        self.c3FieldName7 = QLabel(self)
        self.c3FieldName7.setText('Kisan CC')
        # self.c3FieldName7.move(App.c3fnx, 300)
        self.c3FieldName7.setGeometry(QtCore.QRect(App.c3fnx, 300, 120, 30))  # (x, y, width, height)

        self.c3TextBox7 = QLineEdit(self)
        self.c3TextBox7.installEventFilter(self)
        self.c3TextBox7.move(App.c3tbx, 300)
        self.c3TextBox7.resize(App.tbx, App.tby)

        self.c3FieldName8 = QLabel(self)
        self.c3FieldName8.setText('RuPay Card')
        self.c3FieldName8.move(App.c3fnx, 340)

        self.c3TextBox8 = QLineEdit(self)
        self.c3TextBox8.installEventFilter(self)
        self.c3TextBox8.move(App.c3tbx, 340)
        self.c3TextBox8.resize(App.tbx, App.tby)

        self.c3FieldName9 = QLabel(self)
        self.c3FieldName9.setText("Guardian's Name")
        # self.c3FieldName9.move(App.c3fnx, 380)
        self.c3FieldName9.setGeometry(QtCore.QRect(App.c3fnx, 380, 150, 30))  # (x, y, width, height)

        self.c3TextBox9 = QLineEdit(self)
        self.c3TextBox9.installEventFilter(self)
        self.c3TextBox9.move(App.c3tbx, 380)
        self.c3TextBox9.resize(App.tbx, App.tby)

        self.c3FieldName10 = QLabel(self)
        self.c3FieldName10.setText('DOB Minor')
        self.c3FieldName10.move(App.c3fnx, 420)

        self.c3TextBox10 = QLineEdit(self)
        self.c3TextBox10.installEventFilter(self)
        self.c3TextBox10.move(App.c3tbx, 420)
        self.c3TextBox10.resize(App.tbx, App.tby)
    
        self.c3FieldName11 = QLabel(self)
        self.c3FieldName11.setText('DOB Guardian')
        self.c3FieldName11.move(App.c3fnx, 460)

        self.c3TextBox11 = QLineEdit(self)
        self.c3TextBox11.installEventFilter(self)
        self.c3TextBox11.move(App.c3tbx, 460)
        self.c3TextBox11.resize(App.tbx, App.tby)

        self.c3FieldName12 = QLabel(self)
        self.c3FieldName12.setText('Realtionship')
        self.c3FieldName12.move(App.c3fnx, 500)

        self.c3TextBox12 = QLineEdit(self)
        self.c3TextBox12.installEventFilter(self)
        self.c3TextBox12.move(App.c3tbx, 500)
        self.c3TextBox12.resize(App.tbx, App.tby)

        self.c3FieldName13 = QLabel(self)
        self.c3FieldName13.setText('Instruction for Operation')
        # self.c3FieldName13.move(App.c3fnx, 540)
        self.c3FieldName13.setGeometry(QtCore.QRect(App.c3fnx, 540, 150, 30))  # (x, y, width, height)

        self.c3TextBox13 = QLineEdit(self)
        self.c3TextBox13.installEventFilter(self)
        self.c3TextBox13.move(App.c3tbx, 540)
        self.c3TextBox13.resize(App.tbx, App.tby)

        self.c3FieldName14 = QLabel(self)
        self.c3FieldName14.setText('Channel Services')
        # self.c3FieldName14.move(App.c3fnx, 580)
        self.c3FieldName14.setGeometry(QtCore.QRect(App.c3fnx, 580, 120, 30))  # (x, y, width, height)

        self.c3TextBox14 = QLineEdit(self)
        self.c3TextBox14.installEventFilter(self)
        self.c3TextBox14.move(App.c3tbx, 580)
        self.c3TextBox14.resize(App.tbx, App.tby)

        self.c3FieldName15 = QLabel(self)
        self.c3FieldName15.setText('Primary Card')
        # self.c3FieldName15.move(App.c3fnx, 620)
        self.c3FieldName15.setGeometry(QtCore.QRect(App.c3fnx, 620, 150, 30))  # (x, y, width, height)

        self.c3TextBox15 = QLineEdit(self)
        self.c3TextBox15.installEventFilter(self)
        self.c3TextBox15.move(App.c3tbx, 620)
        self.c3TextBox15.resize(App.tbx, App.tby)

        self.c3FieldName16 = QLabel(self)
        self.c3FieldName16.setText('Chequebook')
        self.c3FieldName16.move(App.c3fnx, 660)

        self.c3TextBox16 = QLineEdit(self)
        self.c3TextBox16.installEventFilter(self)
        self.c3TextBox16.move(App.c3tbx, 660)
        self.c3TextBox16.resize(App.tbx, App.tby)

        self.c3FieldName17 = QLabel(self)
        self.c3FieldName17.setText('Passbook')
        self.c3FieldName17.move(App.c3fnx, 700)

        self.c3TextBox17 = QLineEdit(self)
        self.c3TextBox17.installEventFilter(self)
        self.c3TextBox17.move(App.c3tbx, 700)
        self.c3TextBox17.resize(App.tbx, App.tby)

        self.c3FieldName18 = QLabel(self)
        self.c3FieldName18.setText('Statement')
        self.c3FieldName18.move(App.c3fnx, 740)

        self.c3TextBox18 = QLineEdit(self)
        self.c3TextBox18.installEventFilter(self)
        self.c3TextBox18.move(App.c3tbx, 740)
        self.c3TextBox18.resize(App.tbx, App.tby)

        # Column 4

        self.c4FieldName = QLabel(self)
        self.c4FieldName.setText('Want to Nominate')
        # self.c4FieldName.move(App.c4fnx, 20)
        self.c4FieldName.setGeometry(QtCore.QRect(App.c4fnx, 20, 120, 30))  # (x, y, width, height)

        self.c4TextBox = QLineEdit(self)
        self.c4TextBox.installEventFilter(self)
        self.c4TextBox.move(App.c4tbx, 20)
        self.c4TextBox.resize(App.tbx, App.tby)
        self.c4TextBoxs = ""

        self.c4FieldName1 = QLabel(self)
        self.c4FieldName1.setText('Name of the Nominee')
        self.c4FieldName1.move(App.c4fnx, 60)
        self.c4FieldName1.setGeometry(QtCore.QRect(App.c4fnx, 60, 150, 30))  # (x, y, width, height)

        self.c4TextBox1 = QLineEdit(self)
        self.c4TextBox1.installEventFilter(self)
        self.c4TextBox1.move(App.c4tbx, 60)
        self.c4TextBox1.resize(App.tbx, App.tby)
        # self.c4TextBox1s = "newn"
        # self.c4TextBox1.setText(self.c4TextBox1s)

        self.c4FieldName2 = QLabel(self)
        self.c4FieldName2.setText('Relationship')
        self.c4FieldName2.move(App.c4fnx, 100)

        self.c4TextBox2 = QLineEdit(self)
        self.c4TextBox2.installEventFilter(self)
        self.c4TextBox2.move(App.c4tbx, 100)
        self.c4TextBox2.resize(App.tbx, App.tby)
        self.c4TextBox2s = ""

        self.c4FieldName3 = QLabel(self)
        self.c4FieldName3.setText('Age')
        self.c4FieldName3.move(App.c4fnx, 140)

        self.c4TextBox3 = QLineEdit(self)
        self.c4TextBox3.installEventFilter(self)
        self.c4TextBox3.move(App.c4tbx, 140)
        self.c4TextBox3.resize(App.tbx, App.tby)
        self.c4TextBox3s = ""

        self.c4FieldName4 = QLabel(self)
        self.c4FieldName4.setText('DOB Minor')
        self.c4FieldName4.move(App.c4fnx, 180)

        self.c4TextBox4 = QLineEdit(self)
        self.c4TextBox4.installEventFilter(self)
        self.c4TextBox4.move(App.c4tbx, 180)
        self.c4TextBox4.resize(App.tbx, App.tby)

        self.c4FieldName5 = QLabel(self)
        self.c4FieldName5.setText('Authorised Name')
        # self.c4FieldName5.move(App.c4fnx, 220)
        self.c4FieldName5.setGeometry(QtCore.QRect(App.c4fnx, 220, 120, 30))  # (x, y, width, height)

        self.c4TextBox5 = QLineEdit(self)
        self.c4TextBox5.installEventFilter(self)
        self.c4TextBox5.move(App.c4tbx, 220)
        self.c4TextBox5.resize(App.tbx, App.tby)

        self.c4FieldName6 = QLabel(self)
        self.c4FieldName6.setText('Tax Purposes')
        # self.c4FieldName6.move(App.c4fnx, 260)
        self.c4FieldName6.setGeometry(QtCore.QRect(App.c4fnx, 260, 120, 30))  # (x, y, width, height)

        self.c4TextBox6 = QLineEdit(self)
        self.c4TextBox6.installEventFilter(self)
        self.c4TextBox6.move(App.c4tbx, 260)
        self.c4TextBox6.resize(App.tbx, App.tby)

        self.c4FieldName7 = QLabel(self)
        self.c4FieldName7.setText('Place')
        self.c4FieldName7.move(App.c4fnx, 300)

        self.c4TextBox7 = QLineEdit(self)
        self.c4TextBox7.installEventFilter(self)
        self.c4TextBox7.move(App.c4tbx, 300)
        self.c4TextBox7.resize(App.tbx, App.tby)

        self.c4FieldName8 = QLabel(self)
        self.c4FieldName8.setText('Date')
        self.c4FieldName8.move(App.c4fnx, 340)

        self.c4TextBox8 = QLineEdit(self)
        self.c4TextBox8.installEventFilter(self)
        self.c4TextBox8.move(App.c4tbx, 340)
        self.c4TextBox8.resize(App.tbx, App.tby)

        self.c4FieldName9 = QLabel(self)
        self.c4FieldName9.setText('Acting Branch head')
        # self.c4FieldName9.move(App.c4fnx, 380)
        self.c4FieldName9.setGeometry(QtCore.QRect(App.c4fnx, 380, 120, 30))  # (x, y, width, height)

        self.c4TextBox9 = QLineEdit(self)
        self.c4TextBox9.installEventFilter(self)
        self.c4TextBox9.move(App.c4tbx, 380)
        self.c4TextBox9.resize(App.tbx, App.tby)

        self.c4FieldName10 = QLabel(self)
        self.c4FieldName10.setText('Risk Level Code')
        # self.c4FieldName10.move(App.c4fnx, 420)
        self.c4FieldName10.setGeometry(QtCore.QRect(App.c4fnx, 420, 150, 30))  # (x, y, width, height)

        self.c4TextBox10 = QLineEdit(self)
        self.c4TextBox10.installEventFilter(self)
        self.c4TextBox10.move(App.c4tbx, 420)
        self.c4TextBox10.resize(App.tbx, App.tby)
    
        self.c4FieldName11 = QLabel(self)
        self.c4FieldName11.setText('Name of BC / BF')
        # self.c4FieldName11.move(App.c4fnx, 460)
        self.c4FieldName11.setGeometry(QtCore.QRect(App.c4fnx, 460, 150, 30))  # (x, y, width, height)

        self.c4TextBox11 = QLineEdit(self)
        self.c4TextBox11.installEventFilter(self)
        self.c4TextBox11.move(App.c4tbx, 460)
        self.c4TextBox11.resize(App.tbx, App.tby)

        self.c4FieldName12 = QLabel(self)
        self.c4FieldName12.setText('No. of BC / BF')
        # self.c4FieldName12.move(App.c4fnx, 500)
        self.c4FieldName12.setGeometry(QtCore.QRect(App.c4fnx, 500, 130, 30))  # (x, y, width, height)

        self.c4TextBox12 = QLineEdit(self)
        self.c4TextBox12.installEventFilter(self)
        self.c4TextBox12.move(App.c4tbx, 500)
        self.c4TextBox12.resize(App.tbx, App.tby)

        self.c4FieldName13 = QLabel(self)
        self.c4FieldName13.setText('Name of Official')
        self.c4FieldName13.move(App.c4fnx, 540)

        self.c4TextBox13 = QLineEdit(self)
        self.c4TextBox13.installEventFilter(self)
        self.c4TextBox13.move(App.c4tbx, 540)
        self.c4TextBox13.resize(App.tbx, App.tby)

        self.c4FieldName14 = QLabel(self)
        self.c4FieldName14.setText('Employee Code')
        # self.c4FieldName14.move(App.c4fnx, 580)
        self.c4FieldName14.setGeometry(QtCore.QRect(App.c4fnx, 580, 120, 30))  # (x, y, width, height)

        self.c4TextBox14 = QLineEdit(self)
        self.c4TextBox14.installEventFilter(self)
        self.c4TextBox14.move(App.c4tbx, 580)
        self.c4TextBox14.resize(App.tbx, App.tby)

        self.c4FieldName15 = QLabel(self)
        self.c4FieldName15.setText('Name of Branch')
        # self.c4FieldName15.move(App.c4fnx, 620)
        self.c4FieldName15.setGeometry(QtCore.QRect(App.c4fnx, 620, 150, 30))  # (x, y, width, height)

        self.c4TextBox15 = QLineEdit(self)
        self.c4TextBox15.installEventFilter(self)
        self.c4TextBox15.move(App.c4tbx, 620)
        self.c4TextBox15.resize(App.tbx, App.tby)

        self.c4FieldName16 = QLabel(self)
        self.c4FieldName16.setText('Code of Branch')
        # self.c4FieldName16.move(App.c4fnx, 660)
        self.c4FieldName16.setGeometry(QtCore.QRect(App.c4fnx, 660, 150, 30))  # (x, y, width, height)

        self.c4TextBox16 = QLineEdit(self)
        self.c4TextBox16.installEventFilter(self)
        self.c4TextBox16.move(App.c4tbx, 660)
        self.c4TextBox16.resize(App.tbx, App.tby)

        self.c4FieldName17 = QLabel(self)
        self.c4FieldName17.setText('Customer ID')
        self.c4FieldName17.move(App.c4fnx, 700)

        self.c4TextBox17 = QLineEdit(self)
        self.c4TextBox17.installEventFilter(self)
        self.c4TextBox17.move(App.c4tbx, 700)
        self.c4TextBox17.resize(App.tbx, App.tby)

        self.c4FieldName18 = QLabel(self)
        self.c4FieldName18.setText('Account No.')
        self.c4FieldName18.move(App.c4fnx, 740)

        self.c4TextBox18 = QLineEdit(self)
        self.c4TextBox18.installEventFilter(self)
        self.c4TextBox18.move(App.c4tbx, 740)
        self.c4TextBox18.resize(App.tbx, App.tby)



        # self.c1TextBox3.mousePressEvent(self.press)
        # Create a button in the window
        self.button = QPushButton('Show text', self)
        self.button.move(500, 800)
        # self.button.move(App.c1fnx, 20)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)

        self.show()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.focused_box = obj
            # print(obj)
            # if obj == self.c1TextBox:
            #     print("txtbox")
            #     self.c1TextBoxs = stri
            # if obj == self.c1TextBox1:
            #     print("txtbox1")
            #     self.c1TextBox1s = stri
            # if obj == self.c1TextBox2:
            #     print("txtbox2")
            #     self.c1TextBox2s = stri
            # if obj == self.c1TextBox3:
            #     print("txtbox3")
            #     self.c1TextBox3s = stri


        
        return super(App, self).eventFilter(obj, event)
    # def focusOutEvent(self, event):
    #     self.label.setText('Lost focus')
    # def focusInEvent(self, event):
    #     self.label.setText('Got focus')

    @pyqtSlot()
    def on_click(self):
        # c1TextBoxValue = self.c1TextBox.text()
        # QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + c1TextBoxValue, QMessageBox.Ok, QMessageBox.Ok)
        # self.c1TextBox.setText("")
        self.press()

    def press(self):
        print("Im done.")
        Thread(target=main).start()


app = QApplication(sys.argv)
ex = App()
# ex.focused_box = None
ex.focused_box = ex.c1TextBox
stri = ex.c1TextBoxs

Thread(target=main).start()
sys.exit(app.exec_())

