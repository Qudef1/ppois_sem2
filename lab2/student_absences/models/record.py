from pydantic import BaseModel, Field, field_validator


class StudentRecord(BaseModel):
    id: int = Field(default=0,ge=0)
    full_name: str = Field(..., min_length=4,max_length=100)
    group: str = Field(...,min_length=4,max_length=10)
    absences_illness: int = Field(default=0, ge=0, le=999)
    absences_other: int = Field(default=0, ge=0, le=999)
    absences_unexcused: int = Field(default=0, ge=0, le=999)

    @property
    def total_absences(self) -> int:
        return self.absences_illness + self.absences_other + self.absences_unexcused
    
    @property 
    def surname(self) -> str:
        return self.full_name.split()[0] if self.full_name else ""
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls,v: str):
        v = v.strip()
        if len(v.split()) < 2:
            raise ValueError('ФИО должно содержать как минимум 2 слова')
        return v.title()
    
    @field_validator('group')
    @classmethod
    def validate_group(cls, v: str) -> str:
        return v.strip().upper()
    
    def to_dict(self) -> dict:
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudentRecord':
        return cls.model_validate(data)

