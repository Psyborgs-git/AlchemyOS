"""Natural language to SMILES translation.

Uses LLM to convert natural language descriptions to SMILES.
"""

from backend.core.ports.outbound.i_chem_port import IChemPort
from backend.core.ports.outbound.i_llm_port import ILLMPort, Message


class NLToSmiles:
    """Convert natural language to SMILES using LLM."""

    def __init__(self, llm_port: ILLMPort, chem_port: IChemPort) -> None:
        """Initialize NL to SMILES converter.

        Args:
            llm_port: LLM port for text generation
            chem_port: Chemistry port for validation
        """
        self.llm = llm_port
        self.chem = chem_port

    async def convert(self, description: str) -> str | None:
        """Convert natural language description to SMILES.

        Args:
            description: Natural language description of molecule

        Returns:
            SMILES string or None if conversion fails
        """
        # Create prompt for LLM
        prompt = f"""Convert the following molecular description to a valid SMILES string.
Output ONLY the SMILES string, nothing else.

Description: {description}

SMILES:"""

        messages = [Message(role="user", content=prompt)]

        try:
            # Get SMILES from LLM
            response = await self.llm.complete(messages)
            smiles = response.strip()

            # Validate SMILES
            if self.chem.validate_smiles(smiles):
                return smiles
            else:
                return None
        except Exception:
            return None
