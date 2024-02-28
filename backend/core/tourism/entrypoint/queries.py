from core.tourism.domain import model as tsm_mdl
from core.entrypoint.uow import AbstractUnitOfWork

def get_all_sites(uow:AbstractUnitOfWork):
    sql = """
        select id from sites
    """

    uow.dict_cursor.execute(sql)
    rows = uow.dict_cursor.fetchall()
    return [
        uow.sites.get(each['id'])
        for each in rows
    ]