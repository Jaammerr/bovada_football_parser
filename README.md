# Основна інформація:

1. Проект створений для отримання даних про футбольні події з сайту https://www.bovada.lv
2. Отримані дані зберігаються та оновлюються в файлі output.json



## Конфігурація (settings.yaml)

```yaml
event_limit: 1000 # Ліміт футбольних подій (per 1 request)
use_proxy: False # Використовувати проксі (True/False)
timeout: 10 # Таймаут (в секундах) між запитами до сайту
```
Якщо використовуються проксі, то необхідно вказати їх в файл proxies.txt в форматі `ip:port:user:pass` (по одній проксі на рядок)


## Встановлення

Для встановлення необхідно виконати наступні команди:

```bash
git clone https://github.com/bovada_football_parser.git
cd bovada_football_parser
pip install -r requirements.txt
python run.py
```


## Загальна Структура JSON файла

Цей документ описує структуру JSON-файлу, який містить інформацію про футбольні події. Даний JSON-файл генерується за допомогою методу `export_events_to_json` і містить дані про футбольні події, їх учасників та ринки.

```json
[
    {
        "path": {
            "id": "string", // Ідентифікатор події
            "link": "string" // Посилання на подію",
            "description": "string", // Назва події
            "type": "string", // Тип події
            "sportCode": "string", // Код виду спорту
        },
        "id": "string",   // Ідентифікатор події
        "link": "string", // Посилання на подію
        "sport": "string", // Вид спорту
        "startTime": "string", // Час початку події
        "live": "boolean",  // Чи є подія в прямому ефірі (так/ні)
        "competitors": [ // Учасники подій
            {
                "_id": "string", // Ідентифікатор команди
                "name": "string", // Назва команди
                "home": "boolean" // Чи є команда господарем (так/ні)
            },
        ],
        "displayGroups": [ // Групи ринків
            {
                "id": "string", // Ідентифікатор групи ринків
                "description": "string", // Назва групи ринків
                "markets": [ // Ринки
                    {
                        "id": "string", // Ідентифікатор ринку
                        "description": "string", // Назва ринку
                        "outcomes": [ // Варіанти ринку
                            {
                                "id": "string", // Ідентифікатор варіанту ринку
                                "description": "string", // Назва варіанту ринку
                                "status": "string", // Статус варіанту ринку
                                "type": "string", // Тип варіанту ринку
                                "price": { // Коефіцієнти варіанту ринку
                                    "id": "string", // Ідентифікатор коефіцієнту
                                    "handicap": "string", // Гандікап коефіцієнту
                                    "american": "string", // Американський коефіцієнт
                                    "decimal": "string", // Десятковий коефіцієнт
                                    "fractional": "string", // Дробовий коефіцієнт
                                    "malay": "string", // Малайзійський коефіцієнт
                                    "indonesian": "string", // Індонезійський коефіцієнт
                                    "hongkong": "string" // Гонконгський коефіцієнт
                                }
                            },
                        ]
                    },
                ]
            },
        ]
    },
    // Інші події
]
