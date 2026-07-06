"""
Exemple de web scraping avec Procyl.

Cet exemple montre comment utiliser Procyl pour effectuer des requêtes
HTTP et du web scraping en parallèle, avec gestion des dépendances.
"""

import procyl
import json

print("=" * 70)
print("Web Scraping avec Procyl")
print("=" * 70)

# ============================================================================
# Worker de scraping simple
# ============================================================================

print("\n1. Création d'un worker de scraping simple")
print("-" * 70)

simple_scraper = procyl.create(
    "simple_scraper",
    '''
import sys
import requests

url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/get"

try:
    response = requests.get(url, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Length: {len(response.content)} bytes")
    print(f"URL: {url}")
except Exception as e:
    print(f"Error: {e}")
''',
)

print(f"Worker créé: {simple_scraper.name}")
print(f"Dépendances: {simple_scraper.data.dependencies}")

# ============================================================================
# Préparation de l'environnement
# ============================================================================

print("\n2. Préparation de l'environnement")
print("-" * 70)

print("Installation des dépendances...")
success = procyl.prepare(constraints={"requests": ">=2.28.0"})

if success:
    print("✓ Environnement préparé avec succès!")
else:
    print("✗ Échec de la préparation (peut-être déjà installé)")

# ============================================================================
# Scraping simple
# ============================================================================

print("\n3. Scraping simple d'une URL")
print("-" * 70)

url = "https://httpbin.org/get"
print(f"Scraping de: {url}")

result = simple_scraper.run(count=1, args=[url])
print(f"Résultat:\n{result[0]}")

# ============================================================================
# Scraping parallèle de plusieurs URLs
# ============================================================================

print("\n4. Scraping parallèle de plusieurs URLs")
print("-" * 70)

urls_to_scrape = [
    "https://httpbin.org/get",
    "https://httpbin.org/uuid",
    "https://httpbin.org/ip",
    "https://httpbin.org/user-agent",
]

print(f"Scraping de {len(urls_to_scrape)} URLs en parallèle...")

# Note: Pour scraper des URLs différentes, on doit exécuter le worker
# plusieurs fois avec des arguments différents
parallel_results = []
for url in urls_to_scrape:
    result = simple_scraper.run(count=1, args=[url])
    parallel_results.append(result[0])

print(f"\nRésultats:")
for i, result in enumerate(parallel_results, 1):
    print(f"\nURL {i}:")
    print(f"  {result.strip()}")

# ============================================================================
# Worker de scraping avec extraction de données
# ============================================================================

print("\n5. Worker avec extraction de données JSON")
print("-" * 70)

json_scraper = procyl.create(
    "json_scraper",
    '''
import sys
import requests
import json

url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/json"

try:
    response = requests.get(url, timeout=5)
    data = response.json()
    
    # Extrait des informations spécifiques
    if "slideshow" in data:
        title = data["slideshow"].get("title", "N/A")
        print(f"Title: {title}")
    else:
        print(f"Keys: {list(data.keys())[:5]}")
        
except Exception as e:
    print(f"Error: {e}")
''',
)

print(f"Worker créé: {json_scraper.name}")
print(f"Dépendances: {json_scraper.data.dependencies}")

json_url = "https://httpbin.org/json"
print(f"\nScraping JSON de: {json_url}")

result = json_scraper.run(count=1, args=[json_url])
print(f"Résultat:\n{result[0]}")

# ============================================================================
# Worker de scraping avec headers personnalisés
# ============================================================================

print("\n6. Worker avec headers personnalisés")
print("-" * 70)

header_scraper = procyl.create(
    "header_scraper",
    '''
import sys
import requests
import json

url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/headers"

headers = {
    "User-Agent": "Procyl-Scraper/1.0",
    "Accept": "application/json",
}

try:
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    print(f"User-Agent sent: {headers['User-Agent']}")
    print(f"User-Agent received: {data.get('headers', {}).get('User-Agent', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
''',
)

print(f"Worker créé: {header_scraper.name}")

result = header_scraper.run(count=1, args=["https://httpbin.org/headers"])
print(f"Résultat:\n{result[0]}")

# ============================================================================
# Worker de scraping avec retry
# ============================================================================

print("\n7. Worker avec mécanisme de retry")
print("-" * 70)

retry_scraper = procyl.create(
    "retry_scraper",
    '''
import sys
import requests
import time

url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/get"
max_retries = 3

for attempt in range(max_retries):
    try:
        response = requests.get(url, timeout=5)
        print(f"Success on attempt {attempt + 1}")
        print(f"Status: {response.status_code}")
        break
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_retries - 1:
            time.sleep(1)
else:
    print("All attempts failed")
''',
)

print(f"Worker créé: {retry_scraper.name}")

result = retry_scraper.run(count=1, args=["https://httpbin.org/get"])
print(f"Résultat:\n{result[0]}")

# ============================================================================
# Worker de scraping avec rate limiting
# ============================================================================

print("\n8. Worker avec rate limiting")
print("-" * 70)

rate_limited_scraper = procyl.create(
    "rate_limited_scraper",
    '''
import sys
import requests
import time

url = sys.argv[1] if len(sys.argv) > 1 else "https://httpbin.org/delay/1"
delay = 1  # Secondes entre les requêtes

print(f"Scraping with {delay}s delay between requests")

try:
    start = time.time()
    response = requests.get(url, timeout=10)
    elapsed = time.time() - start
    print(f"Request completed in {elapsed:.2f}s")
    print(f"Status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
''',
)

print(f"Worker créé: {rate_limited_scraper.name}")

# ============================================================================
# Monitoring des workers
# ============================================================================

print("\n9. Monitoring des workers")
print("-" * 70)

workers = ["simple_scraper", "json_scraper", "header_scraper", 
           "retry_scraper", "rate_limited_scraper"]

for worker_name in workers:
    status = procyl.status(worker_name)
    print(f"\n{worker_name}:")
    print(f"  Exists: {status['exists']}")
    print(f"  State: {status['state']}")
    print(f"  Dependencies: {status.get('dependencies', 'N/A')}")

# ============================================================================
# Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("Cleanup")
print("=" * 70)

for worker_name in workers:
    result = procyl.delete(worker_name)
    print(f"Supprimé '{worker_name}': {result['deleted']}")

print("\n" + "=" * 70)
print("Exemple terminé!")
print("=" * 70)
print("\nConseils de web scraping avec Procyl:")
print("- Utilisez toujours des timeouts pour éviter les blocages")
print("- Respectez les robots.txt et les rate limits des sites")
print("- Utilisez des headers User-Agent appropriés")
print("- Implémentez des mécanismes de retry pour la robustesse")
print("- Considérez l'utilisation de proxies pour le scraping à grande échelle")
print("- Vérifiez les conditions d'utilisation des sites cibles")
