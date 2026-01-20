from django import forms
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import get_user_model

from content.models import ContentItem
from crm.models import Client
from operations.models import Activity, Service, ServiceCategory
from tasks.models import Task, TaskChecklistItem
from wigs.models import CareWig


class ActivityForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.none(),
        required=False,
        label="Prestation",
        empty_label="Sélectionner une prestation",
    )
    quantity = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        label="Quantité",
        widget=forms.NumberInput(attrs={"placeholder": "Quantité"}),
    )
    unit_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=10,
        label="Prix unitaire",
        widget=forms.NumberInput(attrs={"placeholder": "Prix unitaire"}),
    )
    estimated_end_at = forms.DateTimeField(
        required=False,
        input_formats=["%d/%m/%Y %H:%M"],
        widget=forms.DateTimeInput(
            attrs={
                "class": "datetime-picker",
                "placeholder": "jj/mm/aaaa hh:mm",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = Activity
        fields = [
            "type",
            "client",
            "assigned_staff",
            "expected_amount",
            "estimated_end_at",
            "notes",
            "content_possible",
        ]
        widgets = {
            "client": forms.TextInput(attrs={"placeholder": "Nom du client"}),
            "expected_amount": forms.NumberInput(
                attrs={"placeholder": "Montant attendu (auto si prestation)"}
            ),
            "notes": forms.Textarea(attrs={"placeholder": "Notes internes"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True).order_by(
            "name"
        )
        self.fields["expected_amount"].required = False
        self.order_fields(
            [
                "type",
                "service",
                "quantity",
                "unit_price",
                "client",
                "assigned_staff",
                "expected_amount",
                "estimated_end_at",
                "notes",
                "content_possible",
            ]
        )


class ActivityStatusForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["status"]


class CareWigForm(forms.ModelForm):
    promised_date = forms.DateField(
        required=False,
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            attrs={
                "placeholder": "jj/mm/aaaa",
                "autocomplete": "off",
                "class": "date-picker",
            }
        ),
    )

    class Meta:
        model = CareWig
        fields = ["client", "promised_date", "status", "notes"]
        widgets = {
            "client": forms.TextInput(attrs={"placeholder": "Nom de la cliente"}),
            "notes": forms.Textarea(attrs={"placeholder": "Notes"}),
        }


class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            attrs={"placeholder": "jj/mm/aaaa", "class": "date-picker"}
        ),
    )

    class Meta:
        model = Task
        fields = ["title", "description", "status", "assigned_to", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Titre de la tâche"}),
            "description": forms.Textarea(
                attrs={"placeholder": "Description ou consignes"}
            ),
        }


class TaskChecklistForm(forms.ModelForm):
    class Meta:
        model = TaskChecklistItem
        fields = ["label", "order"]
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": "Libellé"}),
            "order": forms.NumberInput(attrs={"placeholder": "Ordre"}),
        }


class ContentItemForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        required=False,
        input_formats=["%d/%m/%Y %H:%M"],
        widget=forms.DateTimeInput(
            attrs={
                "placeholder": "jj/mm/aaaa hh:mm",
                "autocomplete": "off",
                "class": "datetime-picker",
            }
        ),
    )

    class Meta:
        model = ContentItem
        fields = [
            "title",
            "description",
            "platform",
            "status",
            "scheduled_at",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Titre du contenu"}),
            "description": forms.Textarea(
                attrs={"placeholder": "Résumé du contenu"}
            ),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Identifiant",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Votre identifiant"}
        ),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Votre mot de passe"}
        ),
    )


class PrestationsPOSForm(forms.Form):
    type = forms.ChoiceField(
        choices=Activity.Type.choices,
        label="Type d'activité",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    services = forms.MultipleChoiceField(
        required=False,
        choices=[],
        label="Prestations",
        widget=forms.SelectMultiple(
            attrs={"class": "form-select", "size": 8}
        ),
    )
    quantity = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        label="Quantité (par prestation)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    unit_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=10,
        label="Prix unitaire (optionnel)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    client_existing = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        required=False,
        label="Cliente existante",
        empty_label="Sélectionner une cliente",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    client_name = forms.CharField(
        required=False,
        label="Nouvelle cliente",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Nom de la cliente"}
        ),
    )
    client_phone = forms.CharField(
        required=False,
        label="Téléphone",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+225..."}
        ),
    )
    assigned_staff = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        required=False,
        label="Collaborateur",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    expected_amount = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        max_digits=10,
        label="Montant (achat/produit)",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Montant total"}
        ),
    )
    notes = forms.CharField(
        required=False,
        label="Notes / référence",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "Notes"}
        ),
    )
    content_possible = forms.BooleanField(
        required=False,
        label="Contenu possible",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = ServiceCategory.objects.filter(is_active=True).prefetch_related(
            "services"
        )
        choices = []
        for category in categories:
            services = category.services.filter(is_active=True).order_by("name")
            if not services.exists():
                continue
            choices.append(
                (
                    category.name,
                    [(str(service.id), service.name) for service in services],
                )
            )
        self.fields["services"].choices = choices
        self.fields["client_existing"].queryset = Client.objects.order_by("name")
        self.fields["assigned_staff"].queryset = get_user_model().objects.order_by(
            "first_name", "last_name"
        )

    def clean_services(self):
        service_ids = self.cleaned_data.get("services") or []
        return list(Service.objects.filter(id__in=service_ids, is_active=True))

    def clean(self):
        cleaned_data = super().clean()
        activity_type = cleaned_data.get("type")
        services = cleaned_data.get("services") or []
        expected_amount = cleaned_data.get("expected_amount")
        client_existing = cleaned_data.get("client_existing")
        client_name = cleaned_data.get("client_name", "").strip()

        if activity_type == Activity.Type.SERVICE and not services:
            self.add_error("services", "Sélectionnez au moins une prestation.")
        if activity_type == Activity.Type.PRODUCT_PURCHASE and expected_amount is None:
            self.add_error("expected_amount", "Le montant est requis pour un achat.")
        if not client_existing and not client_name:
            self.add_error(
                "client_name",
                "Sélectionnez une cliente existante ou saisissez un nouveau nom.",
            )

        return cleaned_data
