from .core import Result, Benchmark
from pathlib import Path
from sqlalchemy import String, Float, create_engine, Column, tuple_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
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

    def __repr__(self):
        return (f"Result(runner='{self.runner}', ref='{self.ref}', "
                f"alt='{self.alt}', dist={self.dist})")

def session_from_path(path: Path):
    url = f"sqlite:///{str(path)}"
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

class Cache:

    def __init__(self, session : Session = None):
        if session is None: session = sessionmaker(bind=create_engine("sqlite://", echo=True))()
        self.session = session

    def save_results(self, results):
        results = list(map(DbResult.from_result, results))
        self.session.bulk_save_objects(results)
        self.session.commit()

    def get_results(self, runner, bench):
        rows = (self.session.query(DbResult.ref, DbResult.alt, DbResult.dist)
            .filter(DbResult.runner == runner)
            .filter(tuple_(DbResult.ref, DbResult.alt).in_(pairs))
            .all())

        output = [Result(runner, bench, ref, alt, dist) for ref, alt, dist in rows]
        remaining = set(bench.pairs()) - set((res.ref, res.alt) for res in output)
        return output, Benchmark(f'partial-{bench.id()}', list(remaining))
