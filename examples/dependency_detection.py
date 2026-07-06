"""
Exemple de détection automatique des dépendances.

Cet exemple montre comment Procyl détecte automatiquement les dépendances
externes dans le code Python en utilisant l'analyse AST.
"""

import procyl

print("=" * 70)
print("Détection automatique des dépendances avec Procyl")
print("=" * 70)

# ============================================================================
# Worker avec dépendances mixtes (externes + stdlib)
# ============================================================================

print("\n1. Création d'un worker avec dépendances mixtes")
print("-" * 70)

mixed_deps_worker = procyl.create(
    "mixed_deps",
    '''
import requests              # Dépendance externe
import numpy as np          # Dépendance externe
import os                   # Stdlib (sera filtré)
import sys                  # Stdlib (sera filtré)
import json                 # Stdlib (sera filtré)
from datetime import datetime  # Stdlib (sera filtré)

print("Dépendances détectées automatiquement!")
''',
)

print(f"Worker créé: {mixed_deps_worker.name}")
print(f"Dépendances détectées: {mixed_deps_worker.data.dependencies}")
print("\nNote: os, sys, json, datetime sont filtrés (stdlib)")

# ============================================================================
# Worker avec imports complexes
# ============================================================================

print("\n2. Imports complexes (sous-modules)")
print("-" * 70)

complex_imports_worker = procyl.create(
    "complex_imports",
    '''
import tensorflow.keras        # Détecte 'tensorflow'
import pandas.core.frame      # Détecte 'pandas'
import sklearn.linear_model   # Détecte 'sklearn'
from scipy import stats       # Détecte 'scipy'

print("Imports complexes traités correctement!")
''',
)

print(f"Worker créé: {complex_imports_worker.name}")
print(f"Dépendances détectées: {complex_imports_worker.data.dependencies}")
print("\nNote: Seuls les packages racines sont détectés")

# ============================================================================
# Worker avec imports relatifs (internes)
# ============================================================================

print("\n3. Imports relatifs (internes au projet)")
print("-" * 70)

relative_imports_worker = procyl.create(
    "relative_imports",
    '''
from . import local_module      # Import relatif (ignoré)
from ..core import something    # Import relatif (ignoré)
from ...utils import helper     # Import relatif (ignoré)
import requests                 # Import externe (détecté)

print("Imports relatifs filtrés correctement!")
''',
)

print(f"Worker créé: {relative_imports_worker.name}")
print(f"Dépendances détectées: {relative_imports_worker.data.dependencies}")
print("\nNote: Les imports relatifs sont ignorés (internes)")

# ============================================================================
# Worker avec imports avec alias
# ============================================================================

print("\n4. Imports avec alias")
print("-" * 70)

alias_imports_worker = procyl.create(
    "alias_imports",
    '''
import numpy as np              # Détecte 'numpy', pas 'np'
import pandas as pd             # Détecte 'pandas', pas 'pd'
import tensorflow as tf         # Détecte 'tensorflow', pas 'tf'

print("Imports avec alias gérés correctement!")
''',
)

print(f"Worker créé: {alias_imports_worker.name}")
print(f"Dépendances détectées: {alias_imports_worker.data.dependencies}")
print("\nNote: Les noms originaux sont détectés, pas les alias")

# ============================================================================
# Worker sans dépendances externes
# ============================================================================

print("\n5. Worker sans dépendances externes")
print("-" * 70)

no_deps_worker = procyl.create(
    "no_deps",
    '''
import os
import sys
import json
from datetime import datetime

print("Worker avec seulement des imports stdlib")
''',
)

print(f"Worker créé: {no_deps_worker.name}")
print(f"Dépendances détectées: {no_deps_worker.data.dependencies}")
print("\nNote: Aucune dépendance externe détectée")

# ============================================================================
# Worker avec dépendances versionnées
# ============================================================================

print("\n6. Préparation de l'environnement avec contraintes")
print("-" * 70)

print("Préparation de l'environnement avec contraintes de version...")
success = procyl.prepare(
    constraints={
        "requests": ">=2.28.0",
        "numpy": ">=1.20,<2.0",
    }
)

if success:
    print("✓ Environnement préparé avec succès!")
else:
    print("✗ Échec de la préparation de l'environnement")

# ============================================================================
# Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("Cleanup")
print("=" * 70)

workers_to_delete = ["mixed_deps", "complex_imports", "relative_imports", 
                     "alias_imports", "no_deps"]

for worker_name in workers_to_delete:
    result = procyl.delete(worker_name)
    print(f"Supprimé '{worker_name}': {result['deleted']}")

print("\n" + "=" * 70)
print("Exemple terminé!")
print("=" * 70)
