# Procyl

Procyl is a lightweight Python execution layer for managing isolated workers as named tasks. It allows defining and running Python code snippets as independent units using a simple API, with output captured through subprocess execution.

## Example

```python
import procyl

procyl.create("hello", """
print("Hello World")
""")

print(procyl.run("hello"))