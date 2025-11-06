"""
Классификация источников данных для AI-ассистента.
Определяет в каком JSON файле искать информацию в зависимости от типа запроса.
"""

DATA_SOURCES_CLASSIFICATION = {
    "catalog.json": {
        "description": "Каталог продуктов компании EWA",
        "use_when": [
            "Поиск продукта по названию, категории, свойствам",
            "Вопросы о цене, составе, описании товара",
            "Рекомендации продуктов (для мозга, сна, кожи, похудения и т.д.)",
            "Вопросы типа: 'Что у вас есть для...', 'Какие товары для...', 'Сколько стоит...'"
        ],
        "categories": [
            "БИОХАКИНГ",
            "СПОРТПИТ",
            "БАД",
            "УХОД ЗА ЛИЦОМ",
            "УХОД ЗА ТЕЛОМ",
            "УХОД ЗА ВОЛОСАМИ",
            "HOME (товары для дома)",
            "ЧАЙНАЯ КОЛЛЕКЦИЯ"
        ],
        "fields": ["id", "name", "category", "subcategory", "price_rub", "quantity_volume", "description", "tags"]
    },
    
    "company.json": {
        "description": "Информация о компании EWA PRODUCT",
        "use_when": [
            "Вопросы о компании: история, основатели, география присутствия",
            "Качество продукции: стандарты, сертификаты (ISO, GMP)",
            "Производство: биотехнологии, лаборатории",
            "Контакты компании: телефон, email, соцсети, приложения",
            "Вопросы типа: 'Расскажите о компании', 'Когда основана', 'Где представлена'"
        ],
        "key_info": [
            "Основана в 2022 году",
            "Присутствие: Россия, Беларусь, Казахстан, Узбекистан, Киргизия, Армения",
            "100+ товаров под собственным брендом",
            "Сертификаты: ISO 22000, GMP",
            "Телефон: 8 (800) 100-73-00"
        ]
    },
    
    "business.json": {
        "description": "Бизнес-модель и партнерская программа MLM",
        "use_when": [
            "Вопросы о партнерстве, сотрудничестве, бизнесе с EWA",
            "MLM-программа, привилегии партнеров",
            "Обучение партнеров: EWA Университет, soft skills, нутрициология",
            "Бонусы: автомобили (EWA CAR PROGRAM), путешествия",
            "Инфраструктура: офисы, пункты выдачи",
            "Вопросы типа: 'Как стать партнером', 'Какие условия', 'Что дает партнерство'"
        ],
        "key_info": [
            "250,000+ зарегистрированных партнеров",
            "Без вложений и рисков",
            "Программа EWA CAR - возможность получить автомобиль",
            "Обучение нутрициологии с дипломом"
        ]
    },
    
    "events.json": {
        "description": "Предстоящие события компании",
        "use_when": [
            "Вопросы о мероприятиях, событиях, турах",
            "Даты, города, адреса проведения событий",
            "Спикеры и программа мероприятий",
            "Вопросы типа: 'Какие события будут', 'Где ближайшее мероприятие', 'Когда тур в...'"
        ],
        "events_list": "EWA PRODUCT TOUR по городам России"
    },
    
    "geography.json": {
        "description": "Адреса пунктов выдачи заказов по России",
        "use_when": [
            "Вопросы о адресах, пунктах выдачи, офисах",
            "Где забрать заказ в конкретном городе",
            "Часы работы пунктов выдачи",
            "Телефоны пунктов выдачи",
            "Вопросы типа: 'Где находится офис', 'Адрес в городе X', 'Режим работы'"
        ],
        "cities_count": "30+ городов России"
    }
}


def get_search_strategy(user_query: str) -> dict:
    """
    Определяет стратегию поиска для запроса пользователя.
    
    Args:
        user_query: Текст вопроса пользователя
        
    Returns:
        dict с рекомендуемыми источниками данных и типом ответа
    """
    query_lower = user_query.lower()
    
    strategy = {
        "sources": [],
        "answer_type": "general",  # general, catalog_search, company_info, combined
        "needs_gpt_knowledge": False
    }
    
    # Ключевые слова для каждого источника
    catalog_keywords = [
        "продукт", "товар", "цена", "стоит", "купить", "рекомендуете", "порекомендуйте",
        "для мозга", "для сна", "для кожи", "похудение", "витамин", "бад", "косметика",
        "уход", "мозг", "память", "энергия", "иммунитет", "сон", "стресс"
    ]
    
    company_keywords = [
        "компания", "история", "основана", "сертификат", "качество", "производство",
        "контакт", "телефон", "email", "где представлена", "география компании"
    ]
    
    business_keywords = [
        "партнер", "бизнес", "сотрудничество", "mlm", "заработок", "обучение",
        "стать партнером", "условия", "бонус", "программа", "университет"
    ]
    
    events_keywords = [
        "событие", "мероприятие", "тур", "встреча", "когда будет", "ближайшее событие"
    ]
    
    geography_keywords = [
        "адрес", "где находится", "офис", "пункт выдачи", "забрать заказ",
        "часы работы", "режим работы", "город"
    ]
    
    # Определяем источники
    if any(keyword in query_lower for keyword in catalog_keywords):
        strategy["sources"].append("catalog.json")
        strategy["answer_type"] = "catalog_search"
    
    if any(keyword in query_lower for keyword in company_keywords):
        strategy["sources"].append("company.json")
        strategy["answer_type"] = "company_info"
    
    if any(keyword in query_lower for keyword in business_keywords):
        strategy["sources"].append("business.json")
        strategy["answer_type"] = "company_info"
    
    if any(keyword in query_lower for keyword in events_keywords):
        strategy["sources"].append("events.json")
        strategy["answer_type"] = "company_info"
    
    if any(keyword in query_lower for keyword in geography_keywords):
        strategy["sources"].append("geography.json")
        strategy["answer_type"] = "company_info"
    
    # Общие вопросы о здоровье/витаминах (нужны знания GPT)
    health_keywords = [
        "влияет", "влияние", "дефицит", "организм", "здоровье", "польза",
        "что такое", "зачем нужен", "для чего", "как работает"
    ]
    
    if any(keyword in query_lower for keyword in health_keywords):
        strategy["needs_gpt_knowledge"] = True
        if strategy["sources"]:
            strategy["answer_type"] = "combined"  # Теория + продукты
        else:
            strategy["answer_type"] = "general"
    
    # Если источники не определены - общий вопрос
    if not strategy["sources"]:
        strategy["answer_type"] = "general"
        strategy["needs_gpt_knowledge"] = True
    
    return strategy


# Примеры использования
EXAMPLES = {
    "Что порекомендуете для мозга?": {
        "sources": ["catalog.json"],
        "answer_type": "catalog_search"
    },
    "Как влияет витамин B на организм?": {
        "sources": [],
        "answer_type": "general",
        "needs_gpt_knowledge": True
    },
    "Расскажите о компании": {
        "sources": ["company.json"],
        "answer_type": "company_info"
    },
    "Какие товары у вас есть для восполнения витамина С?": {
        "sources": ["catalog.json"],
        "answer_type": "catalog_search"
    },
    "Как стать партнером?": {
        "sources": ["business.json"],
        "answer_type": "company_info"
    },
    "При дефиците витамина D что может быть и что посоветуете?": {
        "sources": ["catalog.json"],
        "answer_type": "combined",
        "needs_gpt_knowledge": True
    },
    "Где находится офис в Москве?": {
        "sources": ["geography.json"],
        "answer_type": "company_info"
    }
}

