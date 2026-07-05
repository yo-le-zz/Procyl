import threading

import procyl


def build_worker(name: str, code: str) -> None:
    procyl.create(name, code, compiler="pyinstaller")
    procyl.precompile(name, output_dir="./dist", compiler="pyinstaller", thread=True)


threads = [
    threading.Thread(target=build_worker, args=("worker-a", 'print("A")')),
    threading.Thread(target=build_worker, args=("worker-b", 'print("B")')),
]

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(procyl.status("worker-a"))
print(procyl.status("worker-b"))
