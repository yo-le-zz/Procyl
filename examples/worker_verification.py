"""
Exemple de vérification de workers avec Procyl.

Cet exemple montre comment utiliser la fonction worker.verify() pour
valider l'intégrité des workers avant leur exécution.
"""

import procyl

print("=" * 70)
print("Vérification de Workers avec Procyl")
print("=" * 70)

# ============================================================================
# Worker valide
# ============================================================================

print("\n1. Création et vérification d'un worker valide")
print("-" * 70)

valid_worker = procyl.create(
    "valid_worker",
    '''
import sys
print("Hello, World!")
print(f"Arguments: {sys.argv[1:]}")
''',
)

print(f"Worker créé: {valid_worker.name}")
print(f"Code:\n{valid_worker.code}")

# Vérifie le worker
verification = valid_worker.verify()
print(f"\nRésultat de la vérification:")
print(f"  Valid: {verification['valid']}")
print(f"  Name: {verification['name']}")
print(f"  Issues: {verification['issues']}")
if 'dependencies' in verification:
    print(f"  Dependencies: {verification['dependencies']}")

# ============================================================================
# Worker avec erreur de syntaxe
# ============================================================================

print("\n2. Création et vérification d'un worker avec erreur de syntaxe")
print("-" * 70)

invalid_syntax_worker = procyl.create(
    "invalid_syntax",
    '''
import sys
print("Hello, World!"
# Missing closing parenthesis
''',
)

print(f"Worker créé: {invalid_syntax_worker.name}")
print(f"Code:\n{invalid_syntax_worker.code}")

# Vérifie le worker
verification = invalid_syntax_worker.verify()
print(f"\nRésultat de la vérification:")
print(f"  Valid: {verification['valid']}")
print(f"  Name: {verification['name']}")
print(f"  Issues: {verification['issues']}")

# ============================================================================
# Worker avec dépendances
# ============================================================================

print("\n3. Vérification d'un worker avec dépendances")
print("-" * 70)

deps_worker = procyl.create(
    "deps_worker",
    '''
import requests
import numpy as np
print("Worker with dependencies")
''',
)

print(f"Worker créé: {deps_worker.name}")
print(f"Dépendances détectées: {deps_worker.data.dependencies}")

# Vérifie le worker
verification = deps_worker.verify()
print(f"\nRésultat de la vérification:")
print(f"  Valid: {verification['valid']}")
print(f"  Name: {verification['name']}")
print(f"  Issues: {verification['issues']}")
if 'dependencies' in verification:
    print(f"  Dependencies: {verification['dependencies']}")

# ============================================================================
# Worker compilé
# ============================================================================

print("\n4. Vérification d'un worker compilé")
print("-" * 70)

compiled_worker = procyl.create(
    "compiled_worker",
    '''
print("Compiled worker")
''',
    compiler="python",  # Utilise python comme compilateur (copie le source)
)

print(f"Worker créé: {compiled_worker.name}")
print(f"Compiler: {compiled_worker.data.compiler}")
print(f"Compiled: {compiled_worker.data.compiled}")

# Vérifie avant compilation
verification_before = compiled_worker.verify()
print(f"\nVérification avant compilation:")
print(f"  Valid: {verification_before['valid']}")
print(f"  Compiled: {verification_before.get('compiled', 'N/A')}")

# Compile le worker
print("\nCompilation du worker...")
# Note: En production, utilisez procyl.precompile()
# Pour cet exemple, on simule juste la vérification

# ============================================================================
# Vérification de métadonnées
# ============================================================================

print("\n5. Inspection des métadonnées du worker")
print("-" * 70)

print(f"Worker: {valid_worker.name}")
print(f"  Hash: {valid_worker.data.hash}")
print(f"  Compiler: {valid_worker.data.compiler}")
print(f"  Compiled: {valid_worker.data.compiled}")
print(f"  Python version: {valid_worker.data.python_version}")
print(f"  Platform: {valid_worker.data.platform}")
print(f"  Dependencies: {valid_worker.data.dependencies}")
print(f"  Created at: {valid_worker.data.created_at}")
print(f"  Last build: {valid_worker.data.last_build}")
print(f"  Artifact path: {valid_worker.data.path}")
print(f"  Artifact size: {valid_worker.data.size}")
print(f"  Running: {valid_worker.data.running}")

# ============================================================================
# Vérification de plusieurs workers
# ============================================================================

print("\n6. Vérification batch de plusieurs workers")
print("-" * 70)

# Crée plusieurs workers
workers_to_check = []
for i in range(3):
    worker = procyl.create(
        f"batch_worker_{i}",
        f'''
print("Batch worker {i}")
result = {i} * 2
print(f"Result: {{result}}")
''',
    )
    workers_to_check.append(worker)

