import time

import procyl

procyl.create(
    "threaded-demo",
    'print("Compiling in a thread")',
    compiler="pyinstaller",
)

procyl.precompile("threaded-demo", output_dir="./dist", compiler="pyinstaller", thread=True)

for _ in range(20):
    status = procyl.status("threaded-demo")
    print(status)
    if status["state"] != "compiling":
        break
    time.sleep(0.1)
