# pekopeko
a mobile game automation tool

Python + ADB

## Install
- install Android sdkmanager. https://developer.android.com/studio#downloads
- install platform-tools with sdkmanager. (sdkmanager "platform-tools")
- pip install easyocr

## port for mumu
\[win\]
adb connect 127.0.0.1:7555
adb shell

\[mac\]
adb kill-server && adb server && adb shell