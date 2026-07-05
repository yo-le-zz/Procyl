import procyl

# Create workers
procyl.create("hello", """
print("Hello from Procyl!")
""")

procyl.create("math", """
result = 2 + 2
print("Result:", result)
""")

# Run workers
print(procyl.run("hello"))
print(procyl.run("math"))

# Status check
print(procyl.status("hello"))
print(procyl.status("unknown"))

# Delete worker
procyl.delete("hello")
print(procyl.status("hello"))