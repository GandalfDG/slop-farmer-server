from collections.abc import Iterable
from urllib.parse import ParseResult
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from slopserver.models import Domain, Path, User

def select_slop(urls: list[ParseResult], engine: Engine) -> Iterable[Domain]:
    query = select(Domain).where(Domain.domain_name.in_(url[1] for url in urls))
    with Session(engine) as session:
        rows = session.scalars(query).all()
        return rows