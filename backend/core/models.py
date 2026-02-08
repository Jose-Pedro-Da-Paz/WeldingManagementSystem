from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TimeStampedModel):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class RuleSet(TimeStampedModel):
    standard = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.standard} ({self.version})"


class Document(TimeStampedModel):
    STATUS_VALID = "VALID"
    STATUS_WARNING = "WARNING"
    STATUS_INVALID = "INVALID"
    STATUS_CHOICES = [
        (STATUS_VALID, "Valid"),
        (STATUS_WARNING, "Warning"),
        (STATUS_INVALID, "Invalid"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_VALID)
    active_rule_set = models.ForeignKey(RuleSet, on_delete=models.PROTECT)


class DocumentVersion(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    version = models.PositiveIntegerField()
    payload = models.JSONField(default=dict)
    changed_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("document", "version")


class Procedure(TimeStampedModel):
    TYPE_PWPS = "pWPS"
    TYPE_PQR = "PQR"
    TYPE_WPS = "WPS"
    TYPE_CHOICES = [(TYPE_PWPS, "pWPS"), (TYPE_PQR, "PQR"), (TYPE_WPS, "WPS")]

    document = models.OneToOneField(Document, on_delete=models.CASCADE)
    procedure_type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    parent_procedure = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)


class Welder(TimeStampedModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=100)


class Qualification(TimeStampedModel):
    welder = models.ForeignKey(Welder, on_delete=models.CASCADE, related_name="qualifications")
    procedure = models.ForeignKey(Procedure, on_delete=models.PROTECT)
    continuity_until = models.DateField(null=True, blank=True)


class RuleEvaluationResult(TimeStampedModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    rule_set = models.ForeignKey(RuleSet, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=Document.STATUS_CHOICES)
    errors = models.JSONField(default=list)
    warnings = models.JSONField(default=list)
    explanations = models.JSONField(default=list)
