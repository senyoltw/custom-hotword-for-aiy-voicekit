# custom-hotword-for-aiy-voicekit
Snowboy API for AIY Voice Kit.    
Replace your AIY Voice Kit hotword [OK. Google] to [alexa],[jarvis]...etc  
You can easily replace your program.  
See. [diff AIY Voice Kit Press button and own hotword program](#diff-original-programaiy-voice-kit-press-button-snowboy-wakeword-program)

# Before How to install
Buy The AIY Voice Kit and complete the tutorial.  
custom-hotword-for-aiy-voicekit use lowlevel api AIY Voice Kit.

https://aiyprojects.withgoogle.com/voice/

Are you work your voice kit this program?
```
src/examples/voice/assistant_grpc_demo.py
```
If the demo has worked,next step.

# How to install

```
cd /home/pi/
# libatlas-base-dev need snowboy module.
sudo apt-get install libatlas-base-dev
git clone https://github.com/senyoltw/custom-hotword-for-aiy-voicekit

# copy snowboy module and sample program.
cp -ipr custom-hotword-for-aiy-voicekit/mod AIY-projects-python/src/
cp -ip custom-hotword-for-aiy-voicekit/assistant_grpc_demo_snowboy.py AIY-projects-python/src/examples/voice/
```

# How to use

```
cd AIY-voice-kit-python
chmod a+x src/examples/voice/assistant_grpc_demo_snowboy.py
rc/examples/voice/assistant_grpc_demo_snowboy.py src/mod/resources/alexa_02092017.umdl
```
Say "alexa" and talk your google assistant!

sample log
```
pi@raspberrypi:~/AIY-voice-kit-python $ src/examples/voice/assistant_grpc_demo_snowboy.py src/mod/resources/alexa_02092017.umdl
/opt/aiy/projects-python/src/aiy/_drivers/_led.py:51: RuntimeWarning: This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.
  GPIO.setup(channel, GPIO.OUT)
[2018-06-03 13:40:32,643] INFO:recorder:started recording
Speak own hotword and speak
[2018-06-03 13:40:35,289] INFO:snowboy:Keyword 1 detected at time: 2018-06-03 13:40:35
Listening...
[2018-06-03 13:40:38,042] INFO:speech:transcript: What
[2018-06-03 13:40:38,049] INFO:speech:transcript: What is
[2018-06-03 13:40:38,051] INFO:speech:transcript: What is your
[2018-06-03 13:40:38,053] INFO:speech:transcript: What is your ね
[2018-06-03 13:40:38,055] INFO:speech:transcript: What is your name
[2018-06-03 13:40:38,056] INFO:speech:transcript: What  is your name
[2018-06-03 13:40:38,058] INFO:speech:transcript: What is  your name
[2018-06-03 13:40:38,060] INFO:speech:transcript: What is your  name
[2018-06-03 13:40:38,062] INFO:speech:event_type: 1
[2018-06-03 13:40:38,067] INFO:speech:transcript: What is your name
[2018-06-03 13:40:38,070] INFO:speech:transcript: What is your name
You said " What is your name "
Speak own hotword and speak
```

# Make your own hotword
Make your own hotword this site.   
and download your voice kit [hotword].pmdl  
(how to make your hotword by snowboy, google it ^^!)

https://snowboy.kitt.ai/

and run program argument your hotword

```
cd AIY-voice-kit-python
src/examples/voice/assistant_grpc_demo_snowboy.py [hotword].pmdl
```

# diff original program(AIY Voice Kit Press button), snowboy wakeword program
```
$ diff -u src/examples/voice/assistant_grpc_demo.py src/examples/voice/assistant_grpc_demo_snowboy.py
--- src/examples/voice/assistant_grpc_demo.py	2018-04-14 06:05:49.000000000 +0900
+++ src/examples/voice/assistant_grpc_demo_snowboy.py	2018-05-29 10:44:28.486009208 +0900
@@ -21,6 +21,16 @@
 import aiy.audio
 import aiy.voicehat

+import mod.snowboydecoder as snowboydecoder
+import sys
+
+if len(sys.argv) == 1:
+    print("Error: need to specify model name")
+    print("Usage: python demo.py your.model")
+    sys.exit(-1)
+
+model = sys.argv[1]
+
 logging.basicConfig(
     level=logging.INFO,
     format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
@@ -31,12 +41,15 @@
     status_ui = aiy.voicehat.get_status_ui()
     status_ui.status('starting')
     assistant = aiy.assistant.grpc.get_assistant()
-    button = aiy.voicehat.get_button()
+    #button = aiy.voicehat.get_button()
+    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
     with aiy.audio.get_recorder():
         while True:
             status_ui.status('ready')
-            print('Press the button and speak')
-            button.wait_for_press()
+            #print('Press the button and speak')
+            print('Speak own hotword and speak')
+            #button.wait_for_press()
+            detector.start()
             status_ui.status('listening')
             print('Listening...')
             text, audio = assistant.recognize()
$
```
