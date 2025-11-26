from collections.abc import Iterable
from datetime import datetime
from urllib.parse import ParseResult
from sqlalchemy import select, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from slopserver.models import Domain, Path, User, Report

def select_slop(urls: list[ParseResult], engine: Engine) -> Iterable[Domain]:
    query = select(Domain).where(Domain.domain_name.in_(url[1] for url in urls))
    with Session(engine) as session:
        rows = session.scalars(query).all()
        return rows

def top_offenders(engine: Engine, limit: int|None = None) -> Iterable[Domain]:
    query = select(Domain.domain_name, func.count(Path.id)).join(Path).group_by(Domain.id).order_by(func.count(Path.id).desc())
    if limit: query = query.limit(limit)
    with Session(engine) as session:
        top_offenders = session.execute(query).all()
        return top_offenders
    
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
                new_paths = list()
                for path in paths:
                    new_path = Path(path=path)
                    if user:
                        reports = list()
                        reports.append(Report(path=new_path, user=user, timestamp=datetime.now()))
                        new_path.reports = reports
                    new_paths.append(new_path)
                new_domain.paths = new_paths
                session.add(new_domain)
            
            else:
                existing_domain = existing_dict[domain]
                existing_paths = dict({path.path: path for path in existing_domain.paths})
                for path in paths:
                    if not path in existing_paths:
                        new_path = Path(path=path)
                        if user:
                            report_list = list()
                            report_list.append(Report(path=new_path, user=user, timestamp=datetime.now()))
                            new_path.reports = report_list
                        existing_domain.paths.append(new_path)
                        session.add(new_path)

                    else:
                        # domain and path exist, append to the path's reports
                        if user:
                            existing_path = existing_paths.get(path)
                            report_dict = {(report.user.id, report.path.id): report for report in existing_path.reports}
                            existing_report = report_dict.get((user.id, existing_path.id))
                            if existing_report:
                                existing_report.timestamp = datetime.now()
                            else:
                                existing_path.reports.append(Report(path=existing_path, user=user, timestamp=datetime.now()))

        session.commit()

def get_user(email, engine) -> User:
    query = select(User).where(User.email == email)

    with Session(engine) as session:
        user = session.scalar(query)
        return user

def create_user(email, password_hash, engine):
    user = User(email=email, password_hash=password_hash, email_verified=False)

    with Session(engine) as session:
        session.add(user)
        session.commit()

def verify_user_email(user: User, engine):
    with Session(engine) as session:
        session.add(user)
        user.email_verified = True
        session.commit()
