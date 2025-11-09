from typing import Annotated
from sqlmodel import Field, SQLModel, create_engine, Relationship
from pydantic import AfterValidator, Base64Str, BaseModel, EmailStr, Json, SecretStr

from datetime import datetime

from altcha import Payload as AltchaPayload, verify_solution

from urllib.parse import urlparse, ParseResult

from slopserver.settings import settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = SQLModel.metadata
metadata.naming_convention = NAMING_CONVENTION

################################################
#           Database Models
################################################

class Domain(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    domain_name: str = Field(index=True, unique=True)

    paths: list["Path"] = Relationship(back_populates="domain")

class Path(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path: str
    
    domain_id: int | None = Field(foreign_key="domain.id")
    domain: Domain = Relationship(back_populates="paths")
    reports: list["Report"] = Relationship(back_populates="path")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str

    email_verified: bool = Field(default=False)

    reports: list["Report"] = Relationship(back_populates="user")

class Report(SQLModel, table=True):
    path_id: int | None = Field(default=None, primary_key=True, foreign_key="path.id")
    user_id: int | None = Field(default=None, primary_key=True, foreign_key="user.id")
    timestamp: datetime | None = Field(default=datetime.now())

    path: Path = Relationship(back_populates="reports")
    user: User = Relationship(back_populates="reports")

################################################
#           API Models
################################################

def url_validator(urls: list[str]) -> list[ParseResult]:
    parsed_urls = list()
    for url in urls:
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError(f"couldn't parse domain from '{url}'")
            parsed_urls.append(parsed)
        except ValueError as e:
            raise ValueError(f"couldn't parse '{url}' as a URL")
    return parsed_urls

def altcha_validator(altcha_response: AltchaPayload):
    verified = verify_solution(altcha_response, settings.altcha_secret)
    if not verified[0]:
        raise ValueError(f"altcha verification failed: {verified[1]}")
    return None

class SlopReport(BaseModel):
    """Accept reports of one or more slop page URLs"""
    slop_urls: Annotated[list[str], AfterValidator(url_validator)]

class SignupForm(BaseModel):
    email: EmailStr
    password: SecretStr
    altcha: Annotated[str, AfterValidator(altcha_validator)]