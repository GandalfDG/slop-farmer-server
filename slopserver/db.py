from collections.abc import Iterable
from datetime import datetime
from urllib.parse import ParseResult
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from slopserver.models import Domain, Path, User, Report

def select_slop(urls: list[ParseResult], engine: Engine) -> Iterable[Domain]:
    query = select(Domain).where(Domain.domain_name.in_(url[1] for url in urls))
    with Session(engine) as session:
        rows = session.scalars(query).all()
        return rows
    
def insert_slop(urls: list[ParseResult], engine: Engine, user: User | None = None):
    domain_dict: dict[str. set[str]] = dict()
    for url in urls:
        if not domain_dict.get(url[1]):
            domain_dict[url[1]] = set()
        
        if url.path:
            domain_dict[url[1]].add(url.path)

    # get existing domains
    query = select(Domain).where(Domain.domain_name.in_(domain_dict.keys()))
    
    existing_dict: dict[str, Domain] = dict()
    with Session(engine) as session:
        existing_domains = session.scalars(query).all()
        for domain in existing_domains:
            existing_dict[domain.domain_name] = domain

        for domain, paths in domain_dict.items():
            if not domain in existing_dict:
                # create a new domain object and paths
                new_domain = Domain(domain_name=domain, paths=list())
                new_domain.paths = [Path(path=path) for path in paths]
                session.add(new_domain)
                if user:
                    for path in new_domain.paths:
                        new_report = Report(path_id=path.id, user_id=user.id)
                        session.add(new_report)
            
            else:
                existing_domain = existing_dict[domain]
                existing_paths = set((path.path for path in existing_domain.paths))
                for path in paths:
                    if not path in existing_paths:
                        new_path = Path(path=path)
                        existing_domain.paths.append(new_path)
                        session.add(new_path)
                        session.flush([new_path])
                        session.refresh(new_path)
                        if user:
                            new_report = Report(
                                path_id=new_path.id, user_id=user.id, timestamp=datetime.now())
                            session.add(new_report)

        session.commit()

def get_user(email, engine):
    query = select(User).where(User.email == email)

    with Session(engine) as session:
        user = session.scalar(query)
        return user

def create_user(email, password_hash, engine):
    user = User(email=email, password_hash=password_hash, email_verified=False)

    with Session(engine) as session:
        session.add(user)
        session.commit()
