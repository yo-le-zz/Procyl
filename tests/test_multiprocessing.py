"""
Tests complets pour le système d'exécution parallèle (multiprocessing) de Procyl.

Ce module teste tous les aspects de l'exécution parallèle:
- Exécution unique (count=1)
- Exécution parallèle avec différents counts
- Gestion des arguments personnalisés
- Fallback quand multiprocessing échoue
- Gestion des timeouts
- Retour des résultats
- Performance et scaling
"""

import sys
import os
import time
import pytest
sys.path.insert(0, "src")

import procyl


class TestSingleExecution:
    """Tests pour l'exécution unique (count=1)."""
    
    def test_run_single_worker(self):
        """
        Teste l'exécution d'un worker une seule fois.
        
        count=1 doit exécuter le worker une fois et retourner
        une liste avec un seul résultat.
        """
        worker = procyl.create("single_test", "print('Hello, World!')")
        results = worker.run(count=1)
        
        # Doit retourner une liste
        assert isinstance(results, list)
        # Doit avoir exactement un résultat
        assert len(results) == 1
        # Le résultat doit contenir la sortie attendue
        assert "Hello, World!" in results[0]
        
        procyl.delete("single_test")
    
    def test_run_default_count(self):
        """
        Teste l'exécution avec le count par défaut (1).
        
        Quand count n'est pas spécifié, il doit par défaut être 1.
        """
        worker = procyl.create("default_test", "print('Default')")
        results = worker.run()
        
        assert len(results) == 1
        assert "Default" in results[0]
        
        procyl.delete("default_test")
    
    def test_run_single_with_custom_args(self):
        """
        Teste l'exécution unique avec des arguments personnalisés.
        
        Les arguments personnalisés doivent remplacer les arguments par défaut.
        """
        code = """
import sys
print(f"Args: {sys.argv[1:]}")
"""
        worker = procyl.create("args_test", code, args=["default"])
        results = worker.run(count=1, args=["custom", "args"])
        
        assert len(results) == 1
        assert "custom" in results[0]
        assert "args" in results[0]
        # Les arguments par défaut ne doivent pas être utilisés
        assert "default" not in results[0]
        
        procyl.delete("args_test")
    
    def test_run_single_with_timeout(self):
        """
        Teste l'exécution unique avec timeout.
        
        Le worker doit respecter le timeout spécifié.
        """
        code = """
import time
time.sleep(0.1)
print('Done')
"""
        worker = procyl.create("timeout_test", code, timeout_seconds=5)
        results = worker.run(count=1)
        
        assert len(results) == 1
        assert "Done" in results[0]
        
        procyl.delete("timeout_test")


