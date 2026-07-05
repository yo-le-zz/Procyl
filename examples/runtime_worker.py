import procyl

procyl.create(
    "runtime-demo",
    'print("Runtime compile and execute")',
    compiler="pyinstaller",
    timeout_seconds=5,
)

print(procyl.runtime_compile("runtime-demo", compiler="pyinstaller"))
