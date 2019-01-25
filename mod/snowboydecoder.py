#!/usr/bin/env python3

import collections
from . import snowboydetect
import time
import os
import logging

from aiy.voice.audio import AudioFormat, Recorder, play_wav

logger = logging.getLogger("snowboy")
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")

AUDIO_SAMPLE_RATE_HZ = 16000
AUDIO_FORMAT=AudioFormat(sample_rate_hz=AUDIO_SAMPLE_RATE_HZ,
                         num_channels=1,
                         bytes_per_sample=2)

def play_audio_file(fname=DETECT_DING):
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.

    :param str fname: wave file name
    :return: None
    """
    play_wave(fname)

def callbacks():
    global interrupted
    interrupted = True

def callbacks_and_play_audio_file(fname=DETECT_DING):
    """callback function to play a wave file and interrupted is true. By default it plays
    a Ding sound.

    :param str fname: wave file name
    :return: None
    """
    play_wave(fname)
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

class HotwordDetector(object):
    """
    Snowboy decoder to detect whether a keyword specified by `decoder_model`
    exists in a microphone input stream.

    :param decoder_model: decoder model file path, a string or a list of strings
    :param resource: resource file path.
    :param sensitivity: decoder sensitivity, a float of a list of floats.
                              The bigger the value, the more senstive the
                              decoder. If an empty list is provided, then the
                              default sensitivity in the model will be used.
    :param audio_gain: multiply input volume by this factor.
    """

    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity=[],
                 audio_gain=1):

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(audio_gain)
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity * self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

    def start(self, detected_callback=callbacks,
              interrupt_check=interrupt_callback,
              sleep_time=0.02):
        """
        Start the voice detector. For every `sleep_time` second it checks the
        audio buffer for triggering keywords. If detected, then call
        corresponding function in `detected_callback`, which can be a single
        function (single model) or a list of callback functions (multiple
        models). Every loop it also calls `interrupt_check` -- if it returns
        True, then breaks from the loop and return.

        :param detected_callback: a function or list of functions. The number of
                                  items must match the number of models in
                                  `decoder_model`.
        :param interrupt_check: a function that returns True if the main loop
                                needs to stop.
        :param float sleep_time: how much time in second every loop waits.
        :return: None
        """
        self._running = True

        global interrupted
        interrupted = False

        if interrupt_check():
            logger.debug("detect voice return")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "Error: hotwords in your models (%d) do not match the number of " \
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))

        logger.debug("detecting...")

        while self._running is True:
            with Recorder() as recorder:
                for data in recorder.record(AUDIO_FORMAT,
                                         chunk_duration_sec=0.02,
                                         on_start=self.start_detect,
                                         on_stop=self.stop_detect):

                    ans = self.detector.RunDetection(data)
                    if ans == -1:
                        logger.warning("Error initializing streams or reading audio data")
                        recorder.done()
                    elif ans > 0:
                        recorder.done()
                        message = "Keyword " + str(ans) + " detected at time: "
                        message += time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(time.time()))
                        logger.info(message)
                        callback = detected_callback[ans - 1]
                        if callback is not None:
                            callback()

            if interrupt_check():
                logger.debug("detect voice break")
                recorder.done()
                break
        logger.debug("finished.")

    def terminate(self):
        """
        Terminate audio stream. Users can call start() again to detect.
        :return: None
        """
        self._running = False

    def start_detect(self):
        logger.info('detect started.')

    def stop_detect(self):
        logger.info('detect stopped.')
