# Exemples Procyl

Ce dossier contient des exemples complets montrant comment utiliser les différentes fonctionnalités de Procyl v1.0.0.

## Liste des exemples

### Exemples de base

1. **demo.py** - Démo complète de toutes les fonctionnalités
   - Création de workers
   - Inspection des métadonnées
   - Vérification des workers
   - Préparation de l'environnement
   - Exécution simple et parallèle
   - Gestion du statut
   - Cleanup

2. **parallel_workers.py** - Création parallèle de workers
   - Utilisation de threads pour compiler plusieurs workers
   - Compilation en arrière-plan
   - Monitoring de la progression

3. **runtime_worker.py** - Compilation et exécution runtime
   - Compilation à la volée
   - Exécution immédiate après compilation
   - Gestion des timeouts

4. **threaded_compile.py** - Compilation threadée
   - Compilation en arrière-plan
   - Suivi de la progression
   - Gestion des états de transition

### Exemples avancés (nouveaux)

5. **dependency_detection.py** - Détection automatique des dépendances
   - Imports simples et complexes
   - Filtrage de la stdlib
   - Imports relatifs
   - Imports avec alias
   - Préparation de l'environnement

6. **parallel_data_processing.py** - Traitement de données parallèle
   - Traitement séquentiel vs parallèle
   - Vrai parallélisme avec count > 1
   - Traitement par lots
   - Agrégation de résultats

7. **version_constraints.py** - Gestion des contraintes de version
   - Contraintes spécifiques par package
   - Différents opérateurs de version
   - Fichiers requirements.txt
   - Validation des contraintes
   - Gestion des erreurs

8. **web_scraping.py** - Web scraping avec Procyl
   - Requêtes HTTP simples
   - Scraping parallèle d'URLs
   - Extraction de données JSON
   - Headers personnalisés
   - Mécanismes de retry
   - Rate limiting

9. **worker_verification.py** - Vérification de workers
   - Workers valides et invalides
   - Détection d'erreurs de syntaxe
   - Vérification des dépendances
   - Inspection des métadonnées
   - Vérification batch
   - Exécution sécurisée
   - Intégrité des artefacts

10. **timeout_handling.py** - Gestion des timeouts
    - Workers avec et sans timeout
    - Timeouts raisonnables et courts
    - Exécution parallèle avec timeout
    - Timeouts conditionnels
    - Retry avec timeout
    - Monitoring des timeouts
    - Best practices

## Comment exécuter les exemples

```bash
# Exemple de base
python examples/demo.py

# Exemples avancés
python examples/dependency_detection.py
python examples/parallel_data_processing.py
python examples/version_constraints.py
python examples/web_scraping.py
python examples/worker_verification.py
python examples/timeout_handling.py
```

## Prérequis

- Python 3.10+
- Procyl installé (`pip install procyl`)
- Pour certains exemples: `pip install procyl[compile]`

## Notes importantes

- Certains exemples nécessitent des packages externes (requests, numpy, etc.)
- Les exemples de web scraping nécessitent une connexion internet
- Les exemples de compilation nécessitent PyInstaller ou Nuitka
- Tous les exemples incluent un cleanup automatique des workers créés

## Structure des exemples

Chaque exemple suit cette structure:
1. Introduction avec description
2. Création de workers
3. Démonstration de fonctionnalités
4. Monitoring et vérification
5. Cleanup
6. Best practices et conseils

## Personnalisation

Vous pouvez facilement adapter ces exemples à vos besoins:
- Modifiez le code des workers
- Changez les paramètres (timeout, compiler, etc.)
- Ajustez le nombre de workers parallèles
- Adaptez les contraintes de version
- Modifiez les URLs pour le web scraping

## Support

Pour plus d'informations, consultez:
- [Documentation principale](../README.md)
- [Documentation API](../doc/API.md)
- [Guide de développement](../doc/DEVELOPMENT.md)
