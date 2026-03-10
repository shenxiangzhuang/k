# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownParameterType=false, reportUnknownLambdaType=false
"""OpenTelemetry setup helpers for kcastle."""

from __future__ import annotations

from typing import Any

import opentelemetry.trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_otel(endpoint: str) -> Any:
    """Create and register an OTLP exporter-backed tracer provider."""
    resource = Resource.create({"service.name": "kcastle"})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=endpoint.startswith("http://"),
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    opentelemetry.trace.set_tracer_provider(provider)
    return provider