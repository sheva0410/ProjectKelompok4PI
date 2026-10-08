from datetime import datetime
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator


class SubmissionCreate(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def check_url(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 2048:
            raise ValueError("URL terlalu panjang (maks 2048 karakter)")
        p = urlparse(v)
        if p.scheme not in ("http", "https") or not p.hostname:
            raise ValueError("URL harus diawali http:// atau https://")
        try:
            p.port
        except ValueError:
            raise ValueError("Port pada URL tidak valid")
        return v


class AnalysisResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    confidence: float
    explanation: str
    sources: list
    modalitas_dinilai: list[str]
    created_at: datetime


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    normalized_url: str
    title: str | None
    status: str
    error_message: str | None
    created_at: datetime
    result: AnalysisResultOut | None