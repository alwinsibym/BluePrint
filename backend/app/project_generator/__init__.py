"""Project Generator package.

Provides a deterministic, template‑driven project generation pipeline that
consumes the ``GenerationContext`` produced by the Scaffold AI Agent.

Sub‑modules
~~~~~~~~~~~
* ``loader``       – discovers and loads Jinja2 template packs
* ``renderer``     – renders individual templates with a context dict
* ``file_generator`` – builds the complete file list from the context
* ``builder``      – orchestrates the full generation pipeline
* ``validator``    – post‑generation sanity checks
"""
