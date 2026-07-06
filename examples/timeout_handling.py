"""
Exemple de gestion des timeouts avec Procyl.

Cet exemple montre comment configurer et gérer les timeouts pour
les workers afin d'éviter les blocages et les exécutions trop longues.
"""

import procyl
import time

print("=" * 70)
print("Gestion des Timeouts avec Procyl")
print("=" * 70)

# ============================================================================
# Worker sans timeout (dangereux)
# ============================================================================

print("\n1. Worker sans timeout (dangereux)")
print("-" * 70)

no_timeout_worker = procyl.create(
    "no_timeout",
    '''
import time
print("Starting long task...")
time.sleep(10)  # 10 secondes - très long!
print("Task completed")
''',
)

print(f"Worker créé: {no_timeout_worker.name}")
print(f"Timeout configuré: {no_timeout_worker.timeout_seconds}")
print("\n⚠️  Ce worker peut bloquer indéfiniment s'il y a un problème!")

# ============================================================================
# Worker avec timeout raisonnable
# ============================================================================

print("\n2. Worker avec timeout raisonnable")
print("-" * 70)

timeout_worker = procyl.create(
    "timeout_worker",
    '''
import time
print("Starting task...")
time.sleep(2)  # 2 secondes
print("Task completed")
''',
    timeout_seconds=5,  # Timeout de 5 secondes
)

print(f"Worker créé: {timeout_worker.name}")
print(f"Timeout configuré: {timeout_worker.timeout_seconds} secondes")
print("✓ Ce worker sera interrompu après 5 secondes")

# ============================================================================
# Worker avec timeout court
# ============================================================================

print("\n3. Worker avec timeout court")
print("-" * 70)

short_timeout_worker = procyl.create(
    "short_timeout",
    '''
import time
print("Starting long task...")
time.sleep(10)  # 10 secondes - plus long que le timeout!
print("This may not print if timeout occurs")
''',
    timeout_seconds=2,  # Timeout de 2 secondes
)

print(f"Worker créé: {short_timeout_worker.name}")
print(f"Timeout configuré: {short_timeout_worker.timeout_seconds} secondes")
print("⚠️  Ce worker sera probablement interrompu (timeout: 2s, task: 10s)")

# ============================================================================
# Exécution avec timeout
# ============================================================================

print("\n4. Exécution avec timeout")
print("-" * 70)

print("Exécution du worker avec timeout raisonnable (5s):")
start = time.time()
try:
    result = procyl.run("timeout_worker")
    elapsed = time.time() - start
    print(f"✓ Exécution terminée en {elapsed:.2f}s")
    print(f"Résultat: {result.strip()}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Erreur après {elapsed:.2f}s: {e}")

print("\nExécution du worker avec timeout court (2s):")
start = time.time()
try:
    result = procyl.run("short_timeout")
    elapsed = time.time() - start
    print(f"✓ Exécution terminée en {elapsed:.2f}s")
    print(f"Résultat: {result.strip()}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Erreur après {elapsed:.2f}s: {e}")

# ============================================================================
# Worker avec timeout et tâche rapide
# ============================================================================

print("\n5. Worker avec timeout mais tâche rapide")
print("-" * 70)

fast_worker = procyl.create(
    "fast_worker",
    '''
import time
print("Quick task...")
time.sleep(0.1)  # 100ms - très rapide
print("Done")
''',
    timeout_seconds=10,  # Timeout généreux mais tâche rapide
)

print(f"Worker créé: {fast_worker.name}")
print(f"Timeout configuré: {fast_worker.timeout_seconds} secondes")
print("Tâche: 100ms")

print("\nExécution:")
start = time.time()
result = procyl.run("fast_worker")
elapsed = time.time() - start
print(f"✓ Exécution terminée en {elapsed:.2f}s")
print(f"Résultat: {result.strip()}")
print("Note: Le timeout n'est pas atteint car la tâche est rapide")

# ============================================================================
# Timeout avec exécution parallèle
# ============================================================================

print("\n6. Timeout avec exécution parallèle")
print("-" * 70)

parallel_timeout_worker = procyl.create(
    "parallel_timeout",
    '''
import time
import random
delay = random.uniform(0.5, 1.5)
print(f"Task with {delay:.2f}s delay")
time.sleep(delay)
print("Completed")
''',
    timeout_seconds=2,  # Timeout de 2 secondes
)

print(f"Worker créé: {parallel_timeout_worker.name}")
print(f"Timeout configuré: {parallel_timeout_worker.timeout_seconds} secondes")

print("\nExécution parallèle (4 workers):")
start = time.time()
try:
    results = parallel_timeout_worker.run(count=4)
    elapsed = time.time() - start
    print(f"✓ Toutes les exécutions terminées en {elapsed:.2f}s")
    for i, result in enumerate(results, 1):
        print(f"  Worker {i}: {result.strip()}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Erreur après {elapsed:.2f}s: {e}")

# ============================================================================
# Worker avec timeout conditionnel
# ============================================================================

print("\n7. Worker avec logique de timeout conditionnel")
print("-" * 70)

