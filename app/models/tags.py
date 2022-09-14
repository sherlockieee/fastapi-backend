# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
# )
# from sqlalchemy.orm import relationship
# from app.db import Base


# class Tag(Base):
#     __tablename__ = "tags"
#     id = Column(
#         Integer, primary_key=True, index=True, autoincrement=True, nullable=False
#     )
#     name = Column(String, nullable=False)
#     projects = relationship("Project", secondary="project_tags", back_populates="tags")

#     def __repr__(self):
#         return f"{self.name}"
