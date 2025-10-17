from sqlmodel import Field, SQLModel, create_engine, Relationship

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = SQLModel.metadata
metadata.naming_convention = NAMING_CONVENTION

class Domain(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    domain_name: str = Field(index=True, unique=True)

    paths: list["Path"] = Relationship(back_populates="domain")

class Path(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path: str
    
    domain_id: int = Field(foreign_key="domain.id")
    domain: Domain = Relationship(back_populates="paths")