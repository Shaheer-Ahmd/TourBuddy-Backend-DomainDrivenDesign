from abc import ABC, abstractmethod
from typing import Dict
from psycopg2.extras import DictCursor

from core.tourism.domain import model as mdl
class SiteAbstractRepository(ABC):
    """User Abstract Repository"""

    @abstractmethod
    def add(self, site: mdl.Site):
        pass

    @abstractmethod
    def get(self, site_id: str) -> mdl.Site:
        pass

class SiteRepository(SiteAbstractRepository):
    """User Repository"""

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor(cursor_factory=DictCursor)

    def add(self, site: mdl.Site):
        sql = """
            insert into sites (id, name, category, description, location)
            VALUES (%(id)s, %(name)s, %(category)s, %(description)s, %(location)s)
            on conflict (id) do update set
            name = excluded.name,
            category = excluded.category,
            description = excluded.description,
            location = excluded.location
        """

        self.cursor.execute(
            sql,
            {
            "id":  site.id,
            "name":  site.name,
            "category":  site.category.name,
            "description":  site.description,
            "location": site.location,
            } 
        )

        for each in site.accomodations:
            sql = """
                insert into accomodations (id, site_id, company, category, cost)
                values (%(id)s, %(site_id)s, %(company)s, %(category)s, %(cost)s)  
                on conflict (id) do update set
                site_id = excluded.site_id, 
                company = excluded.company, 
                category = excluded.category,
                cost = excluded.cost
            """

            self.cursor.execute(
                sql,
                {
                   "id": each.id,
                   "site_id": site.id,
                   "company": each.company,
                   "category": each.category.name,
                   "cost": each.cost, 
                }
            )

        for each in site.transportations:
            sql = """
                insert into transportations (id, site_id, company, cost, mode)
                values (%(id)s, %(site_id)s, %(company)s, %(cost)s, %(mode)s)  
                on conflict (id) do update set
                site_id = excluded.site_id, 
                company = excluded.company, 
                cost = excluded.cost,
                mode = excluded.mode
            """
            self.cursor.execute(
                sql,
                {
                   "id": each.id,
                   "site_id": site.id,
                   "company": each.company,
                   "cost": each.cost,
                   "mode": each.mode.name,
                }
            )

    def get(self, site_id: str) -> mdl.Site:
        sql = """
        SELECT * FROM sites WHERE id = %(id)s
        """
        self.cursor.execute(sql, {'id': site_id})
        site = self.cursor.fetchone()
        
        sql = """
            select * from transportations where site_id = %(site_id)s
            """
        
        self.cursor.execute(sql, {'site_id': site_id})
        transportations_rows = self.cursor.fetchall()
                            
        sql = """
            select * from accomodations where site_id = %(site_id)s
            """
        
        self.cursor.execute(sql, {'site_id': site_id})
        accomodations_rows = self.cursor.fetchall()

        return mdl.Site(
            id= site['id'],
            name= site['name'],
            description= site['description'], 
            category= site['category'], 
            location= site['location'],
            transportations=[
                mdl.Transportation(
                    id = each['id'],
                    company = each['company'],
                    mode = each['mode'],
                    cost = each['cost'],
                )
                for each in transportations_rows
            ],
            accomodations=[
                mdl.Accomodation(
                    id=each['id'],
                    company=each['company'],
                    category=each['category'],
                    cost=each['cost'],
                )
                for each in accomodations_rows
            ] 
        )
        