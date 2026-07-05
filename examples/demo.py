import procyl

procyl.create(
    "hello",
    'print("Hello from Procyl!")',
    icon="hello.png",
    args=["--demo"],
)

print(procyl.run("hello"))
print(procyl.precompile("hello", output_dir="./dist", compiler="python"))
print(procyl.runtime_compile("hello", compiler="python"))
print(procyl.status("hello"))
procyl.delete("hello")
print(procyl.status("hello"))