"""
EcoTrace AI — Demo Presets
───────────────────────────
Four predefined scenario presets for the live demo.
Each preset returns a dict that maps directly onto session_state keys
used by the verification page and demo controls panel.

No Streamlit imports — pure data.
"""

from __future__ import annotations


PRESETS: dict[str, dict] = {

    # ── Preset 1: Successful Dismantled Item ───────────────────────────────
    "Preset 1 — Successful Dismantled Item": {
        "item_state":             "dismantled",
        "component":              "PCB",
        "component_confidence":   0.94,
        "material_plausibility":  0.90,
        "facility_validity":      1.00,
        "gps_validity":           0.96,
        "image_quality":          0.88,
        "weight_consistency":     0.93,
        "completion_evidence":    True,
        "within_time_window":     True,
        "narration_hard_gate":    True,
        # Expected outcomes (informational):
        "_expected_trust_score":  ">0.80",
        "_expected_gate":         "PASSED",
        "_expected_badge":        "AUTO-ISSUED",
    },

    # ── Preset 2: High Trust but No Processing Proof ───────────────────────
    "Preset 2 — High Trust, No Processing Proof": {
        "item_state":             "dismantled",
        "component":              "PCB",
        "component_confidence":   0.94,
        "material_plausibility":  0.90,
        "facility_validity":      1.00,
        "gps_validity":           0.96,
        "image_quality":          0.88,
        "weight_consistency":     0.93,
        "completion_evidence":    False,   # <-- key toggle
        "within_time_window":     True,
        "narration_hard_gate":    True,
        # Expected outcomes:
        "_expected_trust_score":  ">0.80 (AUTO-VERIFIED)",
        "_expected_gate":         "FAILED",
        "_expected_badge":        "NOT ISSUED",
    },

    # ── Preset 3: Low Evidence Quality ────────────────────────────────────
    "Preset 3 — Low Evidence Quality": {
        "item_state":             "dismantled",
        "component":              "PCB",
        "component_confidence":   0.45,
        "material_plausibility":  0.50,
        "facility_validity":      0.75,   # reduced so score lands < 0.55 (REJECTED)
        "gps_validity":           0.50,
        "image_quality":          0.50,
        "weight_consistency":     0.55,
        "completion_evidence":    False,
        "within_time_window":     False,
        "narration_hard_gate":    True,
        # Expected outcomes:
        "_expected_trust_score":  "<0.55 (REJECTED)",
        "_expected_gate":         "FAILED",
        "_expected_badge":        "REJECTED",
    },

    # ── Preset 4: Intact Device ────────────────────────────────────────────
    "Preset 4 — Intact Device": {
        "item_state":             "intact",
        "component":              "PCB",   # not used in intact mode
        "component_confidence":   0.94,    # not used
        "material_plausibility":  0.90,    # not used
        "ocr_confidence":         0.92,
        "serial_uniqueness":      1.00,
        "facility_validity":      1.00,
        "gps_validity":           0.96,
        "image_quality":          0.88,
        "weight_consistency":     0.93,
        "completion_evidence":    True,
        "within_time_window":     True,
        "narration_hard_gate":    True,
        # Expected outcomes:
        "_expected_trust_score":  ">0.80",
        "_expected_gate":         "PASSED",
        "_expected_badge":        "AUTO-ISSUED",
    },
}


def get_preset_names() -> list[str]:
    return list(PRESETS.keys())


def get_preset(name: str) -> dict:
    """Return a copy of the preset so session state mutations don't pollute it."""
    return dict(PRESETS.get(name, PRESETS["Preset 1 — Successful Dismantled Item"]))


def apply_preset_to_state(name: str, state: dict) -> None:
    """
    Write preset values directly into a mutable state dict (e.g. st.session_state).
    Internal _expected_* keys are stripped.
    """
    preset = get_preset(name)
    for key, value in preset.items():
        if not key.startswith("_"):
            state[key] = value
