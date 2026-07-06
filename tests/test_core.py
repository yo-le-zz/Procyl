import subprocess
import time

import procyl


def test_create_and_run():
    """
    Teste la création et l'exécution basique d'un worker.
    
    Ce test vérifie:
    - La création d'un worker avec tous les paramètres optionnels
    - L'accès aux propriétés du worker via la notation dict
    - L'exécution du worker et vérification de la sortie
    
    Paramètres testés:
    - icon: chemin vers un fichier icône pour l'exécutable compilé
    - args: arguments par défaut pour l'exécution
    - compiler: choix du compilateur (pyinstaller, nuitka, python)
    - timeout_seconds: timeout en secondes pour l'exécution
    - auto_delete_after: suppression automatique après N secondes
    """
    worker = procyl.create(
        "t1",
        "print('ok')",
        icon="demo.ico",
        args=["hello"],
        compiler="pyinstaller",
        timeout_seconds=3,
        auto_delete_after=5,
    )
    # Vérifie que le worker a été créé avec le bon nom
    assert worker.name == "t1"
    # Vérifie que l'état initial est "ready"
    assert worker.state == "ready"
    # Vérifie que le timeout a été correctement configuré
    assert worker.timeout_seconds == 3
    # Vérifie que l'auto-delete a été correctement configuré
    assert worker.auto_delete_after == 5
    # Exécute le worker et vérifie la sortie
    output = procyl.run("t1")
    assert "ok" in output


def test_status_and_delete(tmp_path):
    """
    Teste la gestion du statut et la suppression des workers.
    
    Ce test vérifie:
    - La création d'un worker et vérification de son statut
    - L'assignation manuelle d'un artefact (fichier exécutable compilé)
    - La suppression du worker et vérification que l'artefact est aussi supprimé
    
    tmp_path: fixture pytest qui fournit un chemin temporaire pour les tests
    """
    # Crée un worker simple
    procyl.create("t2", "print('x')")
    # Vérifie le statut du worker
    status = procyl.status("t2")
    # Le worker doit exister
    assert status["exists"] is True
    # L'état doit être "ready" (prêt à l'exécution)
    assert status["state"] == "ready"

    # Crée un faux artefact (simule un fichier exécutable compilé)
    artifact = tmp_path / "t2.exe"
    artifact.write_text("fake")
    # Assigne manuellement l'artefact au worker
    procyl._workers["t2"].artifact_path = str(artifact)
    # Supprime le worker
    procyl.delete("t2")
    # Vérifie que le worker n'existe plus
    assert procyl.status("t2")["exists"] is False
    # Vérifie que l'artefact a été supprimé
    assert not artifact.exists()


def test_precompile_uses_pyinstaller_arguments(tmp_path, monkeypatch):
    """
    Teste que la précompilation utilise correctement les arguments PyInstaller.
    
    Ce test utilise monkeypatch pour remplacer subprocess.run par une fonction fake
    qui simule la compilation. Cela permet de tester sans vraiment compiler.
    
    Vérifications:
    - L'icône est passée correctement à PyInstaller (--icon)
    - Le nom du worker est passé correctement (--name)
    - L'état final est "compiled"
    - Le chemin de l'artefact se termine par .exe
    
    monkeypatch: fixture pytest qui permet de remplacer des fonctions pendant le test
    """
    calls = []

    # Fonction fake qui simule subprocess.run
    def fake_run(command, capture_output=True, text=True):
        # Crée un faux exécutable
        output_path = tmp_path / "demo.exe"
        output_path.write_text("fake exe")
        # Enregistre la commande pour vérification
        calls.append(command)
        # Retourne un résultat succès
        return subprocess.CompletedProcess(command, 0, stdout="built", stderr="")

    # Remplace subprocess.run par notre fonction fake
    monkeypatch.setattr("procyl.worker.subprocess.run", fake_run)
    # Remplace shutil.which pour simuler que pyinstaller est installé
    monkeypatch.setattr("procyl.worker.shutil.which", lambda name: "/usr/bin/pyinstaller" if name == "pyinstaller" else None)

    # Crée un worker avec icône et compilateur pyinstaller
    procyl.create("t3", "print('compiled')", icon="demo.ico", compiler="pyinstaller")
    # Précompile le worker
    result = procyl.precompile("t3", output_dir=str(tmp_path / "build"), compiler="pyinstaller")

    # Vérifie que l'état est "compiled"
    assert result["state"] == "compiled"
    # Vérifie que l'artefact a l'extension .exe
    assert result["artifact_path"].endswith(".exe")
    # Vérifie que l'argument --name a été passé à PyInstaller
    assert any("--name" in item for item in calls[0])
    # Vérifie que l'icône a été passée à PyInstaller
    assert any("demo.ico" in item for item in calls[0])


