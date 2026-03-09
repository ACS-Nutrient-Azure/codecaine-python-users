import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.aws.xray import AwsXRayPropagator
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def setup_telemetry() -> None:
    """OTel TracerProvider / MeterProvider 초기화.

    OTEL_EXPORTER_OTLP_ENDPOINT 환경변수가 없으면 no-op으로 동작합니다 (로컬 개발환경).
    ECS 환경에서는 task definition이 환경변수를 주입하므로 자동 활성화됩니다.

    읽는 환경변수 (ECS task definition에서 주입):
      OTEL_EXPORTER_OTLP_ENDPOINT  - ADOT sidecar gRPC 주소 (http://localhost:4317)
      OTEL_SERVICE_NAME            - 서비스 이름
      OTEL_RESOURCE_ATTRIBUTES     - 추가 리소스 속성 (deployment.environment=dev 등)
    """
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not otlp_endpoint:
        return

    # OTEL_SERVICE_NAME, OTEL_RESOURCE_ATTRIBUTES 환경변수를 자동으로 읽음
    resource = Resource.create({})

    # Traces
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics (30초 간격 export)
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=otlp_endpoint),
                export_interval_millis=30_000,
            )
        ],
    )
    metrics.set_meter_provider(meter_provider)

    # Propagators: AWS X-Ray + W3C TraceContext
    # OTEL_PROPAGATORS 환경변수(xray,tracecontext,baggage)와 동일한 순서
    set_global_textmap(
        CompositePropagator([AwsXRayPropagator(), TraceContextTextMapPropagator()])
    )
