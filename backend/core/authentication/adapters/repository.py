from abc import ABC, abstractmethod
from typing import Dict
from psycopg2.extras import DictCursor

from core.authentication.domain import model as mdl

class UserAbstractRepository(ABC):
    """User Abstract Repository"""

    @abstractmethod
    def add(self, user: mdl.User):
        pass

    @abstractmethod
    def get(self, user_id: str) -> mdl.User:
        pass

class UserRepository(UserAbstractRepository):
    """User Repository"""

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor(cursor_factory=DictCursor)

    def add(self, user: mdl.User):
        sql = """
            INSERT INTO users (id, name, email, password)
            VALUES (%(id)s, %(name)s, %(email)s, %(password)s)
            on conflict (id) do update set
            name = excluded.name,
            email = excluded.email,
            password = excluded.password
        """

        self.cursor.execute(
            sql,
            {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'password': user.password,
            } 
        )

    def get(self, user_id: str) -> mdl.User:
        sql = """
        SELECT * FROM users WHERE id = %(id)s
        """
        self.cursor.execute(sql, {'id': user_id})
        user = self.cursor.fetchone()
        return mdl.User(
            id=user['id'],
            name=user['name'],
            email=user['email'],
            password=user['password'],
        )
                            