from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    value: Mapped[float] = mapped_column(Float,nullable=True)
    status: Mapped[str] = mapped_column(String(50),default="open")
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)
    contact: Mapped["Contact"] = relationship(back_populates="deals")
    owner: Mapped["User"] = relationship(back_populates="deals")