from pydantic import BaseModel


class ExternalDocs(BaseModel):

    description: str | None
    url: str


class MetadataTag(BaseModel):

    name: str
    description: str | None
    external_docs: ExternalDocs | None

    class Config:

        allow_population_by_field_name = True
        fields = {"external_docs": {"alias": "externalDocs"}}
