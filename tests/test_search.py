"""
test_search.py - Automated tests for keyword matching, synonym expansion, and chatbot QA.
"""

import pytest
from utils.search import expand_query_terms, search_all_entities
from modules.chatbot import answer_question


def test_synonym_expansion():
    """Test that biological synonyms are correctly resolved."""
    terms_oct4 = expand_query_terms("OCT4")
    assert "pou5f1" in terms_oct4 or "oct4" in terms_oct4

    terms_msc = expand_query_terms("MSC")
    assert any("mesenchymal" in t for t in terms_msc)

    terms_tuj1 = expand_query_terms("TUJ1")
    assert "tubb3" in terms_tuj1


def test_multi_entity_search():
    """Test searching across multiple tables with a single keyword."""
    results = search_all_entities("Osteoblast")
    assert len(results["differentiation"]) >= 1

    results_marker = search_all_entities("RUNX2")
    assert len(results_marker["markers"]) >= 1


def test_chatbot_esc_vs_ipsc():
    """Test chatbot answering comparison between ESCs and iPSCs."""
    response, refs = answer_question("What is the difference between ESCs and iPSCs?")
    assert "Embryonic Stem Cells" in response
    assert "Induced Pluripotent Stem Cells" in response
    assert len(refs) >= 1


def test_chatbot_msc_capabilities():
    """Test chatbot answering MSC differentiation capabilities."""
    response, refs = answer_question("What are the differentiation capabilities of MSCs?")
    assert "Osteogenic Lineage" in response
    assert "Adipogenic Lineage" in response
    assert "Chondrogenic Lineage" in response
    assert len(refs) >= 1


def test_chatbot_bmp_signaling():
    """Test chatbot answering role of BMP signaling."""
    response, refs = answer_question("What is the role of BMP signalling?")
    assert "BMP" in response
    assert "RUNX2" in response or "SMAD" in response
    assert len(refs) >= 1


def test_chatbot_unsupported_question():
    """Test chatbot guardrail for questions outside the curated database."""
    response, refs = answer_question("What is the weather in Paris?")
    assert "This information is not currently available in the curated StemCell Insight knowledge base." in response
    assert len(refs) == 0