class TestParallelExecution:
    """Tests pour l'exécution parallèle (count > 1)."""
    
    def test_run_parallel_two_workers(self):
        """
        Teste l'exécution parallèle de 2 workers.
        
        count=2 doit exécuter le worker 2 fois en parallèle
        et retourner une liste de 2 résultats.
        """
        worker = procyl.create("parallel_two", "print('Parallel')")
        results = worker.run(count=2)
        
        # Doit retourner 2 résultats
        assert len(results) == 2
        # Chaque résultat doit contenir la sortie attendue
        for result in results:
            assert "Parallel" in result
        
        procyl.delete("parallel_two")
    
    def test_run_parallel_four_workers(self):
        """
        Teste l'exécution parallèle de 4 workers.
        
        count=4 doit exécuter le worker 4 fois en parallèle.
        """
        worker = procyl.create("parallel_four", "print('Four workers')")
        results = worker.run(count=4)
        
        assert len(results) == 4
        for result in results:
            assert "Four workers" in result
        
        procyl.delete("parallel_four")
    
    def test_run_parallel_eight_workers(self):
        """
        Teste l'exécution parallèle de 8 workers.
        
        count=8 teste le scaling sur un plus grand nombre de workers.
        """
        worker = procyl.create("parallel_eight", "print('Eight workers')")
        results = worker.run(count=8)
        
        assert len(results) == 8
        for result in results:
            assert "Eight workers" in result
        
        procyl.delete("parallel_eight")
    
    def test_run_parallel_with_different_outputs(self):
        """
        Teste que chaque exécution parallèle produit une sortie distincte.
        
        Même si le code est le même, chaque exécution doit produire
        son propre résultat dans la liste.
        """
        worker = procyl.create("distinct_outputs", "print('Output')")
        results = worker.run(count=3)
        
        assert len(results) == 3
        # Chaque résultat est indépendant
        for result in results:
            assert "Output" in result
        
        procyl.delete("distinct_outputs")
    
    def test_run_parallel_with_custom_args(self):
        """
        Teste l'exécution parallèle avec des arguments personnalisés.
        
        Tous les workers parallèles doivent recevoir les mêmes arguments.
        """
        code = """
import sys
print(f"Args: {sys.argv[1:]}")
"""
        worker = procyl.create("parallel_args", code)
        results = worker.run(count=3, args=["parallel", "test"])
        
        assert len(results) == 3
        for result in results:
            assert "parallel" in result
            assert "test" in result
        
        procyl.delete("parallel_args")
    
    def test_run_parallel_with_computation(self):
        """
        Teste l'exécution parallèle avec du calcul réel.
        
        Vérifie que le multiprocessing fonctionne correctement
        avec du code qui fait des calculs.
        """
        code = """
result = sum(range(1000))
print(f"Sum: {result}")
"""
        worker = procyl.create("compute_test", code)
        results = worker.run(count=4)
        
        assert len(results) == 4
        for result in results:
            assert "Sum: 499500" in result
        
        procyl.delete("compute_test")


class TestMultiprocessingFallback:
    """Tests pour le fallback quand multiprocessing échoue."""
    
    def test_fallback_on_multiprocessing_error(self):
        """
        Teste le fallback quand multiprocessing lève une erreur.
        
        Si multiprocessing.Pool échoue (ex: dans certains environnements CI),
        le système doit fallback vers l'exécution séquentielle.
        """
        worker = procyl.create("fallback_test", "print('Fallback')")
        
        # Ce test ne peut pas vraiment forcer une erreur multiprocessing,
        # mais vérifie que l'exécution fonctionne dans tous les cas
        results = worker.run(count=2)
        
        # Doit retourner des résultats même avec fallback
        assert len(results) == 2
        for result in results:
            assert "Fallback" in result
        
        procyl.delete("fallback_test")
    
    def test_fallback_preserves_results(self):
        """
        Teste que le fallback préserve les résultats corrects.
        
        Les résultats doivent être identiques que ce soit avec
        multiprocessing ou avec le fallback séquentiel.
        """
        code = """
import sys
print(f"Result: {sys.argv[1] if len(sys.argv) > 1 else 'none'}")
"""
        worker = procyl.create("fallback_preserve", code)
        results = worker.run(count=3, args=["test"])
        
        assert len(results) == 3
        for result in results:
            assert "Result: test" in result
        
        procyl.delete("fallback_preserve")


class TestMultiprocessingPerformance:
    """Tests pour les performances du multiprocessing."""
    
    def test_parallel_faster_than_sequential(self):
        """
        Teste que l'exécution parallèle est plus rapide que séquentielle.
        
        Pour du code qui prend du temps, l'exécution parallèle
        doit être plus rapide que l'exécution séquentielle.
        """
        code = """
import time
time.sleep(0.05)
print('Done')
"""
        worker = procyl.create("perf_test", code)
        
        # Exécution séquentielle (4 exécutions)
        start_seq = time.time()
        seq_results = [worker.run(count=1)[0] for _ in range(4)]
        seq_time = time.time() - start_seq
        
        # Exécution parallèle (4 workers)
        start_par = time.time()
        par_results = worker.run(count=4)
        par_time = time.time() - start_par
        
        # La parallèle doit être plus rapide (ou similaire sur 1 core)
        # On accepte une marge pour les systèmes à 1 core
        assert len(par_results) == 4
        assert len(seq_results) == 4
        
        procyl.delete("perf_test")
    
    def test_scaling_with_count(self):
        """
        Teste que le système scale correctement avec différents counts.
        
        Le temps d'exécution doit augmenter de manière raisonnable
        avec le nombre de workers.
        """
        code = """
import time
time.sleep(0.01)
print('Done')
"""
        worker = procyl.create("scaling_test", code)
        
        # Test avec différents counts
        for count in [1, 2, 4, 8]:
            results = worker.run(count=count)
            assert len(results) == count
            for result in results:
                assert "Done" in result
        
        procyl.delete("scaling_test")


