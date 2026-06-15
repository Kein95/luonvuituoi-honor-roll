"""LUONVUITUOI-HONOR ROLL core engine.

A config-driven student honor-roll toolkit: validate ``honor.config.json``,
ingest achievement sources, and serve a public listing + student search +
admin surface. The Flask/CLI bindings live in ``luonvuitoi_honor_cli``;
this package stays web-framework-agnostic so a future serverless handler
can reuse every pure function.
"""

__version__ = "0.1.0"
