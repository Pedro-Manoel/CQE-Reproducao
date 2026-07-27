"""Compatibility shim.

The official evaluation harness (satya77/CQE_Evaluation, tagger.py) imports
``from CQE.NumParser import NumParser``. In this pre-submission version of the
library the ``NumParser`` class lives in :mod:`CQE.CQE`. Re-export it here so the
evaluation code runs unchanged against this version of CQE.
"""
from CQE.CQE import NumParser  # noqa: F401

__all__ = ["NumParser"]
