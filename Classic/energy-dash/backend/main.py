"""FastAPI: CRUD API для данных дашборда. Данные из CSV, валидация Pydantic, сохранение в файл."""
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data.csv"
_df_cache: pd.DataFrame | None = None


def _load_data() -> pd.DataFrame:
    global _df_cache
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Файл данных не найден: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, low_memory=False)
    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))
    if "timestep" in df.columns:
        df["timestep"] = df["timestep"].astype(str)
    _df_cache = df
    return df


def _save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_PATH, index=False)


def get_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _load_data()
    return _df_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _load_data()
    except Exception as e:
        print(f"Предупреждение при загрузке данных: {e}")
    yield


class RecordCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestep": "2011-11-23 12:00",
                "consumption_eur": 100000,
                "consumption_sib": 25000,
                "price_eur": 900,
                "price_sib": 550,
            }
        }
    )
    timestep: str = Field(...)
    consumption_eur: float = Field(..., ge=0)
    consumption_sib: float = Field(..., ge=0)
    price_eur: float = Field(..., ge=0)
    price_sib: float = Field(..., ge=0)


class RecordResponse(BaseModel):
    id: int
    timestep: str
    consumption_eur: float
    consumption_sib: float
    price_eur: float
    price_sib: float

    class Config:
        from_attributes = True


app = FastAPI(title="Dashboard Data API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/records")
def get_records(limit: int = Query(5000, ge=1, le=100000), offset: int = Query(0, ge=0)):
    """GET /records — получить записи. По умолчанию limit=5000, чтобы не перегружать браузер."""
    try:
        df = get_df().iloc[offset : offset + limit].copy()
        df["id"] = df["id"].astype(int)
        df["timestep"] = df["timestep"].astype(str)
        return df.to_dict(orient="records")
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при чтении данных: {e}")


@app.post("/records", response_model=RecordResponse, status_code=201)
def create_record(record: RecordCreate):
    """POST /records — добавить запись. Валидация Pydantic. Возвращает 201 и запись с id."""
    try:
        df = get_df()
        new_id = int(df["id"].max()) + 1
        new_row = {
            "id": new_id,
            "timestep": record.timestep,
            "consumption_eur": record.consumption_eur,
            "consumption_sib": record.consumption_sib,
            "price_eur": record.price_eur,
            "price_sib": record.price_sib,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        _save_data(df)
        _load_data()
        return RecordResponse(**new_row)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении: {e}")


@app.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: int):
    """DELETE /records/{id} — удалить запись по id. 204 при успехе, 404 если не найдена."""
    try:
        df = get_df()
        if record_id not in df["id"].values:
            raise HTTPException(status_code=404, detail=f"Запись с id={record_id} не найдена")
        df = df[df["id"] != record_id].copy()
        _save_data(df)
        _load_data()
        return None
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}
