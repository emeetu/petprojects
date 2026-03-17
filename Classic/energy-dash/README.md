# Мини-дашборд: энергопотребление и цены (Европа / Сибирь)

Сервис состоит из **Backend (FastAPI)** и **Frontend (Streamlit)**. Данные хранятся в CSV-файле, загружаются и изменяются через API.

## Структура проекта

```
task_02_service/
├── backend/
│   ├── main.py      # FastAPI: эндпоинты GET/POST/DELETE /records
│   └── data.csv     # Данные (время, потребление и цены по регионам)
├── frontend/
│   └── app.py       # Streamlit: таблица, графики, формы добавления/удаления
├── requirements.txt
└── README.md
```

## Требования

- Python 3.10+
- Зависимости из `requirements.txt`

## Установка и запуск

### 1. Виртуальное окружение (рекомендуется)

```bash
cd task_02_service
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Запуск Backend (FastAPI)

Из корня проекта:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- API будет доступен по адресу: **http://localhost:8000**
- Документация: **http://localhost:8000/docs**

### 3. Запуск Frontend (Streamlit)

В **другом** терминале, из корня проекта:

```bash
source venv/bin/activate   # если ещё не активировано
streamlit run frontend/app.py
```

- Дашборд откроется в браузере (обычно http://localhost:8501).

## API

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/records` | Получить все записи (200) |
| POST | `/records` | Добавить запись (201), тело: `timestep`, `consumption_eur`, `consumption_sib`, `price_eur`, `price_sib` |
| DELETE | `/records/{id}` | Удалить запись по **id** (204 при успехе, 404 если не найдена) |
| GET | `/health` | Проверка доступности сервиса |

Валидация входных данных выполняется через Pydantic (числа ≥ 0, обязательные поля). Все изменения сохраняются в `backend/data.csv` и не пропадают при перезапуске.