conditional_worker = procyl.create(
    "conditional_worker",
    '''
import sys
import time

# Récupère le mode depuis les arguments
mode = sys.argv[1] if len(sys.argv) > 1 else "fast"

if mode == "fast":
    print("Fast mode - quick task")
    time.sleep(0.1)
elif mode == "slow":
    print("Slow mode - long task")
    time.sleep(5)
else:
    print("Unknown mode")
''',
    timeout_seconds=2,  # Timeout de 2 secondes
)

print(f"Worker créé: {conditional_worker.name}")
print(f"Timeout configuré: {conditional_worker.timeout_seconds} secondes")

print("\nExécution en mode fast:")
start = time.time()
result = conditional_worker.run(count=1, args=["fast"])
elapsed = time.time() - start
print(f"✓ Terminé en {elapsed:.2f}s: {result.strip()}")

print("\nExécution en mode slow (probable timeout):")
start = time.time()
try:
    result = conditional_worker.run(count=1, args=["slow"])
    elapsed = time.time() - start
    print(f"✓ Terminé en {elapsed:.2f}s: {result.strip()}")
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Timeout après {elapsed:.2f}s: {e}")

# ============================================================================
# Worker avec retry et timeout
# ============================================================================

print("\n8. Worker avec retry et timeout")
print("-" * 70)

retry_worker = procyl.create(
    "retry_worker",
    '''
import sys
import time

# Récupère le nombre de tentatives
attempt = int(sys.argv[1]) if len(sys.argv) > 1 else 1
max_attempts = 3

print(f"Attempt {attempt}/{max_attempts}")

# Simule une tâche qui échoue parfois
if attempt < max_attempts:
    print("Task failed, will retry")
    sys.exit(1)
else:
    print("Task succeeded on final attempt")
''',
    timeout_seconds=3,  # Timeout de 3 secondes par tentative
)

print(f"Worker créé: {retry_worker.name}")
print(f"Timeout configuré: {retry_worker.timeout_seconds} secondes")

print("\nExécution avec retry manuel:")
for attempt in range(1, 4):
    start = time.time()
    try:
        result = retry_worker.run(count=1, args=[str(attempt)])
        elapsed = time.time() - start
        print(f"✓ Tentative {attempt} réussie en {elapsed:.2f}s")
        break
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ Tentative {attempt} échouée après {elapsed:.2f}s")

# ============================================================================
# Monitoring des timeouts
# ============================================================================

print("\n9. Monitoring des timeouts")
print("-" * 70)

workers_with_timeout = [
    "timeout_worker",
    "short_timeout",
    "fast_worker",
    "parallel_timeout",
    "conditional_worker",
    "retry_worker",
]

print("Configuration des timeouts:")
for worker_name in workers_with_timeout:
    status = procyl.status(worker_name)
    if status['exists']:
        timeout = status.get('timeout_seconds', 'Not set')
        print(f"  {worker_name:25} : {timeout} secondes")

# ============================================================================
# Best practices pour les timeouts
# ============================================================================

print("\n10. Best practices pour les timeouts")
print("-" * 70)

print("Recommandations:")
print("  1. Définissez toujours un timeout pour les workers en production")
print("  2. Utilisez des timeouts généreux (2-3x le temps normal)")
print("  3. Testez vos workers avec différents scénarios de timeout")
print("  4. Implémentez des mécanismes de retry pour les tâches critiques")
print("  5. Surveillez les timeouts pour détecter les problèmes de performance")
print("  6. Utilisez des timeouts différents selon le type de tâche")
print("  7. Documentez les timeouts attendus pour chaque worker")
print("  8. Considérez l'utilisation de timeouts adaptatifs")

print("\nExemples de timeouts par type de tâche:")
timeout_examples = {
    "Tâche rapide (< 1s)": "2-3 secondes",
    "Tâche normale (1-10s)": "15-30 secondes",
    "Tâche longue (10-60s)": "2-3 minutes",
    "Tâche très longue (> 1min)": "5-10 minutes",
}

for task_type, recommended_timeout in timeout_examples.items():
    print(f"  {task_type:30} : {recommended_timeout}")

# ============================================================================
# Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("Cleanup")
print("=" * 70)

all_workers = ["no_timeout", "timeout_worker", "short_timeout", 
               "fast_worker", "parallel_timeout", "conditional_worker", 
               "retry_worker"]

for worker_name in all_workers:
    try:
        result = procyl.delete(worker_name)
        print(f"Supprimé '{worker_name}': {result.get('deleted', False)}")
    except:
        print(f"Worker '{worker_name}' déjà supprimé ou inexistant")

print("\n" + "=" * 70)
print("Exemple terminé!")
print("=" * 70)
print("\nPoints clés:")
print("- Les timeouts sont essentiels pour éviter les blocages")
print("- Configurez des timeouts appropriés à chaque type de tâche")
print("- Testez toujours le comportement timeout de vos workers")
print("- Utilisez des mécanismes de retry pour les tâches critiques")
print("- Surveillez les timeouts pour détecter les problèmes de performance")
