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
        return Path(value)


class DbResult(Base):
    __tablename__ = "results"

    runner = Column(String, primary_key=True)
    ref = Column(PathColumnType, primary_key=True)
    alt = Column(PathColumnType, primary_key=True)
    dist = Column(Float, primary_key=False)

    @staticmethod
    def from_result(result):
        return DbResult(
            runner=result.runner.id,
            ref=result.entry.ref,
            alt=result.entry.alt,
            dist=result.distance)

class Cache:

    def __init__(self, path):
        url = f"sqlite:///{str(path)}"
        engine = create_engine(url, echo=False)
        Base.metadata.create_all(engine)
        self.session = sessionmaker(bind=engine)()

    def save_results(self, results):
        self.session.bulk_save_objects([
            DbResult.from_result(res)
            for res in results
        ])
        self.session.commit()

    def update_results(self, results):
        # this is rather slow
        for res in results:
            self.session.merge(DbResult.from_result(res))
        self.session.commit()

    def get_results(self, runner, pairs):
        rows = (self.session.query(DbResult.runner, DbResult.ref, DbResult.alt, DbResult.dist)
            .filter(DbResult.runner == runner)
            .filter(tuple_(DbResult.ref, DbResult.alt).in_(pairs))
            .all())

        return [(runner, ref, alt, dist) for runner, ref, alt, dist in rows]

    def populate_results(self, results):
        pairs = [(res.entry.ref, res.entry.alt) for res in results]
        runner = results[0].runner.id
        result_idx = { (res.entry.ref, res.entry.alt): res for res in results }

        for _, ref, alt, dist in self.get_results(runner, pairs):
            result_idx[(ref, alt)].distance = dist
