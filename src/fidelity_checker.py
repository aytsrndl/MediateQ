import os

from src.llm.openai_client import OpenAIClient
from src.schemas import (
    FidelitySelection,
    QuestionInput,
)


class FidelityChecker:
    """
    Independent semantic-fidelity checker used only to
    resolve tied votes in the primary MediateQ mediator.

    The checker does not answer the clinical question.
    """

    def __init__(
        self,
        model: str | None = None,
    ):
        self.model = (
            model
            or os.getenv("FIDELITY_MODEL")
            or "gpt-4.1-mini"
        )

        self.llm = OpenAIClient(
            model=self.model,
        )

    def select(
        self,
        question: QuestionInput,
        candidates: dict[str, str],
        tied_candidate_ids: list[str],
    ) -> str:

        candidate_text = "\n\n".join(
            [
                f"""
CANDIDATE {candidate_id}:
{candidates[candidate_id]}
"""
                for candidate_id in tied_candidate_ids
            ]
        )

        prompt = f"""
You are an independent semantic-fidelity checker in a healthcare
communication research study.

You do NOT answer the clinical question.

ORIGINAL PATIENT QUESTION:
{question.text}

MEDICAL DOMAIN:
{question.domain.value}

HEALTH LITERACY LEVEL:
{question.literacy_level.value}

TIED ANONYMOUS CANDIDATES:
{candidate_text}

TASK:
Select the single candidate that most conservatively preserves
the meaning of the ORIGINAL PATIENT QUESTION.

Prioritize:

1. Preserve the patient's original clinical intent.
2. Preserve the original question type.
3. Do not add symptoms that were not stated.
4. Do not add timing that was not stated.
5. Do not add severity that was not stated.
6. Do not add causes that were not stated.
7. Do not add medications or medical history that were not stated.
8. Do not introduce unsupported clinical interpretation.

If the source question is ambiguous, prefer the candidate that
preserves that ambiguity rather than resolving it by adding
unsupported information.

Do not prefer a candidate merely because it is more detailed,
polished, or medically specific.

Return:
- the anonymous candidate ID that best preserves the source meaning,
- and a short explanation.
"""

        decision = self.llm.generate_structured(
            prompt=prompt,
            output_schema=FidelitySelection,
        )

        if decision.selected_candidate_id not in tied_candidate_ids:
            raise ValueError(
                "Fidelity checker selected invalid candidate "
                f"{decision.selected_candidate_id}."
            )

        return decision.selected_candidate_id