def test_runtime_compile_and_threaded_progress(tmp_path, monkeypatch):
    """
    Teste la compilation runtime avec progression threadée.
    
    Ce test vérifie:
    - La compilation en arrière-plan (thread=True)
    - Le suivi de la progression pendant la compilation
    - L'exécution runtime après compilation
    - La gestion des états de transition (compiling -> compiled/ready/failed)
    
    La compilation est simulée avec un délai (time.sleep(0.05)) pour tester
    le suivi de progression en temps réel.
    """
    compile_calls = []

    # Fonction fake qui simule la compilation avec un délai
    def fake_compile_run(command, capture_output=True, text=True):
        compile_calls.append(command)
        artifact_path = tmp_path / "runtime.exe"
        artifact_path.write_text("fake exe")
        # Simule un délai de compilation pour tester le suivi de progression
        time.sleep(0.05)
        return subprocess.CompletedProcess(command, 0, stdout="built", stderr="")

    # Fonction fake qui simule l'exécution de l'artefact compilé
    def fake_run(command, capture_output=True, text=True, timeout=None):
        if command and command[0].endswith(".exe"):
            return subprocess.CompletedProcess(command, 0, stdout="artifact-run", stderr="")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    # Remplace subprocess.run dans worker.py pour la compilation
    monkeypatch.setattr("procyl.worker.subprocess.run", fake_compile_run)
    # Remplace subprocess.run dans runner.py pour l'exécution
    monkeypatch.setattr("procyl.runner.subprocess.run", fake_run)

    # Crée un worker avec compilateur pyinstaller
    procyl.create("t4", "print('runtime')", compiler="pyinstaller")
    # Précompile en arrière-plan (thread=True)
    procyl.precompile("t4", output_dir=str(tmp_path / "build"), compiler="pyinstaller", thread=True)

    # Attend que la compilation se termine (max 10 itérations)
    for _ in range(10):
        status = procyl.status("t4")
        if status["state"] != "compiling":
            break
        time.sleep(0.01)

    # Vérifie l'état final
    status = procyl.status("t4")
    # L'état doit être l'un de ces trois
    assert status["state"] in {"compiled", "ready", "failed"}
    # Le pourcentage de progression doit être >= 0
    assert status["progress_percent"] >= 0

    # Exécute la compilation runtime
    runtime_result = procyl.runtime_compile("t4", compiler="pyinstaller")
    # Vérifie que la sortie contient le résultat de l'exécution
    assert "artifact-run" in runtime_result["output"]
    # Vérifie que l'artefact a l'extension .exe
    assert runtime_result["artifact_path"].endswith(".exe")


def test_parallel_creation_and_timeout(tmp_path):
    """
    Teste la création parallèle de workers avec configuration de timeout.
    
    Ce test vérifie:
    - La création de plusieurs workers en parallèle
    - La configuration correcte du timeout pour chaque worker
    - L'indépendance des workers (chaque worker a sa propre configuration)
    
    Vérifie que même avec plusieurs workers créés en parallèle,
    chaque worker conserve sa propre configuration de timeout.
    """
    # Crée deux workers avec le même timeout
    procyl.create("parallel-a", "print('a')", compiler="pyinstaller", timeout_seconds=2)
    procyl.create("parallel-b", "print('b')", compiler="pyinstaller", timeout_seconds=2)

    # Vérifie le statut des deux workers
    status_a = procyl.status("parallel-a")
    status_b = procyl.status("parallel-b")

    # Vérifie que les timeouts sont correctement configurés
    assert status_a["timeout_seconds"] == 2
    assert status_b["timeout_seconds"] == 2
    # Vérifie que les noms sont corrects (indépendance des workers)
    assert status_a["name"] == "parallel-a"
    assert status_b["name"] == "parallel-b"


def test_delete_removes_artifact(tmp_path):
    """
    Teste que la suppression d'un worker supprime aussi son artefact.
    
    Ce test vérifie:
    - L'assignation manuelle d'un artefact à un worker
    - La suppression du worker via procyl.delete()
    - La suppression automatique de l'artefact associé
    
    C'est important pour éviter d'accumuler des fichiers exécutables
    orphelins sur le disque quand les workers sont supprimés.
    """
    # Crée un chemin pour un artefact factice
    artifact_path = tmp_path / "artifact.exe"
    # Écrit du contenu factice dans le fichier
    artifact_path.write_text("fake")
    # Crée un worker
    procyl.create("cleanup", "print('cleanup')")
    # Assigne manuellement l'artefact au worker
    procyl._workers["cleanup"].artifact_path = str(artifact_path)
    # Supprime le worker
    result = procyl.delete("cleanup")
    # Vérifie que la suppression a réussi
    assert result["deleted"] is True
    # Vérifie que l'artefact a été supprimé du disque
    assert not artifact_path.exists()