from pathlib import Path

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Procedure
from core.serializers import ProcedureSerializer, RuleEvaluationInputSerializer
from engine import RuleEvaluator, RulePackLoader


class ProcedureViewSet(viewsets.ModelViewSet):
    queryset = Procedure.objects.select_related("document").all()
    serializer_class = ProcedureSerializer
    permission_classes = [AllowAny]


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
