from django.db import migrations, models
import django.db.models.deletion


def seed_service_categories(apps, schema_editor):
    ServiceCategory = apps.get_model("operations", "ServiceCategory")
    Service = apps.get_model("operations", "Service")

    categories = [
        {
            "name": "Coiffure & soins capillaires",
            "description": "Coiffure, tresses, lissages et soins capillaires.",
            "image_path": "prestations/coiffure-soins-capillaires-1.png",
        },
        {
            "name": "Soins capillaires premium",
            "description": "Protocoles premium et traitements capillaires avancés.",
            "image_path": "prestations/coiffure-soins-capillaires-2.png",
        },
        {
            "name": "Esthétique & make-up",
            "description": "Maquillage professionnel et soins visage.",
            "image_path": "prestations/esthetique.png",
        },
        {
            "name": "Onglerie",
            "description": "Manucure, pédicure et design d'ongles.",
            "image_path": "prestations/onglerie.png",
        },
        {
            "name": "Perruques",
            "description": "Vente, pose et entretien des perruques.",
            "image_path": "",
        },
        {
            "name": "Soins visage & corps",
            "description": "Soins visage, corps et bien-être.",
            "image_path": "",
        },
    ]

    category_map = {}
    for category in categories:
        item, _ = ServiceCategory.objects.get_or_create(
            name=category["name"],
            defaults={
                "description": category["description"],
                "image_path": category["image_path"],
                "is_active": True,
            },
        )
        category_map[item.name] = item

    services_by_category = {
        "Coiffure & soins capillaires": [
            ("Brushing & mise en plis", "Mise en forme et finition coiffure."),
            ("Tresses & tissage", "Tresses, tissages et coiffures protectrices."),
            ("Lissage & brushing", "Lissage, soins lissants et brushing."),
            ("Soin capillaire profond", "Hydratation et réparation intense."),
        ],
        "Soins capillaires premium": [
            ("Diagnostic capillaire premium", "Analyse complète du cuir chevelu."),
            ("Rituel kératine", "Traitement kératine haute performance."),
            ("Traitement réparateur intensif", "Réparation des cheveux abîmés."),
        ],
        "Esthétique & make-up": [
            ("Make-up jour", "Maquillage quotidien lumineux."),
            ("Make-up soirée", "Maquillage événementiel."),
            ("Make-up mariée", "Maquillage longue tenue."),
            ("Soin visage éclat", "Nettoyage et glow immédiat."),
        ],
        "Onglerie": [
            ("Manucure", "Soin complet des mains."),
            ("Pédicure", "Soin complet des pieds."),
            ("Pose gel", "Extensions et renfort gel."),
            ("Nail art", "Design personnalisé des ongles."),
        ],
        "Perruques": [
            ("Vente perruque", "Sélection et conseil personnalisé."),
            ("Pose perruque", "Installation professionnelle."),
            ("Personnalisation perruque", "Ajustements, coupe, styling."),
            ("Entretien perruque", "Nettoyage et remise en état."),
        ],
        "Soins visage & corps": [
            ("Soin visage", "Hydratation et traitement ciblé."),
            ("Gommage & hydratation", "Exfoliation et soin corps."),
            ("Massage relaxant", "Massage bien-être."),
        ],
    }

    for category_name, services in services_by_category.items():
        category = category_map.get(category_name)
        if not category:
            continue
        for service_name, description in services:
            service, created = Service.objects.get_or_create(
                name=service_name,
                defaults={
                    "description": description,
                    "base_price": 0,
                    "is_active": True,
                    "category": category,
                },
            )
            if not created and service.category_id != category.id:
                service.category = category
                if not service.description:
                    service.description = description
                service.save(update_fields=["category", "description", "updated_at"])

    for service in Service.objects.filter(category__isnull=True):
        category = category_map.get(service.name)
        if category:
            service.category = category
            service.save(update_fields=["category", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0003_seed_services"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServiceCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="Catégorie"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Description"),
                ),
                (
                    "image_path",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Visuel (statique)"
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Créée le"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Mis à jour le"),
                ),
            ],
            options={
                "verbose_name": "Catégorie de prestation",
                "verbose_name_plural": "Catégories de prestation",
                "ordering": ["name"],
            },
        ),
        migrations.AddField(
            model_name="service",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="services",
                to="operations.servicecategory",
                verbose_name="Catégorie",
            ),
        ),
        migrations.RunPython(seed_service_categories, migrations.RunPython.noop),
    ]