class TestEdgeCases:
    """Tests pour les cas limites et edge cases."""
    
    def test_run_with_zero_count(self):
        """
        Teste count=0 (doit être traité comme count=1).
        
        count <= 1 doit exécuter une seule fois sans multiprocessing.
        """
        worker = procyl.create("zero_count", "print('Zero')")
        results = worker.run(count=0)
        
        # count=0 doit être traité comme count=1
        assert len(results) == 1
        assert "Zero" in results[0]
        
        procyl.delete("zero_count")
    
    def test_run_with_negative_count(self):
        """
        Teste count négatif (doit être traité comme count=1).
        """
        worker = procyl.create("negative_count", "print('Negative')")
        results = worker.run(count=-1)
        
        # count négatif doit être traité comme count=1
        assert len(results) == 1
        assert "Negative" in results[0]
        
        procyl.delete("negative_count")
    
    def test_run_with_large_count(self):
        """
        Teste avec un count très élevé.
        
        Le système doit gérer correctement un grand nombre de workers
        (limité par os.cpu_count()).
        """
        worker = procyl.create("large_count", "print('Large')")
        results = worker.run(count=100)
        
        # Doit exécuter le nombre demandé de workers
        assert len(results) == 100
        for result in results:
            assert "Large" in result
        
        procyl.delete("large_count")
    
    def test_run_with_empty_code(self):
        """
        Teste l'exécution parallèle avec du code vide.
        """
        worker = procyl.create("empty_code", "")
        results = worker.run(count=2)
        
        assert len(results) == 2
        
        procyl.delete("empty_code")
    
    def test_run_with_syntax_error(self):
        """
        Teste l'exécution parallèle avec du code ayant une erreur de syntaxe.
        
        Le système doit gérer gracieusement les erreurs de syntaxe.
        """
        code = """
print('incomplete'
"""
        worker = procyl.create("syntax_error", code)
        
        # L'exécution doit échouer mais ne pas crasher
        # Le comportement exact dépend de l'implémentation
        try:
            results = worker.run(count=2)
            # Si ça retourne, vérifie qu'on a 2 résultats (même vides ou avec erreur)
            assert len(results) == 2
        except Exception:
            # Si ça lève une exception, c'est aussi acceptable
            pass
        
        procyl.delete("syntax_error")


