# Consensus assumptions and limits

BLOCKLAB 360 demonstrates a simplified honest-majority proof-of-work idea. A candidate block must satisfy its leading-zero difficulty and extend the current valid tip. Active simulated peers synchronize to the canonical chain height. If chain-copy selection is expanded in a later version, the intended educational rule is longest valid chain; ties use first-seen.

This is **not production BFT**. It has no Sybil resistance, peer authentication, adversarial network model, transaction signatures, economic incentives, real finality, robust fork-choice under concurrent miners, or Byzantine quorum protocol. All peers live in one process and share one canonical engine. Latency and drop-rate fields are simulation settings, not real packet delivery guarantees.
