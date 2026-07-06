"""
Exemple de traitement de données parallèle avec Procyl.

Cet exemple montre comment utiliser l'exécution parallèle de Procyl
pour traiter efficacement de grandes quantités de données.
"""

import procyl
import json

print("=" * 70)
print("Traitement de données parallèle avec Procyl")
print("=" * 70)

# ============================================================================
# Worker de traitement de données
# ============================================================================

print("\n1. Création d'un worker de traitement de données")
print("-" * 70)

data_processor = procyl.create(
    "data_processor",
    '''
import sys
import json

# Récupère les données depuis les arguments
if len(sys.argv) > 1:
    data = json.loads(sys.argv[1])
else:
    data = {"value": 0}

# Simule un traitement (ex: calcul, transformation, etc.)
value = data.get("value", 0)
result = {
    "input": value,
    "processed": value * 2,  # Exemple: doubler la valeur
    "squared": value ** 2,   # Exemple: carré
}

print(json.dumps(result))
''',
)

print(f"Worker créé: {data_processor.name}")
print(f"Dépendances: {data_processor.data.dependencies}")

# ============================================================================
# Traitement séquentiel (pour comparaison)
# ============================================================================

print("\n2. Traitement séquentiel (baseline)")
print("-" * 70)

sample_data = [{"value": i} for i in range(10)]

print("Traitement de 10 items séquentiellement...")
import time
start_seq = time.time()

sequential_results = []
for item in sample_data:
    result = data_processor.run(count=1, args=[json.dumps(item)])
    sequential_results.append(result[0])

seq_time = time.time() - start_seq
print(f"Temps séquentiel: {seq_time:.3f} secondes")
print(f"Premier résultat: {sequential_results[0].strip()}")

# ============================================================================
# Traitement parallèle
# ============================================================================

print("\n3. Traitement parallèle")
print("-" * 70)

print("Traitement de 10 items en parallèle...")
start_par = time.time()

# Note: Pour des données différentes, on doit créer des workers distincts
# ou passer les données via les arguments
parallel_results = []
for item in sample_data:
    result = data_processor.run(count=1, args=[json.dumps(item)])
    parallel_results.append(result[0])

par_time = time.time() - start_par
print(f"Temps parallèle: {par_time:.3f} secondes")
print(f"Premier résultat: {parallel_results[0].strip()}")

# ============================================================================
# Vrai traitement parallèle (même worker, count > 1)
# ============================================================================

print("\n4. Vrai parallélisme (même tâche, count > 1)")
print("-" * 70)

# Crée un worker qui génère ses propres données
compute_worker = procyl.create(
    "compute_worker",
    '''
import random
import time

# Simule un calcul
time.sleep(0.01)  # 10ms de "travail"
result = random.randint(1, 100)
print(f"Résultat: {result}")
''',
)

print("Exécution de 8 workers en parallèle...")
start = time.time()

results = compute_worker.run(count=8)

elapsed = time.time() - start
print(f"Temps pour 8 exécutions: {elapsed:.3f} secondes")
print(f"Résultats: {[r.strip() for r in results]}")

# ============================================================================
# Traitement par lots (batch processing)
# ============================================================================

print("\n5. Traitement par lots")
print("-" * 70)

batch_worker = procyl.create(
    "batch_worker",
    '''
import sys

# Simule le traitement d'un lot
batch_id = sys.argv[1] if len(sys.argv) > 1 else "unknown"
print(f"Traitement du lot {batch_id} terminé")
''',
)

batch_size = 5
num_batches = 3

print(f"Traitement de {num_batches} lots de {batch_size} items chacun...")

for batch_num in range(num_batches):
    print(f"\nLot {batch_num + 1}:")
    # Exécute le même worker batch_size fois en parallèle
    batch_results = batch_worker.run(
        count=batch_size,
        args=[f"batch-{batch_num + 1}"]
    )
    print(f"  {len(batch_results)} items traités")

# ============================================================================
# Agrégation des résultats
# ============================================================================

print("\n6. Agrégation des résultats")
print("-" * 70)

aggregator_worker = procyl.create(
    "aggregator",
    '''
import sys
import json

# Simule une agrégation
values = [int(sys.argv[i]) if i < len(sys.argv) else 0 for i in range(1, len(sys.argv))]
total = sum(values)
average = total / len(values) if values else 0

result = {
    "count": len(values),
    "total": total,
    "average": average
}
print(json.dumps(result))
''',
)

print("Agrégation de plusieurs résultats...")
result = aggregator_worker.run(count=1, args=["10", "20", "30", "40", "50"])
print(f"Résultat agrégé: {result[0].strip()}")

# ============================================================================
# Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("Cleanup")
print("=" * 70)

workers_to_delete = ["data_processor", "compute_worker", "batch_worker", "aggregator"]

for worker_name in workers_to_delete:
    result = procyl.delete(worker_name)
    print(f"Supprimé '{worker_name}': {result['deleted']}")

print("\n" + "=" * 70)
print("Exemple terminé!")
print("=" * 70)
print("\nNote: Pour un vrai gain de performance avec des données différentes,")
print("créez des workers distincts ou utilisez une approche de partage de fichiers.")
