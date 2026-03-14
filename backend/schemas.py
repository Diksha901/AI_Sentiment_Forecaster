from pydantic import BaseModel, EmailStr,field_validator 
import re 

class UserRegister(BaseModel):
    firstname: str
    lastname:str
    email: EmailStr
    password:str 
    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(v) > 72:
            raise ValueError("Password cannot exceed 72 characters")

        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[@#$%^&+=!]", v):
            raise ValueError("Password must contain at least one special character (@,#,$ etc)")

        return v

class UserLogin(BaseModel):
    email: EmailStr
    password:str

class Query(BaseModel):
    query: str