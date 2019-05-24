from __future__ import division

import re
import sys

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
from google.oauth2 import service_account
import websockets
from threading import Thread
from PyQt5.QtCore import QEvent

HOST = "localhost"
PORT = 5500

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
    num_chars_printed = 0
    for response in responses:
        print("Inside For")
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))
        ex.textbox.setText(transcript + overwrite_chars + '\r')  

        if not result.is_final:
            # sys.stdout.write(transcript + overwrite_chars + '\r')
            # sys.stdout.write(transcript + overwrite_chars )
            # sys.stdout.flush()
            print("Inside If - called")
            num_chars_printed = len(transcript)
        else:
            print(transcript + overwrite_chars)

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break
            num_chars_printed = 0

def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    # language_code = 'en-US'  # a BCP-47 language tag te-IN en-IN
    language_code = 'en-IN'  # a BCP-47 language tag te-IN en-IN
    # language_code = 'ja-JP'  # a BCP-47 language tag te-IN
    # language_code = 'te-IN'  # a BCP-47 language tag te-IN 
    credentials = service_account.Credentials. from_service_account_file('googleKeys.json')

    # client = vision.ImageAnnotatorClient(credentials=credentials)
    # client = speech.SpeechClient()
    client = speech.SpeechClient(credentials=credentials)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)
"aasldalsd,alnsc asc as calsc alcaasldalsd,alnsc asc as cal,alnsc asc as calsc"
import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # QIcon
from PyQt5.QtCore import *  # pyqtSlot

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Speech - Text form integration'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 800
        self.initUI()
        self.namex = 20
        self.namey = 20
            
    def initUI(self):
        self.setWindowTitle(self.title)
        # self.setGeometry(self.left, self.top)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # Create textbox
        self.fieldName = QLabel(self)
        self.fieldName.setText('First Name:')
        self.fieldName.move(20, 20)

        self.textbox = QLineEdit(self)
        self.textbox.installEventFilter(self)
        self.textbox.move(120, 20)
        self.textbox.resize(280, 40)

        self.fieldName1 = QLabel(self)
        self.fieldName1.setText('Last Name:')
        self.fieldName1.move(20, 90)

        self.textbox1 = QLineEdit(self)
        self.textbox1.installEventFilter(self)
        self.textbox1.move(120, 90)
        self.textbox1.resize(280, 40)

        self.fieldName2 = QLabel(self)
        self.fieldName2.setText('Phone Number:')
        self.fieldName2.move(20, 160)

        self.textbox2 = QLineEdit(self)
        self.textbox2.installEventFilter(self)
        self.textbox2.move(120, 160)
        self.textbox2.resize(280, 40)

        self.fieldName3 = QLabel(self)
        self.fieldName3.setText('Address:')
        self.fieldName3.move(20, 230)

        self.textbox3 = QLineEdit(self)
        self.textbox3.move(120, 230)
        self.textbox3.resize(280, 40)
        # self.textbox3.mousePressEvent(self.press)
        # Create a button in the window
        self.button = QPushButton('Show text', self)
        self.button.move(420, 25)
        # self.button.move(20, 20)
        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.focused_box = obj
            print(obj)
        return super(App, self).eventFilter(obj, event)
    # def focusOutEvent(self, event):
    #     self.label.setText('Lost focus')
    
    # def focusInEvent(self, event):
    #     self.label.setText('Got focus')

    @pyqtSlot()
    def on_click(self):
        # textboxValue = self.textbox.text()
        # QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
        # self.textbox.setText("")
        self.press()

    def press(self):
        print("Im done.")
        Thread(target=main).start()



app = QApplication(sys.argv)
ex = App()
ex.focused_box = ex.textbox

# ex.button.move(300, 25)
# acn = App()
# acn.button.move(300, 55)
# acn.textbox.move(60, 20)

Thread(target=main).start()
sys.exit(app.exec_())