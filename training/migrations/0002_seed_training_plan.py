from django.db import migrations


def seed_training_plan(apps, schema_editor):
    TrainingProgram = apps.get_model("training", "TrainingProgram")
    TrainingWeek = apps.get_model("training", "TrainingWeek")
    TrainingLesson = apps.get_model("training", "TrainingLesson")
    TrainingSector = apps.get_model("training", "TrainingSector")
    TrainingLessonResource = apps.get_model("training", "TrainingLessonResource")
    TrainingLessonChecklistItem = apps.get_model(
        "training", "TrainingLessonChecklistItem"
    )

    if TrainingProgram.objects.filter(title="Formation Manager Floxy Made").exists():
        return

    sectors_data = [
        (
            "Coiffure",
            "Prestations coiffure, diagnostics capillaires et routines client.",
        ),
        (
            "Perruques",
            "Vente, entretien et accompagnement des clientes perruques.",
        ),
        (
            "Make-up",
            "Maquillage professionnel et valorisation de l'image client.",
        ),
        (
            "Onglerie",
            "Soins des ongles, manucure et prestations associées.",
        ),
        (
            "Soins",
            "Soins visage et corps, protocoles institut.",
        ),
    ]

    sectors = {}
    for name, description in sectors_data:
        sector, _ = TrainingSector.objects.get_or_create(
            name=name, defaults={"description": description}
        )
        sectors[name] = sector

    program = TrainingProgram.objects.create(
        title="Formation Manager Floxy Made",
        description=(
            "Programme intensif de 6 semaines pour structurer l'organisation, "
            "booster la performance commerciale et piloter la stratégie digitale."
        ),
        objective=(
            "Rendre le gestionnaire autonome dans l'organisation, la stratégie digitale, "
            "la gestion opérationnelle et la performance commerciale de Floxy Made."
        ),
        duration_weeks=6,
        target_role="Gestionnaire",
    )
    program.sectors.set(sectors.values())

    sector_names = list(sectors.keys())

    weeks_data = [
        {
            "week_number": 1,
            "title": "Fondations & Organisation",
            "objective": (
                "Comprendre et piloter l'institut même sans expertise technique beauté."
            ),
            "focus": "Services clés, parcours client, organisation quotidienne.",
            "lessons": [
                {
                    "title": "Cartographie des services Floxy Made",
                    "lesson_type": "COURSE",
                    "duration": 45,
                    "objective": (
                        "Comprendre la valeur client des pôles coiffure, perruques, make-up, "
                        "onglerie et soins."
                    ),
                    "key_points": "Identifier les services phares.\nQualifier la valeur client.\nRelier chaque service à un besoin client.",
                    "deliverables": "Tableau des services par secteur.\nArguments de valeur par prestation.",
                    "resources": [
                        {
                            "title": "Fiche services Floxy Made",
                            "resource_type": "TEMPLATE",
                            "description": "Modèle pour lister les services et leurs bénéfices.",
                        },
                        {
                            "title": "Matrice valeur client",
                            "resource_type": "GUIDE",
                            "description": "Guide pour prioriser les services à fort impact.",
                        },
                    ],
                    "checklist": [
                        "Lister tous les services par secteur.",
                        "Qualifier les services à forte marge.",
                    ],
                },
                {
                    "title": "Parcours client standardisé",
                    "lesson_type": "WORKSHOP",
                    "duration": 60,
                    "objective": "Structurer accueil, diagnostic, prestation, paiement et suivi.",
                    "key_points": "Accueil et diagnostic systématique.\nScript prestation + encaissement.\nSuivi post-prestation.",
                    "deliverables": "Parcours client documenté.\nChecklist accueil + diagnostic.\nScript paiement et suivi.",
                    "resources": [
                        {
                            "title": "Checklist parcours client",
                            "resource_type": "CHECKLIST",
                            "description": "Étapes clés à suivre à chaque visite.",
                        },
                        {
                            "title": "Script d'accueil",
                            "resource_type": "TEMPLATE",
                            "description": "Formules d'accueil et de diagnostic.",
                        },
                    ],
                    "checklist": [
                        "Formaliser les étapes du parcours client.",
                        "Valider le script d'accueil avec l'équipe.",
                    ],
                },
                {
                    "title": "Organisation quotidienne & standards",
                    "lesson_type": "COURSE",
                    "duration": 45,
                    "objective": "Mettre en place planning, hygiène, caisse et coordination prestataires.",
                    "key_points": "Planning journalier et hebdomadaire.\nCheck hygiène et sécurité.\nRoutine caisse et reporting.",
                    "deliverables": "Routine ouverture/fermeture.\nPlanning hebdomadaire type.",
                    "resources": [
                        {
                            "title": "Routine quotidienne",
                            "resource_type": "CHECKLIST",
                            "description": "Ouverture, clôture et contrôles essentiels.",
                        },
                        {
                            "title": "Checklist hygiène",
                            "resource_type": "GUIDE",
                            "description": "Points de contrôle par zone de prestation.",
                        },
                    ],
                    "checklist": [
                        "Créer un planning hebdomadaire standard.",
                        "Valider la routine hygiène avec l'équipe.",
                    ],
                },
                {
                    "title": "Scripts d'accueil & checklists opérationnelles",
                    "lesson_type": "CHECKLIST",
                    "duration": 40,
                    "objective": "Déployer scripts et checklists pour garantir la qualité.",
                    "key_points": "Scripts d'accueil et d'upsell.\nChecklist par service.\nStandardisation de la qualité.",
                    "deliverables": "Scripts prêts à l'emploi.\nChecklist par prestation.",
                    "resources": [
                        {
                            "title": "Scripts premium",
                            "resource_type": "TEMPLATE",
                            "description": "Scripts d'accueil, diagnostic et upsell.",
                        }
                    ],
                    "checklist": [
                        "Finaliser un script d'accueil officiel.",
                        "Créer une checklist pour chaque prestation clé.",
                    ],
                },
            ],
        },
        {
            "week_number": 2,
            "title": "CRM & Fidélisation",
            "objective": "Transformer chaque cliente en cliente régulière.",
            "focus": "CRM, suivi post-prestation, fidélité et WhatsApp.",
            "lessons": [
                {
                    "title": "CRM : fiches clientes et segmentation",
                    "lesson_type": "COURSE",
                    "duration": 45,
                    "objective": "Exploiter les fiches clientes et créer des segments utiles.",
                    "key_points": "Collecte des données clés.\nHistorique des prestations.\nSegmentation VIP / régulières / dormantes.",
                    "deliverables": "Modèle de fiche cliente.\nSegments prêts à l'emploi.",
                    "resources": [
                        {
                            "title": "Modèle fiche cliente",
                            "resource_type": "TEMPLATE",
                            "description": "Champs essentiels pour un CRM beauté.",
                        }
                    ],
                    "checklist": [
                        "Définir les segments prioritaires.",
                        "Mettre à jour les fiches clientes existantes.",
                    ],
                },
                {
                    "title": "Suivi post-prestation J+1/J+7/J+21",
                    "lesson_type": "WORKSHOP",
                    "duration": 40,
                    "objective": "Créer un plan de relance automatique après prestation.",
                    "key_points": "Messages J+1 / J+7 / J+21.\nObjectifs de relance.\nRelance par service.",
                    "deliverables": "Séquence de relance prête.\nCalendrier de suivi client.",
                    "resources": [
                        {
                            "title": "Scripts de relance",
                            "resource_type": "TEMPLATE",
                            "description": "Messages WhatsApp adaptés par timing.",
                        }
                    ],
                    "checklist": [
                        "Créer 3 scripts de relance standard.",
                        "Planifier les relances dans le CRM.",
                    ],
                },
                {
                    "title": "Réclamations & récupération",
                    "lesson_type": "COURSE",
                    "duration": 35,
                    "objective": "Gérer les clientes insatisfaites et récupérer la confiance.",
                    "key_points": "Process de traitement.\nScripts d'excuse et compensation.\nSuivi personnalisé.",
                    "deliverables": "Process SAV.\nScript récupération cliente.",
                    "resources": [
                        {
                            "title": "Process SAV",
                            "resource_type": "GUIDE",
                            "description": "Étapes pour résoudre les réclamations rapidement.",
                        }
                    ],
                    "checklist": [
                        "Formaliser une procédure de réclamation.",
                        "Créer un script de récupération client.",
                    ],
                },
                {
                    "title": "Programme fidélité & parrainage",
                    "lesson_type": "WORKSHOP",
                    "duration": 45,
                    "objective": "Mettre en place un programme simple et rentable.",
                    "key_points": "Récompenses simples.\nParrainage aligné sur les services.\nSuivi des gains.",
                    "deliverables": "Plan fidélité.\nRègles de parrainage.",
                    "resources": [
                        {
                            "title": "Template fidélité",
                            "resource_type": "TEMPLATE",
                            "description": "Tableau de suivi des points et récompenses.",
                        }
                    ],
                    "checklist": [
                        "Définir 3 niveaux de récompense.",
                        "Créer un message de parrainage prêt à diffuser.",
                    ],
                },
                {
                    "title": "WhatsApp stratégique",
                    "lesson_type": "WORKSHOP",
                    "duration": 40,
                    "objective": "Utiliser WhatsApp pour relancer, qualifier et vendre.",
                    "key_points": "Étiquettes et segments.\nScripts d'accueil et de relance.\nSuivi des conversations.",
                    "deliverables": "Bibliothèque de scripts WhatsApp.\nListe d'étiquettes CRM.",
                    "resources": [
                        {
                            "title": "Scripts WhatsApp",
                            "resource_type": "TEMPLATE",
                            "description": "Messages courts pour conversions rapides.",
                        }
                    ],
                    "checklist": [
                        "Créer les étiquettes WhatsApp clés.",
                        "Valider les scripts avec l'équipe.",
                    ],
                },
            ],
        },
        {
            "week_number": 3,
            "title": "Contenu & Image de Marque",
            "objective": "Créer du contenu performant sans être expert beauté.",
            "focus": "Identité, piliers éditoriaux, production et calendrier.",
            "lessons": [
                {
                    "title": "Identité et ligne éditoriale",
                    "lesson_type": "COURSE",
                    "duration": 45,
                    "objective": "Définir une image cohérente pour Floxy Made.",
                    "key_points": "Positionnement de marque.\nTon et style visuel.\nMots-clés par secteur.",
                    "deliverables": "Guide identité Floxy Made.\nListe de messages clés.",
                    "resources": [
                        {
                            "title": "Guide identité",
                            "resource_type": "GUIDE",
                            "description": "Document pour aligner le contenu visuel.",
                        }
                    ],
                    "checklist": [
                        "Définir 3 valeurs clés de la marque.",
                        "Lister 5 messages principaux.",
                    ],
                },
                {
                    "title": "Piliers de contenu : transformation, éducation, preuve",
                    "lesson_type": "COURSE",
                    "duration": 40,
                    "objective": "Organiser le contenu autour de 3 piliers efficaces.",
                    "key_points": "Avant/Après.\nConseils beauté.\nAvis et témoignages.",
                    "deliverables": "Checklist des formats par pilier.",
                    "resources": [
                        {
                            "title": "Bibliothèque d'idées",
                            "resource_type": "TEMPLATE",
                            "description": "Tableau d'idées par pilier et secteur.",
                        }
                    ],
                    "checklist": [
                        "Lister 5 idées par pilier.",
                        "Identifier les preuves sociales disponibles.",
                    ],
                },
                {
                    "title": "Création de vidéos courtes (Reels, TikTok)",
                    "lesson_type": "WORKSHOP",
                    "duration": 60,
                    "objective": "Produire des vidéos courtes avec smartphone.",
                    "key_points": "Plan de tournage rapide.\nAngles et lumière.\nMontage et publication.",
                    "deliverables": "Plan de tournage 1 semaine.\nChecklist tournage.",
                    "resources": [
                        {
                            "title": "Checklist Reels",
                            "resource_type": "CHECKLIST",
                            "description": "Avant, pendant et après tournage.",
                        }
                    ],
                    "checklist": [
                        "Créer 3 scripts vidéo courts.",
                        "Planifier 2 tournages par semaine.",
                    ],
                },
                {
                    "title": "Captions orientées conversion",
                    "lesson_type": "WORKSHOP",
                    "duration": 40,
                    "objective": "Rédiger des captions avec hooks et CTA efficaces.",
                    "key_points": "Hooks accrocheurs.\nPreuve et bénéfices.\nCTA clair.",
                    "deliverables": "Bibliothèque de hooks.\nTemplates de captions.",
                    "resources": [
                        {
                            "title": "Templates captions",
                            "resource_type": "TEMPLATE",
                            "description": "Modèles pour chaque type de contenu.",
                        }
                    ],
                    "checklist": [
                        "Créer 10 hooks adaptés aux secteurs.",
                        "Définir un CTA principal.",
                    ],
                },
                {
                    "title": "Planification via calendrier éditorial",
                    "lesson_type": "CHECKLIST",
                    "duration": 35,
                    "objective": "Structurer un calendrier éditorial hebdomadaire.",
                    "key_points": "Rythme de publication.\nRépartition par pilier.\nCoordination équipe.",
                    "deliverables": "Calendrier éditorial 4 semaines.",
                    "resources": [
                        {
                            "title": "Calendrier éditorial",
                            "resource_type": "TEMPLATE",
                            "description": "Planification contenu multi-plateformes.",
                        }
                    ],
                    "checklist": [
                        "Planifier 4 semaines de contenu.",
                        "Valider les contenus phares.",
                    ],
                },
            ],
        },
        {
            "week_number": 4,
            "title": "Réseaux Sociaux & Acquisition",
            "objective": "Développer la notoriété et convertir les abonnés en clientes.",
            "focus": "Optimisation profils, croissance locale, DM et offres.",
            "lessons": [
                {
                    "title": "Optimisation des profils sociaux",
                    "lesson_type": "COURSE",
                    "duration": 45,
                    "objective": "Optimiser Instagram, TikTok, Facebook et WhatsApp.",
                    "key_points": "Bio claire.\nHighlights services.\nLien prise de rendez-vous.",
                    "deliverables": "Checklist optimisation profils.",
                    "resources": [
                        {
                            "title": "Checklist profils",
                            "resource_type": "CHECKLIST",
                            "description": "Points de contrôle par plateforme.",
                        }
                    ],
                    "checklist": [
                        "Mettre à jour la bio sur chaque réseau.",
                        "Créer un highlight par service.",
                    ],
                },
                {
                    "title": "Stratégies de croissance locale",
                    "lesson_type": "WORKSHOP",
                    "duration": 45,
                    "objective": "Utiliser hashtags, géolocalisation et collaborations.",
                    "key_points": "Hashtags locaux.\nPartenariats ciblés.\nInfluence locale.",
                    "deliverables": "Plan de collaborations mensuel.",
                    "resources": [
                        {
                            "title": "Plan collaborations",
                            "resource_type": "TEMPLATE",
                            "description": "Tableau des partenaires locaux.",
                        }
                    ],
                    "checklist": [
                        "Identifier 5 partenaires locaux.",
                        "Définir 3 hashtags par service.",
                    ],
                },
                {
                    "title": "Gestion des DM & prise de rendez-vous",
                    "lesson_type": "WORKSHOP",
                    "duration": 50,
                    "objective": "Qualifier, proposer une offre et planifier un RDV.",
                    "key_points": "Questions de qualification.\nProposition d'offre.\nConversion en RDV.",
                    "deliverables": "Script DM complet.\nChecklist prise de RDV.",
                    "resources": [
                        {
                            "title": "Script DM",
                            "resource_type": "TEMPLATE",
                            "description": "Messages pour convertir les prospects.",
                        }
                    ],
                    "checklist": [
                        "Créer un script DM en 4 étapes.",
                        "Fixer un process de prise de RDV.",
                    ],
                },
                {
                    "title": "Offres hebdomadaires & promotions ciblées",
                    "lesson_type": "CHECKLIST",
                    "duration": 35,
                    "objective": "Mettre en place des offres hebdomadaires rentables.",
                    "key_points": "Offres à durée limitée.\nPromotions par secteur.\nCommunication claire.",
                    "deliverables": "Calendrier promos.\nModèles d'offres.",
                    "resources": [
                        {
                            "title": "Modèles d'offres",
                            "resource_type": "TEMPLATE",
                            "description": "Bundles et promotions prêts à l'emploi.",
                        }
                    ],
                    "checklist": [
                        "Planifier 4 offres hebdomadaires.",
                        "Valider les marges avant diffusion.",
                    ],
                },
            ],
        },
        {
            "week_number": 5,
            "title": "Stratégie Commerciale & Management",
            "objective": "Augmenter le chiffre d'affaires et structurer l'équipe.",
            "focus": "Bundles, upsell, objectifs et management.",
            "lessons": [
                {
                    "title": "Offres packagées & bundles",
                    "lesson_type": "WORKSHOP",
                    "duration": 45,
                    "objective": "Créer des bundles alignés aux services Floxy Made.",
                    "key_points": "Bundles coiffure + soins.\nPack perruques + entretien.\nOffres événementielles.",
                    "deliverables": "Catalogue bundles.\nArgumentaire pack.",
                    "resources": [
                        {
                            "title": "Catalogue bundles",
                            "resource_type": "TEMPLATE",
                            "description": "Tableau des offres packagées.",
                        }
                    ],
                    "checklist": [
                        "Définir 3 bundles prioritaires.",
                        "Valider les prix avec la direction.",
                    ],
                },
                {
                    "title": "Upsell & cross-sell",
                    "lesson_type": "COURSE",
                    "duration": 35,
                    "objective": "Augmenter le panier moyen sans nuire à l'expérience client.",
                    "key_points": "Propositions pertinentes.\nMoments clés.\nScripts d'upsell.",
                    "deliverables": "Liste d'upsell par service.",
                    "resources": [
                        {
                            "title": "Scripts upsell",
                            "resource_type": "TEMPLATE",
                            "description": "Formules adaptées par prestation.",
                        }
                    ],
                    "checklist": [
                        "Créer 5 propositions d'upsell.",
                        "Tester 1 cross-sell par secteur.",
                    ],
                },
                {
                    "title": "Objectifs hebdomadaires & suivi CA",
                    "lesson_type": "WORKSHOP",
                    "duration": 40,
                    "objective": "Fixer des objectifs et suivre le chiffre d'affaires.",
                    "key_points": "Objectifs par service.\nSuivi quotidien.\nReporting hebdomadaire.",
                    "deliverables": "Tableau objectifs.\nRituel de suivi.",
                    "resources": [
                        {
                            "title": "Tableau objectifs",
                            "resource_type": "TEMPLATE",
                            "description": "Suivi des ventes par service.",
                        }
                    ],
                    "checklist": [
                        "Fixer un objectif hebdo par secteur.",
                        "Mettre à jour le suivi chaque jour.",
                    ],
                },
                {
                    "title": "Management des prestataires",
                    "lesson_type": "COURSE",
                    "duration": 45,
                    "objective": "Structurer briefs, contrôle qualité et motivation.",
                    "key_points": "Brief quotidien.\nContrôle qualité.\nRituels de motivation.",
                    "deliverables": "Checklist briefing.\nPlan de motivation.",
                    "resources": [
                        {
                            "title": "Checklist briefing",
                            "resource_type": "CHECKLIST",
                            "description": "Points à couvrir avec chaque prestataire.",
                        }
                    ],
                    "checklist": [
                        "Planifier un briefing hebdomadaire.",
                        "Définir 3 critères qualité.",
                    ],
                },
            ],
        },
        {
            "week_number": 6,
            "title": "Pilotage, Résultats & Autonomie",
            "objective": "Rendre le gestionnaire autonome et orienté résultats.",
            "focus": "KPI, reporting, dashboard et plan 90 jours.",
            "lessons": [
                {
                    "title": "Lecture et analyse des KPI",
                    "lesson_type": "COURSE",
                    "duration": 45,
                    "objective": "Comprendre les indicateurs clés de performance.",
                    "key_points": "KPI ventes.\nKPI rétention.\nKPI marketing.",
                    "deliverables": "Liste KPI prioritaires.\nInterprétation des écarts.",
                    "resources": [
                        {
                            "title": "Dashboard KPI",
                            "resource_type": "GUIDE",
                            "description": "Lecture des indicateurs Floxy Made.",
                        }
                    ],
                    "checklist": [
                        "Définir 5 KPI principaux.",
                        "Analyser les résultats du mois précédent.",
                    ],
                },
                {
                    "title": "Reporting hebdomadaire",
                    "lesson_type": "WORKSHOP",
                    "duration": 40,
                    "objective": "Créer un reporting simple et régulier.",
                    "key_points": "Format 1 page.\nDonnées clés.\nPlan d'action rapide.",
                    "deliverables": "Template reporting.\nRituel hebdomadaire.",
                    "resources": [
                        {
                            "title": "Template reporting",
                            "resource_type": "TEMPLATE",
                            "description": "Synthèse performance semaine.",
                        }
                    ],
                    "checklist": [
                        "Mettre en place un reporting hebdo.",
                        "Partager le reporting avec la direction.",
                    ],
                },
                {
                    "title": "Tableau de bord global",
                    "lesson_type": "COURSE",
                    "duration": 35,
                    "objective": "Exploiter le dashboard CRM, ventes et marketing.",
                    "key_points": "Vue CRM.\nVue ventes.\nVue marketing.",
                    "deliverables": "Checklist dashboard.\nRoutine de consultation.",
                    "resources": [
                        {
                            "title": "Checklist dashboard",
                            "resource_type": "CHECKLIST",
                            "description": "Points à vérifier chaque semaine.",
                        }
                    ],
                    "checklist": [
                        "Définir un rituel d'analyse hebdo.",
                        "Partager un plan d'amélioration.",
                    ],
                },
                {
                    "title": "Plan d'actions 90 jours",
                    "lesson_type": "WORKSHOP",
                    "duration": 60,
                    "objective": "Construire un plan d'actions sur 90 jours.",
                    "key_points": "Priorités commerciales.\nActions marketing.\nSuivi mensuel.",
                    "deliverables": "Plan 90 jours complet.",
                    "resources": [
                        {
                            "title": "Plan 90 jours",
                            "resource_type": "TEMPLATE",
                            "description": "Cadre pour structurer les actions.",
                        }
                    ],
                    "checklist": [
                        "Définir 3 objectifs majeurs.",
                        "Lister 5 actions prioritaires.",
                    ],
                },
                {
                    "title": "Évaluation finale",
                    "lesson_type": "EVALUATION",
                    "duration": 30,
                    "objective": "Valider les compétences et l'autonomie.",
                    "key_points": "Auto-évaluation.\nFeedback direction.\nPlan d'amélioration.",
                    "deliverables": "Score et commentaires finaux.",
                    "resources": [
                        {
                            "title": "Grille d'évaluation",
                            "resource_type": "GUIDE",
                            "description": "Critères de validation du manager.",
                        }
                    ],
                    "checklist": [
                        "Compléter l'évaluation finale.",
                        "Partager les commentaires de clôture.",
                    ],
                },
            ],
        },
    ]

    for week_data in weeks_data:
        week = TrainingWeek.objects.create(
            program=program,
            week_number=week_data["week_number"],
            title=week_data["title"],
            objective=week_data["objective"],
            focus=week_data["focus"],
        )
        for index, lesson_data in enumerate(week_data["lessons"], start=1):
            lesson = TrainingLesson.objects.create(
                week=week,
                title=lesson_data["title"],
                lesson_type=lesson_data.get("lesson_type", "COURSE"),
                duration_minutes=lesson_data.get("duration", 30),
                order=index,
                objective=lesson_data.get("objective", ""),
                key_points=lesson_data.get("key_points", ""),
                deliverables=lesson_data.get("deliverables", ""),
            )
            lesson.sectors.set([sectors[name] for name in sector_names])
            for resource in lesson_data.get("resources", []):
                TrainingLessonResource.objects.create(
                    lesson=lesson,
                    title=resource["title"],
                    resource_type=resource.get("resource_type", "GUIDE"),
                    description=resource.get("description", ""),
                    url=resource.get("url", ""),
                )
            for order, label in enumerate(lesson_data.get("checklist", []), start=1):
                TrainingLessonChecklistItem.objects.create(
                    lesson=lesson,
                    label=label,
                    order=order,
                    is_required=True,
                )


class Migration(migrations.Migration):
    dependencies = [
        ("training", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_training_plan, migrations.RunPython.noop),
    ]
