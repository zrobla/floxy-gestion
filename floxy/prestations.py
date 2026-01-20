from pathlib import Path

from django.conf import settings

from operations.models import Service, ServiceCategory

CATEGORY_IMAGE_MAP = {
    "Coiffure & tresses": "prestations/coiffure-tresses.png",
    "Soins capillaires": "prestations/soins-capillaires.jpg",
    "Mèches & perruques": "prestations/meches-perruques.png",
    "Onglerie": "prestations/onglerie-services.png",
    "Maquillage": "prestations/maquillage.png",
    "Soins & esthétiques": "prestations/soins-esthetiques.jpg",
}


def _resolve_image_path(image_path: str) -> str:
    if not image_path:
        return ""
    static_path = Path(settings.BASE_DIR) / "static" / image_path
    if static_path.exists():
        return image_path
    return ""


def get_prestation_cards():
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related(
        "services"
    )
    cards = []
    for category in categories:
        services = list(category.services.filter(is_active=True).order_by("name"))
        if not services:
            continue
        image = category.image_path or CATEGORY_IMAGE_MAP.get(category.name, "")
        image = _resolve_image_path(image)
        cards.append({"category": category, "services": services, "image": image})
    return cards


def get_prestation_filters():
    services = Service.objects.filter(is_active=True).order_by("name")
    categories = ServiceCategory.objects.filter(is_active=True).order_by("name")
    return {"services": services, "categories": categories}


def get_service_ids_for_category(category_name: str) -> list[int]:
    category = ServiceCategory.objects.filter(name=category_name).first()
    if not category:
        return []
    return list(category.services.values_list("id", flat=True))
