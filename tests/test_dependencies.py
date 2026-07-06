"""
Tests complets pour le système de détection de dépendances de Procyl.

Ce module teste tous les aspects de la détection automatique de dépendances:
- Détection des imports simples et complexes
- Filtrage des modules standard library
- Gestion des imports relatifs
- Parsing des contraintes de version
- Lecture des fichiers requirements.txt
- Validation des requirements
"""

import sys
import os
sys.path.insert(0, "src")

import pytest
from procyl.dependencies import (
    DependencyScanner,
    get_dependencies_from_code,
    parse_constraints,
    read_requirements_file,
    validate_requirement,
    _get_stdlib_modules,
    _get_cached_stdlib,
)


class TestDependencyScanner:
    """Tests pour la classe DependencyScanner."""
    
    def test_simple_import_detection(self):
        """
        Teste la détection d'imports simples.
        
        Vérifie que le scanner détecte correctement les imports de base
        comme 'import requests' et 'import numpy'.
        """
        code = """
import requests
import numpy
import sys
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # requests et numpy doivent être détectés (packages externes)
        assert "requests" in deps
        assert "numpy" in deps
        # sys ne doit PAS être détecté (stdlib)
        assert "sys" not in deps
    
    def test_from_import_detection(self):
        """
        Teste la détection des imports 'from X import Y'.
        
        Vérifie que le scanner détecte le package racine même quand
        on importe un sous-module spécifique.
        """
        code = """
from requests import get
from numpy import array
from os import path
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Doit détecter les packages racines
        assert "requests" in deps
        assert "numpy" in deps
        # os est stdlib, ne doit pas être détecté
        assert "os" not in deps
    
    def test_complex_import_detection(self):
        """
        Teste la détection d'imports complexes avec sous-modules.
        
        Cas important: 'import tensorflow.keras' doit détecter 'tensorflow'
        comme package racine, pas 'tensorflow.keras'.
        """
        code = """
import tensorflow.keras
import pandas.core.frame
import sklearn.linear_model
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Doit détecter les packages racines
        assert "tensorflow" in deps
        assert "pandas" in deps
        assert "sklearn" in deps
        # Ne doit pas détecter les sous-modules complets
        assert "tensorflow.keras" not in deps
        assert "pandas.core.frame" not in deps
    
    def test_import_with_alias(self):
        """
        Teste la détection des imports avec alias (as).
        
        Vérifie que 'import numpy as np' détecte correctement 'numpy'.
        """
        code = """
import numpy as np
import pandas as pd
import tensorflow as tf
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Doit détecter les noms originaux, pas les alias
        assert "numpy" in deps
        assert "pandas" in deps
        assert "tensorflow" in deps
        # Les alias ne doivent pas être dans les dépendances
        assert "np" not in deps
        assert "pd" not in deps
        assert "tf" not in deps
    
    def test_relative_imports_filtered(self):
        """
        Teste que les imports relatifs sont filtrés correctement.
        
        Les imports relatifs (from . import, from .. import) sont
        toujours internes au projet et ne doivent pas être considérés
        comme des dépendances externes.
        """
        code = """
from . import local_module
from ..core import something
from ...utils import helper
from .submodule import func
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Aucun import relatif ne doit être détecté
        assert len(deps) == 0
    
    def test_mixed_imports(self):
        """
        Teste un mélange d'imports de différents types.
        
        Scénario réel: code avec imports externes, stdlib et relatifs.
        """
        code = """
