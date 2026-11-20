import unittest

from src.role_router import create_agents_for_domain, get_roles_for_domain
from src.schemas import Domain, LiteracyLevel, QuestionInput, RevisionProposal
from src.topologies.factory import create_topology


class RecordingLLM:
    def __init__(self):
        self.calls = []

    def generate_structured(self, prompt, output_schema):
        self.calls.append(prompt)
        return output_schema(
            agent_name="model",
            revised_question="When should I seek help?",
            meaning_preserved=True,
            unsupported_information_added=False,
            brief_note="Test response",
        )


class SingleAgentTests(unittest.TestCase):
    def test_all_domains_use_one_call_with_all_routed_expertise(self):
        for domain in Domain:
            with self.subTest(domain=domain):
                llm = RecordingLLM()
                topology = create_topology(
                    "single_agent", create_agents_for_domain(domain, llm)
                )
                question = QuestionInput(
                    question_id=1, text="when get help?", domain=domain,
                    literacy_level=LiteracyLevel.VERY_LOW,
                )
                first, second, votes, final = topology.run(question)
                self.assertEqual(len(llm.calls), 1)
                for role, description in get_roles_for_domain(domain).items():
                    self.assertIn(role, llm.calls[0])
                    self.assertIn(description, llm.calls[0])
                self.assertIn(question.text, llm.calls[0])
                self.assertIn(domain.value, llm.calls[0])
                self.assertEqual(final.revised_question, first[0].revised_question)
                self.assertEqual(final.decision_method, "single_agent")
                self.assertEqual((second, votes, topology.extra_llm_calls), ([], [], 0))


if __name__ == "__main__":
    unittest.main()
