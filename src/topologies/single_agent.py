from src.agent import Agent
from src.schemas import FinalSelection


class SingleAgentTopology:
    """One clinical rewriter with all routed expertise and no aggregation."""

    def __init__(self, agents):
        if not agents:
            raise ValueError("Single-agent baseline requires routed clinical roles.")
        self.agent = Agent(
            name="Single clinical rewriter",
            role_description=(
                "You are one clinical question editor with the following combined "
                "clinical expertise:\n\n"
                + "\n\n".join(
                    f"{agent.name}: {agent.role_description}" for agent in agents
                )
            ),
            llm=agents[0].llm,
        )
        self.extra_llm_calls = 0

    def run(self, question):
        # Reuse the exact proposal task, fidelity rules, and output schema.
        proposal = self.agent.propose_revision(question)
        selection = FinalSelection(
            revised_question=proposal.revised_question,
            decision_method="single_agent",
            source_agents=[self.agent.name],
        )
        return [proposal], [], [], selection
