from django.db import migrations


def update_category_images(apps, schema_editor):
    ServiceCategory = apps.get_model("operations", "ServiceCategory")
    image_map = {
        "Coiffure & soins capillaires": "prestations/coiffure-soins-capillaires-1.png",
        "Soins capillaires premium": "prestations/coiffure-soins-capillaires-2.png",
        "Esthétique & make-up": "prestations/makeup.png",
        "Onglerie": "prestations/onglerie-services.png",
        "Perruques": "prestations/perruques.png",
        "Soins visage & corps": "prestations/soins-visage-corps.jpg",
    }

    for name, image_path in image_map.items():
        category = ServiceCategory.objects.filter(name=name).first()
        if not category:
            continue
        if category.image_path != image_path:
            category.image_path = image_path
            category.save(update_fields=["image_path", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0004_service_categories"),
    ]

    operations = [
        migrations.RunPython(update_category_images, migrations.RunPython.noop),
    ]
