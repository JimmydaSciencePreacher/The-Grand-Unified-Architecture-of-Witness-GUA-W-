import numpy as np
from sentence_transformers import SentenceTransformer, util


class GUAWSemanticAuditor:

    def __init__(self, model_name="all-MiniLM-L6-v2", drift_threshold=0.45):
        # Load a lightweight, fast local embedding model
        print(f"Initializing Embedding Node ({model_name})...")
        self.encoder = SentenceTransformer(model_name)

        # PHASE I: THE ANCHOR (Immutable Ground Truth Ledger)
        self.anchor_texts = []
        self.anchor_embeddings = None
        self.drift_threshold = drift_threshold
        self.audit_ledger = []

    def set_anchors(self, foundational_statements: list[str]):
        """Step 04: Establish Pristine Reference State from primary texts/laws."""
        self.anchor_texts = foundational_statements
        self.anchor_embeddings = self.encoder.encode(
            foundational_statements, convert_to_tensor=True
        )
        print(f"⚓ Locked {len(self.anchor_texts)} Anchor axioms into memory.\n")

    def audit_witness_claim(self, incoming_claim: str, human_firewall=True):
        """Executes Phase II (Drift Detection) & Phase III (Return/Guardrail)

        against a real text claim.
        """
        if self.anchor_embeddings is None:
            raise ValueError(
                "System unanchored. Load Phase I Anchor texts first."
            )

        # Encode the incoming claim ("The Witness")
        claim_embedding = self.encoder.encode(
            incoming_claim, convert_to_tensor=True
        )

        # STEP 05: Identifying the Drift (Compare claim against all Anchors)
        cosine_scores = util.cos_sim(claim_embedding, self.anchor_embeddings)
        best_match_idx = int(np.argmax(cosine_scores.cpu().numpy()))
        highest_alignment = float(cosine_scores[best_match_idx])

        # Drift is the inverse of semantic alignment (0.0 = exact match, 1.0 = total divergence)
        drift_score = 1.0 - highest_alignment

        # STEP 06: Root Cause Analysis (Check Triple Constraint / AXIOM 001 boundary)
        axiom_001_violated = drift_score > self.drift_threshold

        # STEP 07 - 12: Reconciliation & Ledger Logging
        if axiom_001_violated and human_firewall:
            action = "🛡️ BLOCKED BY FIREWALL (Routed to Human Steward)"
            accepted = False
        elif axiom_001_violated and not human_firewall:
            action = "⚠️ UNCONTROLLED INFLUX (Drift Accepted into Pool)"
            accepted = True
        else:
            action = "✅ VERIFIED (Converges with Anchor)"
            accepted = True

        result = {
            "claim": incoming_claim,
            "closest_anchor": self.anchor_texts[best_match_idx],
            "alignment_score": round(highest_alignment, 4),
            "drift_score": round(drift_score, 4),
            "violated": axiom_001_violated,
            "action": action,
            "accepted": accepted,
        }
        self.audit_ledger.append(result)
        return result


# ==========================================
# EXAMPLE EXECUTION: AUDITING LIVE CLAIMS
# ==========================================
if __name__ == "__main__":
    # 1. Initialize the Auditor
    auditor = GUAWSemanticAuditor(drift_threshold=0.55)

    # 2. Load Phase I Anchors (Your foundational constraints)
    core_anchors = [
        (
            "Information is conserved at the event horizon via 2D holographic"
            " encoding."
        ),
        (
            "Raw observational data must never be filtered by pre-existing"
            " conclusions."
        ),
        (
            "Physical laws operate consistently across all observable frames of"
            " reference."
        ),
    ]
    auditor.set_anchors(core_anchors)

    # 3. Test incoming statements ("Telemetry / Witness Claims")
    test_claims = [
        (
            "Black holes preserve quantum information on their two-dimensional"
            " boundary."
        ),
        "Scientists should discard measurements that contradict their model.",
        "The stock market will rally next Tuesday due to lunar phases.",
    ]

    print("=== RUNNING GUA-W SEMANTIC AUDIT ===")
    for claim in test_claims:
        report = auditor.audit_witness_claim(claim, human_firewall=True)
        print(f"\nIncoming Claim : '{report['claim']}'")
        print(f"Closest Anchor : '{report['closest_anchor']}'")
        print(
            f"Drift Score    : {report['drift_score']} (Alignment:"
            f" {report['alignment_score']})"
        )
        print(f"Audit Verdict  : {report['action']}")
