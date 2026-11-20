from src.topologies.fully_connected import FullyConnectedTopology
from src.topologies.independent import IndependentTopology
from src.topologies.decentralized import DecentralizedTopology
from src.topologies.centralized import CentralizedTopology
from src.topologies.hybrid import HybridTopology
from src.topologies.single_agent import SingleAgentTopology


def create_topology(topology_name: str, agents):
    name = topology_name.strip().lower()

    if name == "single_agent":
        return SingleAgentTopology(agents)

    if name == "fully_connected":
        return FullyConnectedTopology(agents)

    if name == "independent":
        return IndependentTopology(agents)

    if name == "decentralized":
        return DecentralizedTopology(agents)

    if name == "centralized":
        return CentralizedTopology(agents)

    if name == "hybrid":
        return HybridTopology(agents)

    raise ValueError(
        f"Unsupported topology: {topology_name}"
    )
