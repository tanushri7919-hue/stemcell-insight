"""
test_prediction.py - Automated tests for the rule-based cell-fate reasoning engine.
"""

import pytest
from modules.prediction_engine import evaluate_cell_fate_rules


def test_msc_osteogenesis_prediction():
    """Test MSC osteoblast prediction when required signals are supplied."""
    outcomes = evaluate_cell_fate_rules(
        source_cell_id="MSC",
        target_cell="Osteoblast",
        available_signals=["BMP-2", "Dexamethasone", "Ascorbic Acid (Vitamin C)", "beta-Glycerophosphate"],
        culture_format="Standard Tissue Culture Polystyrene (Adherent Monolayer)"
    )
    assert len(outcomes) >= 1
    best_outcome = outcomes[0]
    assert best_outcome["target_cell"] == "Osteoblast"
    assert best_outcome["compatibility_level"] == "High"
    assert "BMP-2" in best_outcome["matched_req"]
    assert len(best_outcome["missing_req"]) == 0


def test_msc_adipogenesis_prediction():
    """Test MSC adipocyte prediction with adipogenic cocktail."""
    outcomes = evaluate_cell_fate_rules(
        source_cell_id="MSC",
        target_cell="Adipocyte",
        available_signals=["Dexamethasone", "IBMX", "Indomethacin", "Insulin"],
        culture_format="Standard Tissue Culture Polystyrene (Adherent Monolayer)"
    )
    assert len(outcomes) >= 1
    best_outcome = outcomes[0]
    assert best_outcome["target_cell"] == "Adipocyte"
    assert best_outcome["compatibility_level"] == "High"


def test_missing_signals_detection():
    """Test that missing required signals are explicitly flagged."""
    outcomes = evaluate_cell_fate_rules(
        source_cell_id="MSC",
        target_cell="Osteoblast",
        available_signals=["Dexamethasone"],  # Missing BMP-2, Ascorbic Acid, beta-Glycerophosphate
        culture_format="Standard Tissue Culture Polystyrene (Adherent Monolayer)"
    )
    assert len(outcomes) >= 1
    best_outcome = outcomes[0]
    assert best_outcome["compatibility_level"] in ("Partial", "Low")
    assert len(best_outcome["missing_req"]) > 0


def test_incompatible_source_target_pair():
    """Test that biologically incompatible requests (e.g. HSC -> Cardiomyocyte) are rejected."""
    outcomes = evaluate_cell_fate_rules(
        source_cell_id="HSC",
        target_cell="Cardiomyocyte",
        available_signals=["CHIR99021", "IWP-2"],
        culture_format="Standard Tissue Culture Polystyrene (Adherent Monolayer)"
    )
    assert len(outcomes) == 1
    assert outcomes[0]["status"] == "Incompatible Potency"
    assert "lacks the developmental potency" in outcomes[0]["reasoning"]


def test_explore_all_compatible_fates():
    """Test that querying without a target cell returns all valid candidate fates."""
    outcomes = evaluate_cell_fate_rules(
        source_cell_id="MSC",
        target_cell=None,
        available_signals=["BMP-2", "Dexamethasone"],
        culture_format="Standard Tissue Culture Polystyrene (Adherent Monolayer)"
    )
    assert len(outcomes) >= 3
    targets = [o["target_cell"] for o in outcomes]
    assert "Osteoblast" in targets
    assert "Adipocyte" in targets
    assert "Chondrocyte" in targets
