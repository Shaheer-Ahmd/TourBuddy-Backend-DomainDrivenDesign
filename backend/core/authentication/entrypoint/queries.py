from core.authentication.domain import model as mdl
from core.entrypoint.uow import AbstractUnitOfWork

def get_user_from_email(
        email: str,
        uow: AbstractUnitOfWork,
        )->mdl.User:
    
    sql = """
    SELECT * FROM users WHERE email = %(email)s
    """

    uow.dict_cursor.execute(sql, {'email': email})
    user = uow.dict_cursor.fetchone()

    if user is None:
        return None
    
    return mdl.User(
        id=user['id'],
        name=user['name'],
        email=user['email'],
        password=user['password'],
    )
