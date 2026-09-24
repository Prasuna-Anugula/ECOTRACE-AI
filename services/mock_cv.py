"""
EcoTrace AI — Mock Computer Vision Service
──────────────────────────────────────────
THIS IS A PROTOTYPE MOCK.
No real CV model is used. Component classification outputs are synthetically
generated to demonstrate the EcoTrace pipeline architecture.

Future integration: replace this module with a real component classifier that
accepts an image and returns {"component": "PCB", "confidence": 0.xx}.
The Trust Score engine (trust_score.py) will not need to change.
"""

from __future__ import annotations
from config import COMPONENT_CLASSES


# Default confidence values per component class (realistic mock ranges)
_DEFAULT_CONFIDENCE: dict[str, float] = {
    "PCB":     0.94,
    "Battery": 0.87,
    "Casing":  0.81,
    "Cable":   0.78,
}


def predict_component(
    image=None,
    component: str = "PCB",
    confidence: float | None = None,
) -> dict:
    """
    Simulate a CV component classification of a dismantled e-waste item.

    Parameters
    ----------
    image      : uploaded image object (ignored in mock — kept for API parity)
    component  : component class selected via demo controls
    confidence : classification confidence to simulate (0.0 – 1.0)
                 if None, uses a realistic default for the given component

    Returns
    -------
    dict with keys: component, confidence, possible_classes, mode, disclaimer
    """
    if component not in COMPONENT_CLASSES:
        component = COMPONENT_CLASSES[0]

    conf = confidence if confidence is not None else _DEFAULT_CONFIDENCE.get(component, 0.80)

    return {
        "component":       component,
        "confidence":      round(float(conf), 4),
        "possible_classes": COMPONENT_CLASSES,
        "mode":            "MOCK",
        "disclaimer": (
            "Prototype CV — mocked output. "
            "No real computer vision model has been applied. "
            "For architecture validation only."
        ),
    }
