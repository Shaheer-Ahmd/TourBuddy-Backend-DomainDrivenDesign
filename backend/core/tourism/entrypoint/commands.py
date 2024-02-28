from core.tourism.domain import model as tsm_mdl
from core.entrypoint.uow import AbstractUnitOfWork
from typing import List
from uuid import uuid4 as uuid

def create_site(
    name:str,
    category:str,
    description:str,
    location: str,
    uow: AbstractUnitOfWork
    )->None:
    
    uow.sites.add(
        tsm_mdl.Site(
            id= str(uuid()),
            name=name,
            category=tsm_mdl.SiteCategory[category],
            description=description,
            location=location
        )   
    )

def add_transportation(
        site_id: str,
        company: str,
        cost: float,
        mode: str,
        uow: AbstractUnitOfWork
    ):

    site = uow.sites.get(site_id)
    site.add_transportation(
        tsm_mdl.Transportation(
            id=str(uuid()),
            company=company,
            mode=tsm_mdl.TransportationMode[mode],
            cost=cost
        )
    )
    uow.sites.add(site)

def add_accomodation(
        site_id: str,
        company: str,
        cost: float,
        category: str,
        uow: AbstractUnitOfWork
    ):

    site = uow.sites.get(site_id)
    site.add_accomodation(
        tsm_mdl.Accomodation(
            id=str(uuid()),
            company=company,
            category=tsm_mdl.AccomodationCategory[category],
            cost=cost
        )
    )
    uow.sites.add(site)
