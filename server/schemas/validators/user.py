from pydantic import BaseModel, root_validator


class UserSignup(BaseModel):
    username: str
    password: str
    confirm: str

    @root_validator()
    def check_signup(cls, values):
        login, password, confirm_pass = values.get("username"), values.get("password"), values.get("confirm")
        if password and confirm_pass and password != confirm_pass:
            raise ValueError("passwords do not match")
        elif len(password) < 8:
            raise ValueError("password is too short")
        elif len(login) < 6:
            raise ValueError("login is too short")
        return values


class UserLogin(BaseModel):
    username: str
    password: str

    @root_validator
    def check_login(cls, values):
        login, password = values.get("username"), values.get("password")
        if login and password:
            if len(password) < 8:
                raise ValueError("password is too short")
            if len(login) < 6:
                raise ValueError("login is too short")
            return values
