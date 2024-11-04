from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "oracle+cx_oracle://system:root@localhost:1521/?service_name=XE"

engine = create_engine(DATABASE_URL)
metadata = MetaData(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class StudentGrade(BaseModel):
    surname: str
    student_group: str
    subject: str
    ticket_number: int
    grade: int
    teacher: str

app = FastAPI()

grades_table = Table("student_grades", metadata, autoload_with=engine)


@app.post("/grades/")
def create_grade(grade: StudentGrade):
    with SessionLocal() as session:
        try:
            grades = grades_table.insert().values(
                surname=grade.surname,
                student_group=grade.student_group,
                subject=grade.subject,
                ticket_number=grade.ticket_number,
                grade=grade.grade,
                teacher=grade.teacher,
            )
            result = session.execute(grades)
            new_grade_id = result.inserted_primary_key[0]
            session.commit()
            return {
                "id": new_grade_id,
                "surname": grade.surname,
                "student_group": grade.student_group,
                "subject": grade.subject,
                "ticket_number": grade.ticket_number,
                "grade": grade.grade,
                "teacher": grade.teacher
            }
        except SQLAlchemyError as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/grades/")
def read_grades():
    with SessionLocal() as session:
        try:
            grades = grades_table.select()
            results = session.execute(grades).fetchall()
            return results
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/grades/{grade_id}")
def read_grade(grade_id: int):
    with SessionLocal() as session:
        try:
            grades = grades_table.select().where(grades_table.c.id == grade_id)
            result = session.execute(grades).first()
            if not result:
                raise HTTPException(status_code=404, detail="Grade not found")
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.put("/grades/{grade_id}")
def update_grade(grade_id: int, updated_grade: StudentGrade):
    with SessionLocal() as session:
        try:
            grades = grades_table.update().where(grades_table.c.id == grade_id).values(
                surname=updated_grade.surname,
                student_group=updated_grade.student_group,
                subject=updated_grade.subject,
                ticket_number=updated_grade.ticket_number,
                grade=updated_grade.grade,
                teacher=updated_grade.teacher,
            )
            session.execute(grades)
            session.commit()
            return {
                "id": grade_id,
                "surname": updated_grade.surname,
                "student_group": updated_grade.student_group,
                "subject": updated_grade.subject,
                "ticket_number": updated_grade.ticket_number,
                "grade": updated_grade.grade,
                "teacher": updated_grade.teacher
            }
        except SQLAlchemyError as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

@app.delete("/grades/{grade_id}")
def delete_grade(grade_id: int):
    with SessionLocal() as session:
        try:
            grades = grades_table.delete().where(grades_table.c.id == grade_id)
            session.execute(grades)
            session.commit()
            return {"message": "Grade deleted successfully!"}
        except SQLAlchemyError as e:
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))
