"""
Exemple de gestion des contraintes de version avec Procyl.

Cet exemple montre comment utiliser les contraintes de version pour
contrôler précisément les versions des packages installés.
"""

import procyl

print("=" * 70)
print("Gestion des contraintes de version avec Procyl")
print("=" * 70)

# ============================================================================
# Worker avec dépendances
# ============================================================================

print("\n1. Création de workers avec dépendances")
print("-" * 70)

worker1 = procyl.create(
    "worker_requests",
    '''
import requests
print(f"requests version: {requests.__version__}")
''',
)

worker2 = procyl.create(
    "worker_numpy",
    '''
import numpy as np
print(f"numpy version: {np.__version__}")
''',
)

worker3 = procyl.create(
    "worker_pandas",
    '''
import pandas as pd
print(f"pandas version: {pd.__version__}")
''',
)

print(f"Workers créés: {worker1.name}, {worker2.name}, {worker3.name}")
print(f"Dépendances détectées:")
print(f"  {worker1.name}: {worker1.data.dependencies}")
print(f"  {worker2.name}: {worker2.data.dependencies}")
print(f"  {worker3.name}: {worker3.data.dependencies}")

# ============================================================================
# Préparation avec contraintes de version
# ============================================================================

print("\n2. Préparation avec contraintes de version spécifiques")
print("-" * 70)

print("Configuration des contraintes:")
constraints = {
    "requests": ">=2.28.0",      # requests version 2.28.0 ou supérieure
    "numpy": ">=1.20,<2.0",      # numpy version 1.20+ mais < 2.0
    "pandas": "~=1.5.0",         # pandas version compatible avec 1.5.0
}

for package, constraint in constraints.items():
    print(f"  {package}: {constraint}")

print("\nPréparation de l'environnement...")
success = procyl.prepare(constraints=constraints)

if success:
    print("✓ Environnement préparé avec succès!")
else:
    print("✗ Échec de la préparation de l'environnement")

# ============================================================================
# Exécution des workers
# ============================================================================

print("\n3. Exécution des workers")
print("-" * 70)

print(f"\nExécution de {worker1.name}:")
output1 = procyl.run("worker_requests")
print(f"  {output1.strip()}")

print(f"\nExécution de {worker2.name}:")
output2 = procyl.run("worker_numpy")
print(f"  {output2.strip()}")

print(f"\nExécution de {worker3.name}:")
output3 = procyl.run("worker_pandas")
print(f"  {output3.strip()}")

# ============================================================================
# Différents opérateurs de version
# ============================================================================

print("\n4. Exemples d'opérateurs de version")
print("-" * 70)

version_examples = {
    "Exacte": "==1.0.0",
    "Supérieur ou égal": ">=1.0.0",
    "Inférieur ou égal": "<=2.0.0",
    "Strictement supérieur": ">1.0.0",
    "Strictement inférieur": "<2.0.0",
    "Différent": "!=1.0.0",
    "Compatible": "~=1.2.0",
    "Plage": ">=1.0.0,<2.0.0",
}

print("Opérateurs supportés:")
for description, constraint in version_examples.items():
    print(f"  {description:25} : {constraint}")

# ============================================================================
# Préparation avec fichier requirements.txt
# ============================================================================

print("\n5. Préparation avec fichier requirements.txt")
print("-" * 70)

# Crée un fichier requirements.txt temporaire
requirements_content = """
# Requirements.txt pour Procyl
requests>=2.28.0
numpy>=1.20,<2.0
pandas~=1.5.0
"""

with open("requirements_example.txt", "w") as f:
    f.write(requirements_content)

print("Fichier requirements_example.txt créé:")
print(requirements_content)

print("\nPréparation depuis le fichier...")
# Note: En production, utilisez un vrai fichier requirements.txt
# success = procyl.prepare(requirements="requirements_example.txt")
print("(Commenté pour éviter d'installer réellement les packages)")

# ============================================================================
# Validation des contraintes
# ============================================================================

print("\n6. Validation des contraintes")
print("-" * 70)

from procyl.dependencies import parse_constraints, validate_requirement

print("Parsing des contraintes:")
test_constraints = {
    "numpy": ">=1.20,<2.0",
    "requests": "==2.28.0",
    "pandas": "~=1.5.0"
}

parsed = parse_constraints(test_constraints)
print(f"Contraintes parsées: {parsed}")

print("\nValidation de requirements individuels:")
test_requirements = [
    "numpy>=1.20",
    "requests==2.28.0",
    "pandas~=1.5.0",
    "invalid-package",  # Sans version
]

for req in test_requirements:
    try:
        package, version = validate_requirement(req)
        print(f"  {req:20} → Package: {package}, Version: {version}")
    except ValueError as e:
        print(f"  {req:20} → Erreur: {e}")

# ============================================================================
# Gestion des erreurs de contraintes
# ============================================================================

print("\n7. Gestion des erreurs de contraintes")
print("-" * 70)

print("Cas d'erreur:")

try:
    # Nom de package vide
    parse_constraints({"": ">=1.0"})
except ValueError as e:
    print(f"  Nom vide: {e}")

try:
    # Version None
    parse_constraints({"numpy": None})
except ValueError as e:
    print(f"  Version None: {e}")

try:
    # Version vide
    parse_constraints({"numpy": ""})
except ValueError as e:
    print(f"  Version vide: {e}")

# ============================================================================
# Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("Cleanup")
print("=" * 70)

workers_to_delete = ["worker_requests", "worker_numpy", "worker_pandas"]

for worker_name in workers_to_delete:
    result = procyl.delete(worker_name)
    print(f"Supprimé '{worker_name}': {result['deleted']}")

# Nettoie le fichier temporaire
import os
if os.path.exists("requirements_example.txt"):
    os.remove("requirements_example.txt")
    print("Fichier requirements_example.txt supprimé")

print("\n" + "=" * 70)
print("Exemple terminé!")
print("=" * 70)
print("\nConseils:")
print("- Utilisez des contraintes spécifiques pour la reproductibilité")
print("- Préférez ~= pour les mises à jour compatibles")
print("- Utilisez >=1.0,<2.0 pour des plages de version")
print("- Testez toujours vos contraintes avant le déploiement")
