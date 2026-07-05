import procyl

def test_create_and_run():
    procyl.create("t1", "print('ok')")
    output = procyl.run("t1")
    assert "ok" in output

def test_status():
    procyl.create("t2", "print('x')")
    assert procyl.status("t2") == "exists"
    assert procyl.status("fake") == "missing"

def test_delete():
    procyl.create("t3", "print('x')")
    procyl.delete("t3")
    assert procyl.status("t3") == "missing"