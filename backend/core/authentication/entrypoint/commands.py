from core.authentication.domain import model as auth_mdl
from core.entrypoint.uow import AbstractUnitOfWork
from core.authentication.entrypoint import queries as auth_qry
from core.authentication.entrypoint import exceptions as auth_svc_ex
from uuid import uuid4 as uuid


def create_user(
    email: str,
    password: str,
    name: str,
    uow: AbstractUnitOfWork,
    )->None:

    if auth_qry.get_user_from_email(email, uow):
        raise auth_svc_ex.UserAlreadyExists("User already exists")

    user = auth_mdl.User(
        id= str(uuid()),
        email=email,
        password=password,
        name=name,
    )

    uow.users.add(user)
    

def verify_password(
    email: str,
    password: str,
    uow: AbstractUnitOfWork,
    )->None:
    user = auth_qry.get_user_from_email(email, uow)
    
    if user.password != password:
        raise auth_svc_ex.InvalidPassword("Invalid Password")