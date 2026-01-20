from django.db import migrations


def seed_services(apps, schema_editor):
    Service = apps.get_model("operations", "Service")
    services = [
        {
            "name": "Coiffure & soins capillaires",
            "description": "Brushing, tresses, soins profonds et routines capillaires.",
        },
        {
            "name": "Soins capillaires premium",
            "description": "Protocoles premium, traitements réparateurs et diagnostics avancés.",
        },
        {
            "name": "Esthétique & make-up",
            "description": "Maquillage, mise en beauté, soins visage et esthétiques.",
        },
        {
            "name": "Onglerie",
            "description": "Manucure, pédicure, pose et entretien des ongles.",
        },
    ]

    for service in services:
        Service.objects.get_or_create(name=service["name"], defaults=service)


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0002_paymentlink"),
    ]

    operations = [
        migrations.RunPython(seed_services, migrations.RunPython.noop),
    ]
