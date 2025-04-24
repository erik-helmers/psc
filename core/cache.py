from pathlib import Path
from sqlalchemy import String, Float, create_engine, Column, tuple_
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase): pass


class PathColumnType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else None
    def process_result_value(self, value, dialect):
        return Path(str(value))


class DbResult(Base):
    __tablename__ = "results"

    runner = Column(String, primary_key=True)
    ref = Column(PathColumnType, primary_key=True)
    alt = Column(PathColumnType, primary_key=True)
    dist = Column(Float, primary_key=False, nullable=False)
    duration = Column(Float, primary_key=False, nullable=False)

    @staticmethod
    def from_result(result):
        return DbResult(
            runner=result.runner.id,
            ref=result.entry.ref,
            alt=result.entry.alt,
            dist=result.distance,
            duration=result.duration
        )


class Cache:

    def __init__(self, path):
        url = f"sqlite:///{str(path)}"
        engine = create_engine(url, echo=False)
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)


    def save_results(self, results):
        if not results: return

        with self.Session() as session, session.begin():
            session.bulk_save_objects([
                DbResult.from_result(res)
                for res in results
            ])

    def populate_results(self, results):

        ids = { (r.runner.id, r.entry.ref, r.entry.alt): r for r in results }

        with self.Session() as session, session.begin():
            rows = (session.query(DbResult.runner, DbResult.ref, DbResult.alt, DbResult.dist, DbResult.duration)
                .filter(tuple_(DbResult.runner, DbResult.ref, DbResult.alt).in_(list(ids.keys())))
                .all())

        for (runner, ref, alt, dist, duration) in rows:
            res = ids[(runner, ref, alt)]
            res.distance = dist
            res.duration = duration