print(f"Créé {len(workers_to_check)} workers")

# Vérifie tous les workers
print("\nRésultats de vérification:")
all_valid = True
for worker in workers_to_check:
    verification = worker.verify()
    status = "✓" if verification['valid'] else "✗"
    print(f"  {status} {worker.name}: valid={verification['valid']}, issues={len(verification['issues'])}")
    if not verification['valid']:
        all_valid = False

if all_valid:
    print("\n✓ Tous les workers sont valides!")
else:
    print("\n✗ Certains workers ont des problèmes")

# ============================================================================
# Vérification avant exécution
# ============================================================================

print("\n7. Vérification avant exécution (best practice)")
print("-" * 70)

def safe_execute(worker_name, args=None):
    """
    Exécute un worker en toute sécurité après vérification.
    
    Cette fonction montre une best practice: toujours vérifier
    un worker avant de l'exécuter en production.
    """
    worker = procyl._workers.get(worker_name)
    if not worker:
        print(f"Erreur: Worker '{worker_name}' non trouvé")
        return None
    
    # Vérifie le worker
    verification = worker.verify()
    
    if not verification['valid']:
        print(f"Erreur: Worker '{worker_name}' invalide")
        print(f"  Issues: {verification['issues']}")
        return None
    
    # Si valide, exécute
    print(f"Worker '{worker_name}' valide, exécution...")
    try:
        result = procyl.run(worker_name, args=args)
        return result
    except Exception as e:
        print(f"Erreur lors de l'exécution: {e}")
        return None

# Utilise la fonction d'exécution sécurisée
print("Exécution sécurisée de 'valid_worker':")
result = safe_execute("valid_worker", args=["--safe"])
if result:
    print(f"Résultat: {result.strip()}")

print("\nTentative d'exécution sécurisée de 'invalid_syntax':")
result = safe_execute("invalid_syntax")
if result is None:
    print("Exécution bloquée car le worker est invalide (comme attendu)")

# ============================================================================
# Vérification de l'intégrité de l'artefact
# ============================================================================

print("\n8. Vérification de l'intégrité de l'artefact")
print("-" * 70)

# Crée un worker avec un artefact simulé
artifact_worker = procyl.create(
    "artifact_worker",
    '''
print("Artifact worker")
''',
)

# Simule un artefact
import tempfile
import os
temp_dir = tempfile.mkdtemp()
artifact_path = os.path.join(temp_dir, "artifact_worker.exe")
with open(artifact_path, "w") as f:
    f.write("fake artifact")

artifact_worker.artifact_path = artifact_path

print(f"Worker: {artifact_worker.name}")
print(f"Artifact path: {artifact_worker.artifact_path}")
print(f"Artifact exists: {os.path.exists(artifact_worker.artifact_path)}")

# Vérifie
verification = artifact_worker.verify()
print(f"\nVérification:")
print(f"  Valid: {verification['valid']}")
print(f"  Compiled: {verification.get('compiled', 'N/A')}")
if 'artifact_size' in verification:
    print(f"  Artifact size: {verification['artifact_size']} bytes")

# Nettoie
os.remove(artifact_path)
os.rmdir(temp_dir)

# ============================================================================
# Monitoring de l'état des workers
# ============================================================================

print("\n9. Monitoring de l'état des workers")
print("-" * 70)

all_workers = ["valid_worker", "invalid_syntax", "deps_worker", 
               "compiled_worker", "artifact_worker"]

print("État des workers:")
for worker_name in all_workers:
    status = procyl.status(worker_name)
    if status['exists']:
        print(f"  {worker_name}:")
        print(f"    State: {status['state']}")
        print(f"    Compiled: {bool(status.get('artifact_path'))}")
    else:
        print(f"  {worker_name}: Non trouvé")

# ============================================================================
# Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("Cleanup")
print("=" * 70)

# Supprime tous les workers créés
all_workers.extend([f"batch_worker_{i}" for i in range(3)])

for worker_name in all_workers:
    try:
        result = procyl.delete(worker_name)
        print(f"Supprimé '{worker_name}': {result.get('deleted', False)}")
    except:
        print(f"Worker '{worker_name}' déjà supprimé ou inexistant")

print("\n" + "=" * 70)
print("Exemple terminé!")
print("=" * 70)
print("\nBest practices de vérification:")
print("- Vérifiez toujours les workers avant l'exécution en production")
print("- Utilisez worker.verify() pour détecter les erreurs de syntaxe")
print("- Vérifiez les dépendances avant le déploiement")
print("- Surveillez l'état des workers régulièrement")
print("- Implémentez des vérifications d'intégrité pour les artefacts compilés")
print("- Utilisez des fonctions d'exécution sécurisées comme safe_execute()")
