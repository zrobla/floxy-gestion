from django.db import migrations


def sync_service_catalog(apps, schema_editor):
    ServiceCategory = apps.get_model("operations", "ServiceCategory")
    Service = apps.get_model("operations", "Service")

    rename_map = {
        "Coiffure & soins capillaires": "Coiffure & tresses",
        "Soins capillaires premium": "Soins capillaires",
        "Esthétique & make-up": "Maquillage",
        "Perruques": "Mèches & perruques",
        "Soins visage & corps": "Soins & esthétiques",
    }

    for old_name, new_name in rename_map.items():
        category = ServiceCategory.objects.filter(name=old_name).first()
        if category:
            category.name = new_name
            category.is_active = True
            category.save(update_fields=["name", "is_active", "updated_at"])

    categories_data = [
        {
            "name": "Coiffure & tresses",
            "description": "Coiffure, tresses, tissages et mises en plis.",
            "image_path": "prestations/coiffure-tresses.png",
        },
        {
            "name": "Soins capillaires",
            "description": "Soins profonds, diagnostics et traitements capillaires.",
            "image_path": "prestations/soins-capillaires.jpg",
        },
        {
            "name": "Mèches & perruques",
            "description": "Vente, pose et entretien des mèches et perruques.",
            "image_path": "prestations/meches-perruques.png",
        },
        {
            "name": "Onglerie",
            "description": "Manucure, pédicure et pose d'ongles.",
            "image_path": "prestations/onglerie-services.png",
        },
        {
            "name": "Maquillage",
            "description": "Maquillage jour, soirée et événementiel.",
            "image_path": "prestations/maquillage.png",
        },
        {
            "name": "Soins & esthétiques",
            "description": "Soins visage et corps, bien-être et esthétique.",
            "image_path": "prestations/soins-esthetiques.jpg",
        },
    ]

    categories = {}
    for data in categories_data:
        category, _ = ServiceCategory.objects.get_or_create(
            name=data["name"],
            defaults={
                "description": data["description"],
                "image_path": data["image_path"],
                "is_active": True,
            },
        )
        if category.description != data["description"] or category.image_path != data[
            "image_path"
        ]:
            category.description = data["description"]
            category.image_path = data["image_path"]
            category.is_active = True
            category.save(update_fields=["description", "image_path", "is_active", "updated_at"])
        categories[data["name"]] = category

    services_by_category = {
        "Coiffure & tresses": [
            ("Tresses & tissage", "Tresses, tissages et coiffures protectrices."),
            ("Brushing & mise en plis", "Mise en forme et finition coiffure."),
            ("Lissage & brushing", "Lissage, soins lissants et brushing."),
            ("Coiffure événementielle", "Coiffure pour événements et cérémonies."),
        ],
        "Soins capillaires": [
            ("Soin capillaire profond", "Hydratation et réparation intense."),
            ("Diagnostic capillaire", "Analyse complète du cuir chevelu."),
            ("Traitement réparateur intensif", "Réparation des cheveux abîmés."),
            ("Rituel kératine", "Traitement kératine haute performance."),
        ],
        "Mèches & perruques": [
            ("Vente mèches", "Sélection et conseils pour mèches."),
            ("Vente perruque", "Sélection et conseil personnalisé."),
            ("Pose perruque", "Installation professionnelle."),
            ("Personnalisation perruque", "Ajustements, coupe, styling."),
            ("Entretien perruque", "Nettoyage et remise en état."),
        ],
        "Onglerie": [
            ("Manucure", "Soin complet des mains."),
            ("Pédicure", "Soin complet des pieds."),
            ("Pose gel", "Extensions et renfort gel."),
            ("Nail art", "Design personnalisé des ongles."),
        ],
        "Maquillage": [
            ("Make-up jour", "Maquillage quotidien lumineux."),
            ("Make-up soirée", "Maquillage événementiel."),
            ("Make-up mariée", "Maquillage longue tenue."),
            ("Maquillage shooting", "Maquillage photo/vidéo."),
        ],
        "Soins & esthétiques": [
            ("Soin visage éclat", "Nettoyage et glow immédiat."),
            ("Soin visage", "Hydratation et traitement ciblé."),
            ("Gommage & hydratation", "Exfoliation et soin corps."),
            ("Massage relaxant", "Massage bien-être."),
        ],
    }

    for category_name, services in services_by_category.items():
        category = categories.get(category_name)
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
            if service.category_id != category.id:
                service.category = category
                service.save(update_fields=["category", "updated_at"])
            if not service.description:
                service.description = description
                service.save(update_fields=["description", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0005_update_category_images"),
    ]

    operations = [
        migrations.RunPython(sync_service_catalog, migrations.RunPython.noop),
    ]