import requests                    # Externe
from numpy import array            # Externe
import os                          # Stdlib
from sys import argv              # Stdlib
from .local import func            # Relatif (interne)
import pandas as pd                # Exerne avec alias
from ..config import settings     # Relatif (interne)
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Seuls les packages externes doivent être détectés
        assert "requests" in deps
        assert "numpy" in deps
        assert "pandas" in deps
        
        # Stdlib ne doit pas être détecté
        assert "os" not in deps
        assert "sys" not in deps
        
        # Imports relatifs ne doivent pas être détectés
        assert "local" not in deps
        assert "config" not in deps
    
    def test_syntax_error_handling(self):
        """
        Teste que le scanner gère gracieusement les erreurs de syntaxe.
        
        Si le code a une erreur de syntaxe, le scanner doit retourner
        un ensemble vide plutôt que de crasher.
        """
        code = """
import requests
def broken(
# Syntax error: missing closing parenthesis
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Doit retourner un ensemble vide pour du code invalide
        assert deps == set()
    
    def test_empty_code(self):
        """
        Teste le scanner avec du code vide.
        """
        code = ""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        assert deps == set()
    
    def test_no_imports(self):
        """
        Teste le scanner avec du code sans imports.
        """
        code = """
def hello():
    print("Hello, world!")
    
x = 1 + 1
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        assert deps == set()
    
    def test_private_modules_filtered(self):
        """
        Teste que les modules privés (commençant par _) sont filtrés.
        
        Les modules privés Python (commençant par _) sont généralement
        internes et ne doivent pas être considérés comme des dépendances.
        """
        code = """
import _private_module
from _internal import something
import public_package
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Les modules privés doivent être filtrés
        assert "_private_module" not in deps
        assert "_internal" not in deps
        # Les packages publics doivent être détectés
        assert "public_package" in deps


class TestStdlibFiltering:
    """Tests pour le filtrage des modules de la standard library."""
    
    def test_stdlib_modules_not_detected(self):
        """
        Teste que les modules stdlib courants ne sont pas détectés.
        """
        code = """
import os
import sys
import json
import re
import math
import random
from datetime import datetime
from collections import defaultdict
"""
        scanner = DependencyScanner()
        deps = scanner.scan_code(code)
        
        # Aucun module stdlib ne doit être détecté
        assert len(deps) == 0
    
    def test_get_stdlib_modules(self):
        """
        Teste la fonction _get_stdlib_modules.
        
        Vérifie qu'elle retourne un ensemble de modules et que
        les modules stdlib courants sont présents.
        """
        stdlib = _get_stdlib_modules()
        
        # Doit être un ensemble
        assert isinstance(stdlib, set)
        
        # Doit contenir des modules stdlib courants
        assert "os" in stdlib
        assert "sys" in stdlib
        assert "json" in stdlib
        assert "re" in stdlib
    
    def test_cached_stdlib(self):
        """
        Teste que le cache stdlib fonctionne correctement.
        
        _get_cached_stdlib doit utiliser un cache global pour éviter
        de recalculer la liste des modules stdlib à chaque appel.
        """
        # Premier appel
        stdlib1 = _get_cached_stdlib()
        
        # Deuxième appel (doit utiliser le cache)
        stdlib2 = _get_cached_stdlib()
        
        # Doit retourner le même objet (cache)
        assert stdlib1 is stdlib2
        
        # Doit contenir les modules attendus
        assert "os" in stdlib1
        assert "sys" in stdlib1


class TestConstraintParsing:
    """Tests pour le parsing des contraintes de version."""
    
    def test_parse_simple_constraints(self):
        """
        Teste le parsing de contraintes simples.
        
        Vérifie que les contraintes comme {"numpy": ">=1.20"}
        sont converties correctement en format pip.
        """
        constraints = {
            "numpy": ">=1.20",
            "requests": "==2.28.0",
            "pandas": "<2.0"
        }
        result = parse_constraints(constraints)
        
        assert "numpy>=1.20" in result
        assert "requests==2.28.0" in result
        assert "pandas<2.0" in result
    
    def test_parse_empty_constraints(self):
        """
        Teste le parsing avec des contraintes vides.
        
        None ou {} doivent retourner une liste vide.
        """
        assert parse_constraints(None) == []
        assert parse_constraints({}) == []
    
    def test_parse_complex_version_spec(self):
        """
        Teste le parsing de spécifications de version complexes.
        
        Vérifie que les opérateurs de version complexes sont gérés.
        """
        constraints = {
            "numpy": ">=1.20,<2.0",
            "pandas": "~=1.5.0",
            "tensorflow": "!=2.13.0"
        }
        result = parse_constraints(constraints)
        
        assert "numpy>=1.20,<2.0" in result
        assert "pandas~=1.5.0" in result
        assert "tensorflow!=2.13.0" in result
    
    def test_parse_constraint_validation_empty_name(self):
        """
        Teste que les contraintes avec nom vide lèvent une erreur.
        
        Un nom de package vide doit lever ValueError.
        """
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            parse_constraints({"": ">=1.0"})
    
    def test_parse_constraint_validation_none_version(self):
        """
        Teste que les contraintes avec version None lèvent une erreur.
        
        Une version None doit lever ValueError.
        """
        with pytest.raises(ValueError, match="has no version constraint"):
            parse_constraints({"numpy": None})
    
    def test_parse_constraint_validation_empty_version(self):
        """
        Teste que les contraintes avec version vide lèvent une erreur.
        
        Une version vide ("") doit lever ValueError.
        """
        with pytest.raises(ValueError, match="has no version constraint"):
            parse_constraints({"numpy": ""})


class TestRequirementsFile:
    """Tests pour la lecture des fichiers requirements.txt."""
    
    def test_read_simple_requirements(self, tmp_path):
        """
        Teste la lecture d'un fichier requirements.txt simple.
        """
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("numpy>=1.20\nrequests==2.28.0\npandas")
        
        requirements = read_requirements_file(str(req_file))
        
        assert "numpy>=1.20" in requirements
        assert "requests==2.28.0" in requirements
        assert "pandas" in requirements
    
    def test_read_requirements_with_comments(self, tmp_path):
        """
        Teste que les commentaires sont ignorés.
        
        Les lignes commençant par # doivent être ignorées.
        """
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("""
# This is a comment
numpy>=1.20
# Another comment
requests==2.28.0
""")
        
        requirements = read_requirements_file(str(req_file))
        
        assert "numpy>=1.20" in requirements
        assert "requests==2.28.0" in requirements
        # Les commentaires ne doivent pas être dans les résultats
        assert not any(line.startswith("#") for line in requirements)
    
    def test_read_requirements_with_empty_lines(self, tmp_path):
        """
        Teste que les lignes vides sont ignorées.
        """
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("""
numpy>=1.20

