"""
data_validation.py - Scientific data validation and evidence completeness evaluation.
Provides transparent scoring of experimental reporting completeness without making
unsupported claims regarding biological reproducibility.
"""

from typing import Any, Dict, List, Optional, Tuple


def evaluate_evidence_completeness(record: Dict[str, Any], record_type: str = "protocol") -> Dict[str, Any]:
    """Calculate the transparent Evidence Completeness Score (0-100%)
    based on the explicit presence of key experimental reporting dimensions.

    Scientific Disclaimer:
    This score reflects *reporting completeness* in the curated database record.
    It is NOT a measure of experimental quality, biological reproducibility, or paper reliability.
    """
    criteria = []

    if record_type == "protocol":
        # 1. Starting cell identity
        source_cell = record.get("source_cell")
        criteria.append({
            "name": "Starting Cell Identity",
            "present": bool(source_cell and source_cell != "Not reported"),
            "value": source_cell or "Not reported",
            "weight": 10
        })

        # 2. Target differentiated cell identity
        target_cell = record.get("target_cell")
        criteria.append({
            "name": "Target Cell Identity",
            "present": bool(target_cell and target_cell != "Not reported"),
            "value": target_cell or "Not reported",
            "weight": 10
        })

        # 3. Basal medium defined
        medium = record.get("medium")
        criteria.append({
            "name": "Basal Medium Formulation",
            "present": bool(medium and medium != "Not reported"),
            "value": medium or "Not reported",
            "weight": 10
        })

        # 4. Growth factors & signals reported
        gf = record.get("growth_factors")
        criteria.append({
            "name": "Growth Factors / Cytokines",
            "present": bool(gf and gf != "Not reported" and gf != "None reported"),
            "value": gf or "Not reported",
            "weight": 10
        })

        # 5. Small molecules & chemical inducers
        sm = record.get("small_molecules")
        criteria.append({
            "name": "Small Molecules / Chemicals",
            "present": bool(sm and sm != "Not reported" and sm != "None reported"),
            "value": sm or "Not reported",
            "weight": 10
        })

        # 6. Treatment duration specified
        dur = record.get("duration")
        criteria.append({
            "name": "Treatment Duration Specified",
            "present": bool(dur and dur != "Not reported"),
            "value": dur or "Not reported",
            "weight": 10
        })

        # 7. Reported differentiation efficiency
        eff = record.get("reported_efficiency")
        criteria.append({
            "name": "Reported Differentiation Efficiency",
            "present": bool(eff and eff != "Not reported"),
            "value": eff or "Not reported",
            "weight": 10
        })

        # 8. Efficiency measurement method
        eff_m = record.get("efficiency_method")
        criteria.append({
            "name": "Efficiency Quantification Method",
            "present": bool(eff_m and eff_m != "Not reported"),
            "value": eff_m or "Not reported",
            "weight": 10
        })

        # 9. Validation markers reported
        markers = record.get("validation_markers")
        criteria.append({
            "name": "Phenotypic Validation Markers",
            "present": bool(markers and markers != "Not reported"),
            "value": markers or "Not reported",
            "weight": 10
        })

        # 10. Functional validation / assay
        fval = record.get("functional_validation")
        criteria.append({
            "name": "Functional In Vitro / In Vivo Validation",
            "present": bool(fval and fval != "Not reported"),
            "value": fval or "Not reported",
            "weight": 10
        })

    elif record_type == "differentiation":
        criteria = [
            {
                "name": "Source Stem Cell Defined",
                "present": bool(record.get("source_cell_id")),
                "value": record.get("source_cell_id") or "Not reported",
                "weight": 20
            },
            {
                "name": "Target Cell Fate Defined",
                "present": bool(record.get("target_cell")),
                "value": record.get("target_cell") or "Not reported",
                "weight": 20
            },
            {
                "name": "Lineage Annotation",
                "present": bool(record.get("lineage")),
                "value": record.get("lineage") or "Not reported",
                "weight": 20
            },
            {
                "name": "Experimental Induction Summary",
                "present": bool(record.get("conditions_summary")),
                "value": record.get("conditions_summary") or "Not reported",
                "weight": 20
            },
            {
                "name": "Supporting Literature Reference",
                "present": bool(record.get("reference_id")),
                "value": record.get("reference_id") or "Not reported",
                "weight": 20
            }
        ]

    total_weight = sum(c["weight"] for c in criteria)
    earned_weight = sum(c["weight"] for c in criteria if c["present"])
    score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0.0

    missing_items = [c["name"] for c in criteria if not c["present"]]
    present_items = [c["name"] for c in criteria if c["present"]]

    return {
        "score": score,
        "criteria": criteria,
        "missing_items": missing_items,
        "present_items": present_items,
        "total_criteria": len(criteria),
        "satisfied_criteria": len(present_items),
        "disclaimer": (
            "The Evidence Completeness Score indicates the availability of curated experimental "
            "reporting parameters in this record. It is NOT an empirical probability of replication "
            "or a validated metric of biological quality."
        )
    }


def validate_cell_line_record(record: Dict[str, Any]) -> List[str]:
    """Validate data integrity for a cell-line record."""
    errors = []
    if not record.get("cell_line_name"):
        errors.append("Cell line name is required.")
    if not record.get("species"):
        errors.append("Species annotation is required.")
    if record.get("cell_id") not in ("ESC", "IPSC", "MSC", "HSC", "NSC", None):
        errors.append(f"Unrecognized stem cell category: {record.get('cell_id')}")
    return errors
