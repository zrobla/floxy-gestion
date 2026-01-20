from django import forms

from training.models import TrainingActionPlan, TrainingEvaluation


class TrainingEvaluationForm(forms.ModelForm):
    class Meta:
        model = TrainingEvaluation
        fields = ["score", "comments"]
        widgets = {
            "score": forms.NumberInput(
                attrs={"placeholder": "Score sur 100", "min": 0, "max": 100}
            ),
            "comments": forms.Textarea(
                attrs={"placeholder": "Commentaires"}
            ),
        }


class TrainingActionPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingActionPlan
        fields = ["title", "description", "due_date", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Objectif 90 jours"}),
            "description": forms.Textarea(
                attrs={"placeholder": "Détails de l'action", "rows": 3}
            ),
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "date-picker"}
            ),
        }
