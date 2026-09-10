import pytest
from backend.core.orchestrator import MultiAgentOrchestrator
from backend.core.models import VerificationRequest, FactVerdict, ClaimCategory

@pytest.fixture(scope="module")
def orchestrator():
    return MultiAgentOrchestrator()

def test_1_strip_suggested_answer_true(orchestrator):
    """Input: 'India became independent in 1947 true' -> TRUE"""
    req = VerificationRequest(query="India became independent in 1947 true")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE
    assert "true" not in res.claim.lower().split()

def test_2_strip_suggested_answer_false(orchestrator):
    """Input: '2 + 2 = 5 false' -> FALSE"""
    req = VerificationRequest(query="2 + 2 = 5 false")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE
    assert "4" in str(res.correct_statement)

def test_3_water_does_not_contain_oxygen(orchestrator):
    """'Water does not contain oxygen.' -> FALSE"""
    req = VerificationRequest(query="Water does not contain oxygen.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE

def test_4_sun_does_not_rise_in_west(orchestrator):
    """'The Sun does not rise in the west.' -> TRUE"""
    req = VerificationRequest(query="The Sun does not rise in the west.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_5_india_not_in_europe(orchestrator):
    """'India is not in Europe.' -> TRUE"""
    req = VerificationRequest(query="India is not in Europe.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_6_india_not_in_asia(orchestrator):
    """'India is not in Asia.' -> FALSE"""
    req = VerificationRequest(query="India is not in Asia.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE

def test_7_humans_cannot_breathe_underwater(orchestrator):
    """'Humans cannot breathe underwater without equipment.' -> TRUE"""
    req = VerificationRequest(query="Humans cannot breathe underwater without equipment.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_8_math_equation_true(orchestrator):
    """'2 + 2 = 4' -> TRUE"""
    req = VerificationRequest(query="2 + 2 = 4")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_9_math_multiplication(orchestrator):
    """'10 × 5 = 50' -> TRUE"""
    req = VerificationRequest(query="10 × 5 = 50")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_10_math_less_than_false(orchestrator):
    """'100 is less than 20' -> FALSE"""
    req = VerificationRequest(query="100 is less than 20")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE

def test_11_math_percentage(orchestrator):
    """'25% of 200 is 50' -> TRUE"""
    req = VerificationRequest(query="25% of 200 is 50")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_12_all_birds_can_fly(orchestrator):
    """'All birds can fly.' -> FALSE (penguins, ostriches cannot fly)"""
    req = VerificationRequest(query="All birds can fly.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE

def test_13_pacific_larger_than_atlantic(orchestrator):
    """'The Pacific Ocean is larger than the Atlantic Ocean.' -> TRUE"""
    req = VerificationRequest(query="The Pacific Ocean is larger than the Atlantic Ocean.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_14_atlantic_larger_than_pacific(orchestrator):
    """'The Atlantic Ocean is larger than the Pacific Ocean.' -> FALSE"""
    req = VerificationRequest(query="The Atlantic Ocean is larger than the Pacific Ocean.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE

def test_15_multiple_claims(orchestrator):
    """'India became independent in 1947 and Mumbai is the capital of India.' -> FALSE"""
    req = VerificationRequest(query="India became independent in 1947 and Mumbai is the capital of India.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE
    assert res.sub_claims is not None
    assert len(res.sub_claims) == 2

def test_16_fish_do_not_live_in_water(orchestrator):
    """'Fish do not live in water.' -> FALSE"""
    req = VerificationRequest(query="Fish do not live in water.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE

def test_17_fish_do_not_live_on_land(orchestrator):
    """'Fish do not live on land.' -> TRUE"""
    req = VerificationRequest(query="Fish do not live on land.")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.TRUE

def test_18_freezing_water_not_ice(orchestrator):
    """'freezing of water will not turns into ice' -> FALSE"""
    req = VerificationRequest(query="freezing of water will not turns into ice")
    res = orchestrator.process(req)
    assert res.verdict == FactVerdict.FALSE
