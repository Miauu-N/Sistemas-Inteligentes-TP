import datetime
from typing import Any
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr
from src.db.database import Base

class User(Base):
    __tablename__ = "users"
    
    # El id será el sub proporcionado por Auth0 (ej. auth0|123456789)
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    email_notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # Relación uno a muchos con los análisis
    analyses: Mapped[list["CVAnalysis"]] = relationship("CVAnalysis", back_populates="user", cascade="all, delete-orphan")


class CVAnalysis(Base):
    __tablename__ = "cv_analyses"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Datos estructurados guardados en formato JSON (compatible con PostgreSQL JSONB genérico)
    parsed_skills: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    job_titles: Mapped[list[str]] = mapped_column(JSON, default=list)
    final_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Indices de las recomendaciones marcadas como completadas
    completed_recommendations: Mapped[list[int] | None] = mapped_column(JSON, default=list, nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    
    # Relación de vuelta al usuario
    user: Mapped["User"] = relationship("User", back_populates="analyses")
