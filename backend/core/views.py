from pathlib import Path

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Procedure, WelderOperatorCertificate
from core.pdf_export import generate_certificate_pdf
from core.serializers import (
    ProcedureSerializer,
    RuleEvaluationInputSerializer,
    WelderOperatorCertificateSerializer,
)
from engine import RuleEvaluator, RulePackLoader


class ProcedureViewSet(viewsets.ModelViewSet):
    queryset = Procedure.objects.select_related("document").all()
    serializer_class = ProcedureSerializer
    permission_classes = [AllowAny]


class CertificateViewSet(viewsets.ModelViewSet):
    queryset = (
        WelderOperatorCertificate.objects.select_related("organization")
        .prefetch_related("result_documents", "signatures", "revalidations")
        .all()
    )
    serializer_class = WelderOperatorCertificateSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=["post"], url_path="export-pdf")
    def export_pdf(self, request, pk=None):
        certificate = self.get_object()
        pdf_data = generate_certificate_pdf(certificate)
        response = HttpResponse(pdf_data, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="certificate-{certificate.certificate_number}.pdf"'
        return response


class RuleEvaluationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RuleEvaluationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rules_root = Path(__file__).resolve().parents[2] / "rules"
        loader = RulePackLoader(rules_root)
        pack = loader.load(serializer.validated_data["rule_pack"])

        evaluator = RuleEvaluator(pack, debug=serializer.validated_data["debug"])
        result = evaluator.evaluate(
            serializer.validated_data["payload"],
            previous_payload=serializer.validated_data["previous_payload"],
        )
        return Response(result, status=status.HTTP_200_OK)
