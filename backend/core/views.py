from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Procedure, RuleSet
from core.serializers import ProcedureSerializer, RuleEvaluationInputSerializer
from engine.evaluator import evaluate_rules


class ProcedureViewSet(viewsets.ModelViewSet):
    queryset = Procedure.objects.select_related("document").all()
    serializer_class = ProcedureSerializer


class RuleEvaluationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RuleEvaluationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ruleset = RuleSet.objects.get(slug=serializer.validated_data["standard_slug"])
        result = evaluate_rules(
            ruleset.slug,
            serializer.validated_data["current"],
            serializer.validated_data["previous"],
        )
        return Response(result, status=status.HTTP_200_OK)
