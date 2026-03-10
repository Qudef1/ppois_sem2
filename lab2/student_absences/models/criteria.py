from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Optional

class SearchCriteria(BaseModel):
    group: Optional[str] = Field(default=None, min_length=4, max_length=10)
    surname: Optional[str] = Field(default=None, min_length=1, max_length=50)

    absence_type: Optional[Literal['illness','other','unexcused']] = None

    min_absences: Optional[int] = Field(default=None,ge=0,le=999)
    max_absences: Optional[int] = Field(default=None,ge=0,le=999)

    @field_validator('surname', 'group')
    @classmethod
    def strip_values(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v else v
    
    @model_validator(mode='after')
    def check_range(self):
        if self.min_absences is not None and self.max_absences is not None:
            if self.min_absences > self.max_absences:
                raise ValueError('min_absences должно быть <= max_absences')
        return self
    
    def is_valid(self) -> bool:
        return any([
            self.group,
            self.surname,
            self.absence_type is not None,
            self.min_absences is not None
        ])
    
    def to_dict(self) -> dict:
        return self.model_dump(exclude_none=True)
