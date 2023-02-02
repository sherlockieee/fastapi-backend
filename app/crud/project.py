from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload, outerjoin, contains_eager, load_only
from fastapi.encoders import jsonable_encoder

from app import models
import app.schemas.project as schema
from app.schemas.project import ProjectOut


class CRUDProject:
    def get_multi(
        self,
        db: Session,
        filters=[],
        order_by=[],
        skip: int = 0,
        limit: int = 100,
    ) -> List[ProjectOut]:

        subquery = (
            db.query(models.Project)
            .distinct(models.Project.id)
            .outerjoin(models.Transaction)
            .outerjoin(models.User)
            .options(
                # contains_eager(models.Project.backers)
                # .contains_eager(models.Transaction.backer)
                load_only("projects_id")
            )
        )
        if filters:
            subquery = subquery.where(and_(*filters))
        print(subquery.all())
        subquery = subquery.subquery()
        query = db.query(subquery)
        print(query.all())
        if order_by:
            for col in order_by:
                if col not in schema.Project.__fields__.keys():
                    pass
                query = query.order_by(getattr(subquery.c, col).desc())
        print(subquery.c)
        # print(db.query(models.Project).order_by(getattr(models.Project, order_by[0])))
        # print(len(subquery.all()))
        # query = db.query(models.Project).where(models.Project.id._in(subquery))
        # print(len(query.all()))
        # print(str((query).offset(skip).limit(limit)))

        all_projects = query.offset(skip).limit(limit).all()
        print(len(all_projects))
        all_projects = query.all()
        # print(all_projects)
        # print(len(all_projects))
        return all_projects


project = CRUDProject()