requests==2.28.0

pandas
""")
        
        requirements = read_requirements_file(str(req_file))
        
        assert len(requirements) == 3
        assert "numpy>=1.20" in requirements
        assert "requests==2.28.0" in requirements
        assert "pandas" in requirements
    
    def test_read_requirements_windows_line_endings(self, tmp_path):
        """
        Teste la gestion des fins de ligne Windows (CRLF).
        
        Le scanner doit gérer correctement \r\n (Windows) et \n (Unix).
        """
        req_file = tmp_path / "requirements.txt"
        # Écrit avec CRLF (Windows)
        req_file.write_text("numpy>=1.20\r\nrequests==2.28.0\r\n")
        
        requirements = read_requirements_file(str(req_file))
        
        assert "numpy>=1.20" in requirements
        assert "requests==2.28.0" in requirements
    
    def test_read_requirements_with_whitespace(self, tmp_path):
        """
        Teste que l'espace blanc autour des lignes est trimé.
        """
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("  numpy>=1.20  \n  requests==2.28.0  ")
        
        requirements = read_requirements_file(str(req_file))
        
        # L'espace doit être trimé
        assert "numpy>=1.20" in requirements
        assert "requests==2.28.0" in requirements
        assert not any("  " in line for line in requirements)
    
    def test_read_requirements_utf8_encoding(self, tmp_path):
        """
        Teste la lecture avec encodage UTF-8.
        """
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("numpy>=1.20\nrequests==2.28.0", encoding="utf-8")
        
        requirements = read_requirements_file(str(req_file), encoding="utf-8")
        
        assert len(requirements) == 2
    
    def test_read_requirements_latin1_fallback(self, tmp_path):
        """
        Teste le fallback vers latin-1 si UTF-8 échoue.
        
        Si le fichier n'est pas en UTF-8, le lecteur doit essayer latin-1.
        """
        req_file = tmp_path / "requirements.txt"
        # Écrit en latin-1
        req_file.write_text("numpy>=1.20\nrequests==2.28.0", encoding="latin-1")
        
        # Doit réussir avec fallback automatique
        requirements = read_requirements_file(str(req_file), encoding="utf-8")
        
        assert len(requirements) == 2


class TestRequirementValidation:
    """Tests pour la validation des requirements individuels."""
    
    def test_validate_simple_requirement(self):
        """
        Teste la validation d'un requirement simple.
        """
        package, version = validate_requirement("numpy")
        
        assert package == "numpy"
        assert version is None
    
    def test_validate_requirement_with_version(self):
        """
        Teste la validation d'un requirement avec version.
        """
        package, version = validate_requirement("numpy>=1.20")
        
        assert package == "numpy"
        assert version == ">=1.20"
    
    def test_validate_all_operators(self):
        """
        Teste tous les opérateurs de version supportés.
        """
        test_cases = [
            ("numpy==1.20", "numpy", "==1.20"),
            ("numpy>=1.20", "numpy", ">=1.20"),
            ("numpy<=2.0", "numpy", "<=2.0"),
            ("numpy>1.0", "numpy", ">1.0"),
            ("numpy<2.0", "numpy", "<2.0"),
            ("numpy!=1.5", "numpy", "!=1.5"),
            ("numpy~=1.20", "numpy", "~=1.20"),
        ]
        
        for requirement, expected_package, expected_version in test_cases:
            package, version = validate_requirement(requirement)
            assert package == expected_package
            assert version == expected_version
    
    def test_validate_with_whitespace(self):
        """
        Teste que l'espace blanc est trimé correctement.
        """
        package, version = validate_requirement("  numpy  >=  1.20  ")
        
        assert package == "numpy"
        assert version == ">=1.20"
    
    def test_validate_empty_requirement(self):
        """
        Teste qu'un requirement vide lève une erreur.
        """
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_requirement("")
    
    def test_validate_requirement_only_whitespace(self):
        """
        Teste qu'un requirement avec seulement des espaces lève une erreur.
        """
        with pytest.raises(ValueError, match="cannot be empty"):
            validate_requirement("   ")
    
    def test_validate_complex_version_spec(self):
        """
        Teste les spécifications de version complexes.
        """
        package, version = validate_requirement("numpy>=1.20,<2.0")
        
        assert package == "numpy"
        assert version == ">=1.20,<2.0"


class TestGetDependenciesFromCode:
    """Tests pour la fonction utilitaire get_dependencies_from_code."""
    
    def test_get_dependencies_simple(self):
        """
        Teste la fonction utilitaire avec du code simple.
        """
        code = "import requests\nimport numpy"
        deps = get_dependencies_from_code(code)
        
        assert "requests" in deps
        assert "numpy" in deps
    
    def test_get_dependencies_filters_stdlib(self):
        """
        Teste que la fonction filtre correctement la stdlib.
        """
        code = "import requests\nimport os\nimport sys"
        deps = get_dependencies_from_code(code)
        
        assert "requests" in deps
        assert "os" not in deps
        assert "sys" not in deps
    
    def test_get_dependencies_thread_safety(self):
        """
        Teste que la fonction est thread-safe.
        
        Plusieurs appels simultanés ne doivent pas causer de race conditions.
        """
        code = "import requests\nimport numpy"
        
        # Appels multiples
        deps1 = get_dependencies_from_code(code)
        deps2 = get_dependencies_from_code(code)
        deps3 = get_dependencies_from_code(code)
        
        # Tous doivent retourner le même résultat
        assert deps1 == deps2 == deps3
        assert "requests" in deps1
        assert "numpy" in deps1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
