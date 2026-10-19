from src.schemas import (
    Domain,
    LiteracyLevel,
    QuestionInput,
    Vote,
)

import src.topologies.fully_connected as fully_connected_module

from src.topologies.fully_connected import FullyConnectedTopology
from src.topologies.decentralized import DecentralizedTopology


class FakeFidelityChecker:
    """
    Fake checker used so this test does not make a real API call.
    """

    calls = 0

    def __init__(self, *args, **kwargs):
        pass

    def select(
        self,
        question,
        candidates,
        tied_candidate_ids,
    ):
        FakeFidelityChecker.calls += 1

        # Deterministically choose B so we can verify
        # that the checker actually controlled the result.
        return "B"


def make_question():
    return QuestionInput(
        question_id=1,
        text="baby geting enuf milk",
        domain=Domain.INFANT_CARE,
        literacy_level=LiteracyLevel.VERY_LOW,
    )


def test_primary_tie_uses_fidelity_checker():
    print("Testing primary mediator tie...")

    FakeFidelityChecker.calls = 0

    # Replace the real checker with our fake one.
    fully_connected_module.FidelityChecker = FakeFidelityChecker

    topology = FullyConnectedTopology(
        agents=[]
    )

    question = make_question()

    candidates = {
        "A": "Is my baby getting enough milk?",
        "B": "Is the baby getting enough milk?",
    }

    source_agents = {
        "A": ["Agent A"],
        "B": ["Agent B"],
    }

    # One vote for A and one for B -> tie.
    votes = [
        Vote(
            agent_name="Agent 1",
            selected_candidate_id="A",
            brief_reason="A",
        ),
        Vote(
            agent_name="Agent 2",
            selected_candidate_id="B",
            brief_reason="B",
        ),
    ]

    result = topology.select_winner(
        question=question,
        candidates=candidates,
        source_agents=source_agents,
        votes=votes,
    )

    assert FakeFidelityChecker.calls == 1
    assert result.winning_candidate_id == "B"

    assert (
        result.decision_method
        == "blind_vote_with_fidelity_tiebreak"
    )

    assert topology.extra_llm_calls == 1

    print("  Fidelity checker called: PASS")
    print("  Checker selected winner: PASS")
    print("  Extra LLM call counted: PASS")


def test_primary_majority_skips_fidelity_checker():
    print("Testing primary mediator majority vote...")

    FakeFidelityChecker.calls = 0

    fully_connected_module.FidelityChecker = FakeFidelityChecker

    topology = FullyConnectedTopology(
        agents=[]
    )

    question = make_question()

    candidates = {
        "A": "Is my baby getting enough milk?",
        "B": "Is the baby getting enough milk?",
    }

    source_agents = {
        "A": ["Agent A"],
        "B": ["Agent B"],
    }

    votes = [
        Vote(
            agent_name="Agent 1",
            selected_candidate_id="A",
            brief_reason="A",
        ),
        Vote(
            agent_name="Agent 2",
            selected_candidate_id="A",
            brief_reason="A",
        ),
        Vote(
            agent_name="Agent 3",
            selected_candidate_id="B",
            brief_reason="B",
        ),
    ]

    result = topology.select_winner(
        question=question,
        candidates=candidates,
        source_agents=source_agents,
        votes=votes,
    )

    assert FakeFidelityChecker.calls == 0
    assert result.winning_candidate_id == "A"
    assert result.decision_method == "blind_vote"
    assert topology.extra_llm_calls == 0

    print("  Fidelity checker skipped: PASS")
    print("  Majority winner preserved: PASS")


def test_decentralized_tie_skips_fidelity_checker():
    print("Testing decentralized tie...")

    FakeFidelityChecker.calls = 0

    fully_connected_module.FidelityChecker = FakeFidelityChecker

    topology = DecentralizedTopology(
        agents=[]
    )

    question = make_question()

    candidates = {
        "A": "Is my baby getting enough milk?",
        "B": "Is the baby getting enough milk?",
    }

    source_agents = {
        "A": ["Agent A"],
        "B": ["Agent B"],
    }

    votes = [
        Vote(
            agent_name="Agent 1",
            selected_candidate_id="A",
            brief_reason="A",
        ),
        Vote(
            agent_name="Agent 2",
            selected_candidate_id="B",
            brief_reason="B",
        ),
    ]

    result = topology.select_winner(
        question=question,
        candidates=candidates,
        source_agents=source_agents,
        votes=votes,
    )

    assert FakeFidelityChecker.calls == 0

    assert (
        result.decision_method
        == "blind_vote_with_deterministic_tiebreak"
    )

    assert result.winning_candidate_id == "A"
    assert topology.extra_llm_calls == 0

    print("  Fidelity checker skipped: PASS")
    print("  Deterministic resolution used: PASS")


if __name__ == "__main__":

    print()
    print("=" * 60)
    print("FIDELITY TIE-BREAK TESTS")
    print("=" * 60)

    test_primary_tie_uses_fidelity_checker()

    print()

    test_primary_majority_skips_fidelity_checker()

    print()

    test_decentralized_tie_skips_fidelity_checker()

    print()
    print("=" * 60)
    print("ALL FIDELITY TIE-BREAK TESTS PASSED")
    print("=" * 60)