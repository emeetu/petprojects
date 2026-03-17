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

## Тестирование

1. **Backend**
   - Откройте http://localhost:8000/docs и проверьте GET `/records`, POST `/records`, DELETE `/records/{id}`.
   - Для POST укажите в теле, например:  
     `timestep`: `"2011-11-23 12:00"`, `consumption_eur`: 100000, `consumption_sib`: 25000, `price_eur`: 900, `price_sib`: 550.
   - Для DELETE укажите существующий `id` (например, 1) — должен вернуться 204; несуществующий id — 404.

2. **Frontend**
   - Убедитесь, что backend запущен на порту 8000.
   - В боковой панели добавьте запись через форму и нажмите «Добавить» — таблица и графики должны обновиться.
   - Введите id существующей записи и нажмите «Удалить» — запись исчезнет; при неверном id отобразится ошибка.

3. **Персистентность**
   - После добавления/удаления записей остановите backend и снова запустите — данные в таблице и в `backend/data.csv` должны сохраниться.

## Деплой

- **Streamlit Cloud**: загрузите репозиторий, укажите корень проекта и команду `streamlit run frontend/app.py`. В настройках задайте переменную окружения `API_BASE_URL` на URL вашего backend (например, Render).
- **Render**: создайте Web Service из `backend/main.py`, команда запуска: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Укажите в Render путь к `data.csv` или включите его в репозиторий в `backend/`. Для Streamlit Cloud в секретах укажите `API_BASE_URL=https://ваш-backend.onrender.com`.

После настройки фронтенд будет обращаться к API по `API_BASE_URL`, таблица и графики будут обновляться при добавлении и удалении записей через UI.