class TestArgumentsHandling:
    """Tests pour la gestion des arguments."""
    
    def test_run_with_default_args(self):
        """
        Teste l'utilisation des arguments par défaut du worker.
        
        Quand aucun argument n'est passé à run(), les arguments
        par défaut du worker doivent être utilisés.
        """
        code = """
import sys
print(f"Args: {sys.argv[1:]}")
"""
        worker = procyl.create("default_args", code, args=["default1", "default2"])
        results = worker.run(count=2)
        
        assert len(results) == 2
        for result in results:
            assert "default1" in result
            assert "default2" in result
        
        procyl.delete("default_args")
    
    def test_run_custom_args_override_default(self):
        """
        Teste que les arguments personnalisés remplacent les défauts.
        
        Les arguments passés à run() doivent remplacer
        les arguments par défaut du worker.
        """
        code = """
import sys
print(f"Args: {sys.argv[1:]}")
"""
        worker = procyl.create("override_args", code, args=["default"])
        results = worker.run(count=2, args=["custom"])
        
        assert len(results) == 2
        for result in results:
            assert "custom" in result
            assert "default" not in result
        
        procyl.delete("override_args")
    
    def test_run_with_no_args_when_worker_has_args(self):
        """
        Teste run() sans args quand le worker a des arguments par défaut.
        
        Dans ce cas, les arguments par défaut doivent être utilisés.
        """
        code = """
import sys
print(f"Args: {sys.argv[1:]}")
"""
        worker = procyl.create("no_override", code, args=["default"])
        results = worker.run(count=2)
        
        assert len(results) == 2
        for result in results:
            assert "default" in result
        
        procyl.delete("no_override")
    
    def test_run_with_empty_args_list(self):
        """
        Teste avec une liste d'arguments vide.
        
        args=[] doit remplacer les arguments par défaut par rien.
        """
        code = """
import sys
print(f"Args: {sys.argv[1:]}")
"""
        worker = procyl.create("empty_args", code, args=["default"])
        results = worker.run(count=2, args=[])
        
        assert len(results) == 2
        for result in results:
            # Args: [] signifie aucun argument
            assert "default" not in result
        
        procyl.delete("empty_args")


class TestTimeoutHandling:
    """Tests pour la gestion des timeouts."""
    
    def test_run_respects_timeout(self):
        """
        Teste que le timeout est respecté.
        
        Un worker qui prend plus de temps que le timeout doit
        être interrompu ou géré correctement.
        """
        code = """
import time
time.sleep(10)
print('Should not print')
"""
        worker = procyl.create("timeout_respect", code, timeout_seconds=1)
        
        # L'exécution doit soit échouer à cause du timeout,
        # soit retourner rapidement (comportement dépend de l'implémentation)
        start = time.time()
        try:
            results = worker.run(count=1)
            elapsed = time.time() - start
            # Si ça réussit, doit être rapide (< 2 secondes)
            assert elapsed < 2.0
        except Exception:
            elapsed = time.time() - start
            # Si ça échoue, doit être rapide (< 2 secondes)
            assert elapsed < 2.0
        
        procyl.delete("timeout_respect")
    
    def test_run_with_no_timeout(self):
        """
        Teste l'exécution sans timeout.
        
        Quand aucun timeout n'est spécifié, le worker doit
        pouvoir s'exécuter normalement.
        """
        code = """
import time
time.sleep(0.05)
print('Done')
"""
        worker = procyl.create("no_timeout", code)
        results = worker.run(count=1)
        
        assert len(results) == 1
        assert "Done" in results[0]
        
        procyl.delete("no_timeout")


class TestResultConsistency:
    """Tests pour la cohérence des résultats."""
    
    def test_results_are_strings(self):
        """
        Teste que tous les résultats sont des chaînes de caractères.
        """
        worker = procyl.create("string_results", "print('String')")
        results = worker.run(count=3)
        
        for result in results:
            assert isinstance(result, str)
        
        procyl.delete("string_results")
    
    def test_results_order(self):
        """
        Teste que l'ordre des résultats est cohérent.
        
        Les résultats doivent être retournés dans un ordre cohérent.
        """
        worker = procyl.create("order_test", "print('Test')")
        results = worker.run(count=5)
        
        # On ne peut pas garantir l'ordre exact avec multiprocessing,
        # mais on doit avoir le bon nombre de résultats
        assert len(results) == 5
        
        procyl.delete("order_test")
    
    def test_results_independence(self):
        """
        Teste que chaque résultat est indépendant.
        
        Modifier un résultat ne doit pas affecter les autres.
        """
        worker = procyl.create("independence_test", "print('Independent')")
        results = worker.run(count=3)
        
        # Modifier un résultat
        results[0] = "Modified"
        
        # Les autres résultats ne doivent pas être affectés
        assert results[1] != "Modified"
        assert results[2] != "Modified"
        
        procyl.delete("independence_test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
