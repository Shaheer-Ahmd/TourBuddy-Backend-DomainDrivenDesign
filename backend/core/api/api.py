from flask import Flask, request
from core.api import utils
from core.authentication.entrypoint import commands as auth_cmd
from core.entrypoint.uow import UnitOfWork
from core.authentication.entrypoint import exceptions as auth_svc_ex
from core.tourism.entrypoint import commands as tsm_cmd
from core.tourism.entrypoint import queries as tsm_qry
from core.comms.entrypoint import commands as comms_cmd
from flask_cors import CORS, cross_origin

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True

cors = CORS(
    app,
    resources={"/*": {"origins": "*"}},
)

@app.errorhandler(utils.CustomException)
def handle_exceptions(e: utils.CustomException):
    payload = {
        "message": e.message,
    }
    return payload, e.status_code


@app.route("/")
@cross_origin(origin="*")
def base():
    """base endpoint"""

    return utils.Response(message="Welcome to the backend", status_code=200).__dict__


@app.route("/create-user", methods=["POST"])
@cross_origin(origin="*")
def create_user():
    """create user endpoint
    - sample req
    {
        "email": "
        "password": ""
        "name": ""
    }
    """
    print(request.content_length)
    req = request.get_json(force=True)
    uow = UnitOfWork()
    try:
        auth_cmd.create_user(
            email=req["email"],
            password=req["password"],
            name=req["name"],
            uow=uow
        )
    except auth_svc_ex.UserAlreadyExists as e:
        uow.close_connection()
        raise utils.CustomException(str(e))

    uow.commit_close_connection()
    return utils.Response(message="User Created", status_code=201).__dict__

@app.route("/verify-password", methods=["POST"])
@cross_origin(origin="*")
def verify_password():
    """verify password endpoint"""
    # print(request.data)
    # print(request.__dict__)
    req = request.get_json(force=True)
    uow = UnitOfWork()
    try:
        auth_cmd.verify_password(
            email=req["email"],
            password=req["password"],
            uow=uow
        )
    except auth_svc_ex.InvalidPassword as e:
        uow.close_connection()
        raise utils.CustomException(str(e))

    uow.close_connection()
    return utils.Response(message="Password Verified", status_code=200).__dict__

@app.route("/create-site", methods=["POST"])
@cross_origin(origins="*")
def add_site():
    """
    sample json
    {
    "name":  site.name,
    "category":  site.category.name,
    "description":  site.description,
    "latitude":  site.location.latitude,
    "longitude":  site.location.longitude,
    }
    """
    req = request.get_json(force=True)
    uow = UnitOfWork()

    tsm_cmd.create_site(
    name= req["name"]  ,
    category= req["category"]  ,
    description= req["description"]  ,
    location= req["location"],
    uow = uow
    )

    uow.commit_close_connection()
    return utils.Response(message="Site Created Successfuly", status_code=200).__dict__

@app.route("/add-transportation", methods = ["POST"])
@cross_origin(origins="*")
def add_transportation():
    """
    sample json
    {
    "site_id":
    "company": str,
    "cost": float,
    "mode": str,
    }
    """
    req = request.get_json(force=True)
    uow = UnitOfWork()
    tsm_cmd.add_transportation(
        site_id=req["site_id"],
        company=req["company"],
        cost=req["cost"],
        mode=req["mode"],
        uow=uow
    )
    uow.commit_close_connection()
    return utils.Response(message="Transportation added Successfuly", status_code=200).__dict__

@app.route("/add-accomodation", methods = ["POST"])
@cross_origin(origins="*")
def add_accomodation():
    """
    sample json
    {
    "site_id":
    "company": str,
    "cost": float,
    "category": str,
    }
    """
    req = request.get_json(force=True)
    uow = UnitOfWork()
    tsm_cmd.add_accomodation(
        site_id=req["site_id"],
        company=req["company"],
        cost=req["cost"],
        category=req["category"],
        uow=uow
    )
    uow.commit_close_connection()
    return utils.Response(message="accomodation added Successfuly", status_code=200).__dict__


@app.route("/send-email", methods=["POST"])
@cross_origin(origins="*")
def send_email():
    comms_cmd.send_email(
        subject="Tour buddy download kro",
        text="SAMPLE TEXT",
        to="faaizumer9@outlook.com",
    )

@app.route("/get-all-sites",methods=["POST"])
@cross_origin(origins="*")
def get_all_sites():
    uow = UnitOfWork()
    sites = tsm_qry.get_all_sites(uow)
    uow.close_connection()

    return utils.Response(
        data=sites,
        message="All Sites returned succesfuly",
        status_code=200
    ).__dict__

@app.route("/loaderio-aa8cb13228091e607265fd28ea979152/",methods=["POST","GET"])
@cross_origin(origins="*")
def test():
    return utils.Response(
        message="heyy",
        status_code=200
    ).__dict__