from core.authentication.adapters import repository as auth_repo
from core.tourism.adapters import repository as tsm_repo
from abc import ABC, abstractmethod
import psycopg2


class AbstractUnitOfWork(ABC):
    users: auth_repo.UserAbstractRepository
    sites: tsm_repo.SiteAbstractRepository
    
    def __init__(self):
        self.connection: psycopg2.connection
        self.dict_cursor: psycopg2.extras.DictCursor
    
    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, *args):
        pass

    def commit_close_connection(self):
        pass

    def close_connection(self):
        pass

    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
    
class UnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="root",
            host="localhost",
            port="5432"
        )
        self.dict_cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.users = auth_repo.UserRepository(self.connection)
        self.sites = tsm_repo.SiteRepository(self.connection)
       
    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def commit_close_connection(self):
        self.commit()
        self.close_connection()

    def close_connection(self):
        self.connection.close()