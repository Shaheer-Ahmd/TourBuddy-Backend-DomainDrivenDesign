import json
import os
from io import BytesIO
from json import dumps
from uuid import uuid4

import pytest
import qrcode
import requests
from core.authentication.entrypoint import view_models as auth_vm
from core.comms.entrypoint import anti_corruption as acl
from core.comms.entrypoint import commands as comms_cmd
from core.comms.entrypoint import exceptions as comms_svc_ex
from core.entrypoint.uow import FakeUnitOfWork, UnitOfWork
from dotenv import load_dotenv
from firebase_admin import messaging


def test_send_notification(mocker):
    uow = FakeUnitOfWork()
    auth_svc = acl.FakeCommunicationService()
    mocker.patch("core.comms.entrypoint.commands._send_notification_firebase", return_value=None)
    comms_cmd.send_notification(
        user_id="1",
        title="Test",
        body="Test body",
        uow=uow,
        comms_svc=auth_svc,
    )


def test_set_fcm_token(seed_verified_auth_user):
    uow = UnitOfWork()
    sender, _ = seed_verified_auth_user(uow)
    fcm_token = "some_fcm_token"
    comms_cmd.set_fcm_token(user_id=sender.id, fcm_token=fcm_token, uow=uow)

    sql = """
        select
            fcm_token
        from
            fcm_tokens
        where 
            user_id = %(user_id)s
    """
    uow.dict_cursor.execute(sql, {"user_id": sender.id})
    fetched_fcm_token = uow.dict_cursor.fetchone()["fcm_token"]

    assert fetched_fcm_token == fcm_token

    uow.close_connection()


def test_send_notification_missing_fcm_token(mocker):
    user_id = str(uuid4())
    uow = UnitOfWork()
    mocker.patch("core.comms.entrypoint.commands._send_notification_firebase", return_value=None)

    with pytest.raises(comms_svc_ex.FcmTokenNotFound):
        comms_cmd.send_notification(
            user_id=user_id,
            title="Test",
            body="Test body",
            uow=uow,
            comms_svc=acl.CommunicationService(),
        )

    uow.close_connection()


# def test_send_notification_real():
#     msg = messaging.Message(
#         notification=messaging.Notification(title="Notif title", body="Notif body"),
#         token="dPNxmPAdRVajGDbZH7x2om:APA91bG1bGo4DFbz2vaucekhtjzEpgaFMyCwt0Q-xGIbXFapjn5Uwd9HeVHNBhytnY0a6MQl-Gje4ntOnbyrNljsfFnQYBdAx9PqgNu0hSiXl0f7E2_gzWonnMbWKTjCTz7oL6KDlcJ0",
#     )

#     messaging.send(msg)


# load_dotenv()
# from core.comms.entrypoint import commands


# def test_send_email():
#     commands.send_email(
#         subject="Pytest",
#         text="Woah noice content, someone ran pytest and the email got into your inbox successfully!",
#         to="23100011@lums.edu.pk",
#     )


# def test_send_image_email():
#     data = {"qr_id": str(uuid4()), "event_id": str(uuid4())}
#     data_str = str(data)

#     qr = qrcode.QRCode(
#         version=1,
#         box_size=10,
#         border=4,
#     )

#     qr.add_data(data_str)
#     qr.make(fit=True)

#     buffer = BytesIO()
#     img = qr.make_image(fill_color="black", back_color="white")
#     img.save(buffer)
#     qr_code_bytes = buffer.getvalue()
#     buffer.close()

#     comms_cmd.send_image_email(
#         subject="Test image email",
#         text="Woho, sending an email with some images O.o!",
#         to="23100011@lums.edu.pk",
#         image_bytes=qr_code_bytes,
#     )


# def test_send_image_email_tedx():
#     data = {"qr_id": str(uuid4()), "event_id": str(uuid4())}
#     data_str = str(data)

#     qr = qrcode.QRCode(
#         version=1,
#         box_size=10,
#         border=4,
#     )

#     qr.add_data(data_str)
#     qr.make(fit=True)

#     buffer = BytesIO()
#     img = qr.make_image(fill_color="black", back_color="white")
#     img.save(buffer)
#     qr_code_bytes = buffer.getvalue()
#     buffer.close()

#     html = f"""
#     <html>
#         <head>
#             <title>TedX Confirmation Email</title>
#         </head>
#         <body>
#             <h1>Hi Abdur Rehman Shamsi!</h1>

#             <p>We're excited to confirm your registration for TedX</p>

#             <p>Please show this QR code at the venue to mark your attendance:</p>
#             <img src="cid:qr_code_image">

#             <h2>Event Details</h2>

#             <ul>
#                 <li>Date: 18th November, 2023</li>
#                 <li>Time: 9:00 AM</li>
#                 <li>Location: LUMS SDSB B3</li>
#             </ul>

#             <p>Please review the event details carefully and make any necessary arrangements.</p>

#             <p>We look forward to seeing you at the event!</p>

#             <p>Sincerely,</p>
#             <p>CardPay Team</p>
#         </body>
#     </html>
#     """

#     comms_cmd.send_image_email(
#         subject="Successful Registration Completed",
#         html=html,
#         to="huzaifa@cardpay.com.pk",
#         image_bytes=qr_code_bytes,
#     )


"""
https://lifetimesms.com/otp?
api_token=xxxx&
api_secret=xxxx&
to=92xxxxxxxxxx&
from=Brand&
event_id=Approved_id&
data={"name":"Mr Anderson","ledger":"-R520,78","date":"28 February 2015"}
"""

# def test_send_otp_sms():
#     url = "https://lifetimesms.com/otp"
#     parameters = {
#         "api_token": os.environ.get("SMS_API_TOKEN"),
#         "api_secret": os.environ.get("SMS_API_SECRET"),
#         "to": "923333462677",
#         "from": "CardPay",
#         "event_id": "366",
#         "data": dumps({
#             "name": "Suleman Mahmood",
#             "code": "7236",
#         })
#     }

#     response = requests.post(url, data=parameters)
#     print(response.content)


# def test_send_sms():
#     url = "https://lifetimesms.com/otp"
#     headers = {"Content-Type": "application/json"}
#     parameters = {
#         "api_token": os.environ.get("SMS_API_TOKEN"),
#         "api_secret": os.environ.get("SMS_API_SECRET"),
#         "to": "923333462677",
#         "from": "CardPay",
#         "event_id": "xx",
#         "data": {
#             "name": "",
#             "ledger": "",
#             "date": "",
#         },
#     }

#     response = requests.post(
#         url,
#         data=parameters,
#         headers=headers,
#         timeout=30,
#         verify=False,
#     )

#     #

#     url = "https://lifetimesms.com/otp"

#     data = {"key": "value", "code": "123456", "variable": "value of variable"}

#     data = json.dumps(data)

#     parameters = {
#         "api_token": os.environ.get("SMS_API_TOKEN"),
#         "api_secret": os.environ.get("SMS_API_SECRET"),
#         "to": "923333462677",
#         "event_id": "some event id",
#         "data": data,
#     }

#     headers = {"Content-Type": "application/x-www-form-urlencoded"}

#     response = requests.post(
#         url, data=parameters, headers=headers, timeout=30, verify=False
#     )

#     print(response.text)


# def test_send_sms():
#     url = "https://lifetimesms.com/json"
#     parameters = {
#         "api_token": os.environ.get("SMS_API_TOKEN"),
#         "api_secret": os.environ.get("SMS_API_SECRET"),
#         "to": "923333462677",
#         "from": "CardPay",
#         "message": "heyo",
#     }

#     response = requests.post(url, data=parameters)
#     print(response.content)


@pytest.mark.skip
def test_send_personalized_emails():
    """
    This test is skipped since it sends emails to real users.
    Only use this for manual testing.
    """
    auth_acl = acl.FakeAuthenticationService()
    auth_acl.set_all_emails(
        [
            auth_vm.EmailInfoDTO(email="dla@whipplewishes.com", full_name=f"Email {_}")
            for _ in range(300)
        ]
        + [
            auth_vm.EmailInfoDTO(email="lisovalik@miamimarci.com", full_name=f"Email {_}")
            for _ in range(300)
        ]
        + [
            auth_vm.EmailInfoDTO(email="sweetypieerahh@auwake.com", full_name=f"Email {_}")
            for _ in range(300)
        ]
    )

    email_body_template = """<p><strong>Bold <em>Italic <u>Underlined </u></em></strong>Dekhlo brother chal raha hai sahi se</p><p><img src="data:image/png;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAARCALQAtADASIAAhEBAxEB/8QAHgABAAIDAQEBAQEAAAAAAAAAAAEJAggKBwMFBAb/xABjEAEAAQAFBwQJCg0TAwMFAAAAAQIDBAURBgcICSExQThylbEZM1Z1srTB0dISExc0UVdhcXSzFBgyNTZUY2RzdpKTxBUWJyg3REZHUlViZWZnkabT1OQiQoUjwsNDRYGho//EABwBAQABBQEBAAAAAAAAAAAAAAADAQIFBgcIBP/EAFQRAQABAQMDBRkOBQUBAQAAAAABAgMEEQUGBxIXMYLCExYhNTZBUVJUZHFyc4GDkZKjsbPBw9HS4xQjJDI0QkNEYaGisuHiFSIzYvAlJjdTk2PT/9oADAMBAAIRAxEAPwC1MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHPll59nOUUz/O1r+epNxzRzT36q7Wje289Rh83VY44/3U4bD4b7ffccUzqccftwdBo51ojjKW760PPne/3vh/jP9n3/AKOigc65vNaHnzvftF0ZXx+Z9/6Oigc7MRgGtBz53v2i7+Lf2ff+jomHO1vZRGCutBz73v2i6MqY/M+/9HRGOdvek1oOfe9+0XRlLH5v3/o6IxzuxHGUbzWg59737RfGUMfm/f8Ao6IxzvRGCVdZ/n3vftFfd39v3/o6IBzvsojBXWe59737Rf7s/t+90PDnhDWe59737RdF6+x0PDniiMU7/iNZ7n3vftF0XjHjOhwc8iYhXWd59737RdFvjxnQ0OeXfshMRgazvPve/aLotMeM6GRzzisaHcfrve/aLoqxdDA554jFluNZzn3vftF2LoWHPSmIxNZzn3vftF2DoVHPXM8IIjBXWb59737RfFDoUHPYtK1WMfsAZQz/AGxtXiVia7nRo632snzf/dOrwmIw1Gp2ft1c+Aqo1MYtyRWLrSLwvCyZ7cmKuyW60VFClkrVTNGrraVGJn6LtO3CJaY/qleMfv8AtP52l5315D0X1ZayfZX/AN1anVxjhqMcODydXHgXU2OqjHF0EDn3/VK8ZjCbfacPc9dped84tFpn98Vn5csvrNzx773v96SLtjx3QYOfSbRX4YTXVkxOzCaU7XziOMqxoanj33vftF0XTHjug6lSo0YmlSmIiN8y+f0TZvtir/Lhz7JXRoZ59737RdFz/u+50F0KyrrMfW6yjSw34TiyaD6qD6w5yPld2eBaH9GtYrKyryYzeet1lKjjb7wxwnD/AOnUtDnM/DObfdi24+Gr1P8AZq/i6rrfG+37EG8Pfd5Yt8Bz8fRNp+2Kz8uUxabTwtFZ+XLe9Zmebe9+0fXGTv7vu/V0DDn7+ibRH74rPy5Pom0/bFZ+XJrMzzb3v2i6Mm4/O+79XQIOfv6JtP2xWflymLRaN82is/LlXWYnm3vftF0ZLx+d936ugMc/n0TaZ/fFZ+XKfom0R++Kz8uVdZeebe9+0XRknH5/3fq6Ahz/AH0Taftis/LljTrK2tw9crKVLDd6qccDWXnm3vftF0ZH/v8Au/V0Bjn8iMBXWX5+717Rd/Bf7/u/V0Bjn8TEYq6y3P3evaL/AOB//T7v1dAQ5/nQBG5oueuZW+fvD3/eu9dV83U4anU/3VY46r7Nh8F/uHuLU/zY448bDYw+37UgNFY8AAAAAAAAAAAAAAAAAAAAAAAAAAc+OXO3LfKGZ/nW1/PUnQc58ct5xy0v+f60tXztJ2PRF/VvfQo8NTCZZ2KOv5H4oG921hYg3sojAiMASRAneb2URguSRBEYI3m9KqSIExHGSI4yjeJaaTeyiMCIwSJIgBlEYLohJEERgAJYgTEYkRinf8SqSIN/xJExHGVy+IIj3SZxJnFMRgJYgiMEgrEJIgIjEiMWW5VJEG4ExGKqSIIjFMzwgmeEERgrEJYgiMEgrspIgWl6rKP2vuUE/wBsrX4lYlWkRitN1WkYaPt//jja/ErE51pS4nqunp8KlpGFLwTWofu3ZL/irVeN2lpe3R1qEfs25Lz/AGVqvG7S0viMWbzG4nbp0vllNYx/LBEYstkQbIhERxltkQ+iIIjjKRKqSIDeb2URgqkiFimqh2XFnIj77uzwLQ+utb+xjN58vvD5upfHVRfWPOR8ruvwLQ++tb25MZu/l94fN1LhE/8AJfX8y+CI+Gf5yFcu9lEYERgO8sxECQiOMi+IIjjJtk2yy3LksQbgTvEkQb2URgRGAqviAExGK5LEERilIJYpF/8AG6FAERxlf/G6PicL00/Uey+bYDL/ANH1/IkBwtroAAAAAAAAAAAAAAAAAAAAAAAAAA58MtPsxv6f6ztXztJ0Hue/LHblffnfK0/O0nY9EX9W99CjdMNleMYo6/kfj72URgRGA7aw8QJ3m9lEYLkkQRGCN5vSqkiBMRxkiOMo3iWmk3sojAiMEiSIAZRGC6ISRBEYACWIExGJEYp3/EqkiDf8SRMRxlcviCI4yTOJM4piMBLEERgkFYhJEBEYkRiy3KpIg3AmIxVSRBEYpmeEEzwgiMFYhLEERgkFdlJEBEYkRiy3CSINy03VbR+18v34csLX4nY1WS07VcRho9338OV9r8TsbnWlLgZvVdPT5VttH8jwPWoRjnsyW/Far8btLTDZEN0dafsz05LT/Zer8btDS2I4yzeYvE7dOl8sp7CMaIIjjKRLbX0RAbzeyiMFUkQRGAG9VJELE9VD9ZM5Hyq6/AtD+jWs/Yxm8+X3h83Uv59VFGFy5yPlV1+BaX31rP2MZvPl94fN1Lg9X/JnX8yx2Hw3/OQrnSERxl3lmYgiOMm2TbLLcuSxBuBO8SRBvZRGBEYCq+IATEYrksQRGLIBLEYBEcZIjjJM4iSIxJnFf/R+pj4lAURgv9o/Ux8Thmmr6j2XzbXs4Po+v5EgOFNbAAAAAAAAAAAAAAAAAAAAAAAAAAHPfld9ll9z7t42n52k6EHPflZtyqvmf6wtHzlJ2TRF/UvfQo3TEZV2KOv5H5Kd5vZRGDtzExBEYI3m9KqSKRMRxkiOMo3iWmk3sojAiMEiSIAZRGC6ISRBEYACWIExGJEYp3/EqkiDf8SRMRxlcviCI4yTOJM4piMBLEERgkFYhJEBEYkRiy3KpIg3AmIxVSRBEYpmeEEzwgiMFYhLEERgkFdlJEBEYkRiy3CSINwJiMVdhJEERitP1XUYaPV9fDlda/FLGqy2RC07Vdx+15viZ45W2zxWyOc6U+J6rp6fKsvEe9vA9afH7NGSs/2XoeN2hpa3T1p/7s2Sn4sUPG69pazeYnE7dOl8sprD+nAbzeyiMG3PqiCIwAiMVUkQb2URgYYCqWIWI6qP6zZyflV1+BaX9GtZ+xjN58vvD5upfz6qP6z5yflN1eDaX9GtZw/Wxm8x+37w+bqXBqv+TOv5li8Ph/8AnIVzxHGTbJtllud7ZyINwJ3iSIN7KIwIjAVXxACYjFcliCIxZAJYjAIjjJEcZJnESRGJM4sojAiMBXYSRAv8ofUUfihQGv8AKH1FH4ocL01fUey+ba5nFGG8tt5GQDhTWQAAAAAAAAAAAAAAAAAAAAAAAAABz3ZVbcqL4+G32j5yk6EXPdlP9kt7T7tur/nKTsuiH+pe+hRu2KypGMU9fyPzYjBG83pduYumkTEcZIjjKN4liDeyiMCIwSJIgBZdoy6C2j5nOzE5IZe5W3He1de98WOnXWqsqb0rauhSpRXU6MYUY2RsowweX84bpm1d6bzfIqmmqdTGpiJnHCZ48xyE9lZTaThCtOIwFvfY29Fnucvvpmu852NvRZ7nL76ZrvO1PXVyHytp3Mes+mLrXCoRMRit67G3os9zl99M13nT2NzRa3frcvvpmu85rq5D5W07mPWXxd6lQu/4kreexuaLXc5ffTNd5zsbmi13OX30zXedXXWyFytp3Mesv3hUqHiOMkzit4nVu6Lc/wAHL76ZrvOdjd0W4/g5ffTNd5zXWyFytp3MesuiymFRERglbv2N7Rb7nb76ZrvOdje0W+5y++ma7zq662QuVtO5j1l8USqIIjFbv2N7Rb7nL76ZrvOdjf0XO5y++ma7zq66+QuVtO5j1l+CorcLduxv6Lnc5ffTNd5zsb+i53OX30zXec118hcradzHrLo4CoqIxTM8IW6djg0Xe52++mK7znY4NFzudvvpiu86uuvkLlbTuY9ZfFUQqLiMErc+xw6Lvc7ffTFd509jh0Xe5y+umK7zmuxkLlbTuY9ZfFpCosiMVunY4dF3ucvrpiu852OLRd7nL66YrvOrrsZC5W07mPWXxa0wqN3C3LscWi73O310xXec7HFou9zt9dMV3nNdnIPK2ncx6y6LehUdEYstkQtw7HHovdzt9dMV3nOxx6L2/wDW7fXTFd51Y0s5B5W07mPWXxeKFR0RxlajqvuTxe342WzxWyP9B2OPRe7nb66YrvO9lzP5mchcxmS1dkdm+sdps1219trLwp0LRaaVfSmup0KFClPqqW3DCro7Go575+5LzhyVNyukVxXqqZ/miIjCOhVK22t6LSjUwr+1qH7suSk/2Yo+NV7Sze3U1qEfsx5J/izR8ar2lsRg6jmJxO3TpfLL7btHvcERgBEYtufVTSRGLLcbhVLECQiOMi+IWIaqP6z5yflN1eDaX9GtZjHJjN58vvD5upfz6qOcbozlfKbq8G0t1MtM22QGcapstny9yNufKCqsNKlTs1C8bJQr4qaVKIilNGKUThMxEY4e4845fyvZ5Bz8tMoWtM1U0TGMRs8GyiOP0WFtrSLC+TXPG9Ch3cLuPpYtHb3ksi+hqj0T6WLR295LIvoao9Ft+vHk7mavt0+l9kZWs+VlSRvZRGC7X6WLR295PIvoao9E+li0dveTyM6HqPRNePJ3M1fbp9K6Mr2fKypKF2v0sWjt7yeRnQ9R6J9LFo7e8nkZ0PUeirryZO5mr7dPpXxlmyj5sqS4jFktm0mNH7Mfk1mCy6v7J/NNkrd142G566us1qs111VXW1NOMMKVGlFHGJ+GFTLes1c6bDOu7V3mws5oimrU4ThyInjdFlLleqb5TNdMYYBEcZIjjJM4tpffEYkziyiMCIwFdhJEAJiMVYhJEERiv7q/qKPxQoGX81f1FH4ocL01fUey+ba1nJ9FtvIyAcJauAAAAAAAAAAAAAAAAAAAAAAAAAAOe3KT/qyivWfv2v8AnJdCTnsyinHKC85+/K7w5dm0QfHvnQo3bGZSjHU9fyPz0xHGSI4yje7ax0Qb2URgRGCRJEAMojBdEJIgiMF1uhHyVs3ne6s8YrVKS63Qj5K2bzvdWeMVrlelvhTY9Uj8tT7bpGFUvcQHn594AAAAAAAAAAAAAAAAAAAAAAACsjWnx+zDknP9mo8armlbdXWn/uv5Jfi1HjVc0qiMXrXMPicunS+WWduse9UkRiy3G4bc+uIEhEcZF8QRHGTbJtlluXJYhYdqo9l05yvlF1eDaW/DQfVSfWrOV8ourwbU34eUdI/FPetp4ulreUPlNXW8EADSHxgAAAPJNLTk2ZxO8df5FLURxldNpZ8m3OJ3jr/IpZmcXonQ3wrvHVNzDacgxjY1dHyEziyiMCIwHYNhsEQAmIxViEkQRGLIFUkQL+av6ij8UKB4jFfxV9ro82HCtNf1Hsvm2sZzRhvLbeRkA4S1UAAAAAAAAAAAAAAAAAAAAAAAAAAc9l/7b9vKZ+267w5dCbnqv2ZpX3eHyqt8OXZ9EHx750LPdsdf4x1PX8j+HeyiMCIwS7Y+CIDeb2URguiEkQRGAAliBddoSclbN53urPGK1SlEYrrdCTkr5vO91Z4xWuV6W+FNj1SPy1Pru0fzS9wAefn2AAAAAAAAAAAAAAAAAAAAAAAAKytafGOd7JH8W/0quaV7m6utO/dcyRn+zn6VXNKnrTMPicunS7qWwXSPeaRIRHGW3vriCI4ybZNssty5LEG4E7xJELDNVH9a85Xyi6fBtTfloNqpNl2Zyo+73T4Nqb8vKOkfinvW08XS1jKPymrreCABpD4gAAAHkmlnybM4neOv8ilyIwXSaWfJtzid46/yKW3onQ3wrvHVNzDa834xsauj5AExGLsMQ2KIIjFkCqSIExGJEYkzwhXZSRBM8IX8Vfa6PNhQREYL9qrtVDmw4Vpr+o9l821bOiMN5bbcswHCGpgAAAAAAAAAAAAAAAAAAAAAAAAADnrvn682+fdtNb4cuhRz1XxON7W2fvis8KXaNEHxr52Pdvgv3zeu/kN5vZRGDtsQ+KIIjAASxAmIxIjFO/4lUkQb/iXWaEvJXzed7qzxitUqLq9CXkr5vO91Z4xWuV6W+FNj1SPy1PpsI4L3AB59fUAAAAAAAAAAAAAAAAAAAAAAAArM1p37reSP4ufpNa0qbra0/wDdZyQ/F2fGa1pTEcZetcwuJy6dLP5pbHc495pIjjJtk2yy3NwfbEG4E7xJEG9lEYERgKr4hYXqpfrbnL/D3T4Nqb8NBtVL9bs5f4e6fBtTfl5R0kcU962ni6WrZS+VVdbwQANHfCAAAA8l0s+TbnE7x1/kUtrpNLPk25xO8df5FLkRi9FaGuFd46puYbdm7GNhX0fJBEYsgdhbHECYjEiMSZ4QrspIgmeEJiMCIwSqliMBfrVdqoc2FBS/Wq7VQ5sOE6a9i49l821TOqMIsdtuWYDhDUAAAAAAAAAAAAAAAAAAAAAAAAAABz03rtvS2fKKzwpdCznqvH642qfdr6fhS7Tof+NfOx7t8V8+b1380RgA7Y+WIExGJEYp3/EqkiDf8SRMRxlckiCI4yuq0JeSvm873VnjFapVmcV1WhLyV83ne6s8YrXKdLnCmx6pH5an0WUYS9wAefU4AAAADxHSW0qslNGSjk7Synyava9/1xza4qPoClVx619D+s+q9V6ulG/16jhh7kvruFwvOU7xTdbpRqrSrHCI4+ETM7P2RJEYvbhpD2VbNT72mVn5dm9NPZVs1Hva5Wfl2b02x74ecfMtXbp9K/UVchu6NIp1q2anCfU5tMrJnhjWWb03z7Kvmx97DKj8/Z/SV3ws45+q1dun0m86uQ3hGj3ZV82PvYZUfn7P6SY1q2bKf4sMqPz9n9I3wc4+Zau3T6Vd418hvANH51qubKP4sMp/z9n9I7Krmy97DKf8/Z/SV3wc4+Zau3T6Vd4WnIbwDR/squbL3sMp/wA/Z/ST2VXNl72GU/5+z+kb4OcnMtXbp9Kvue05Dd8aQdlUzZT/ABYZT/n7P6R2VPNl72GU/wCfs/pG+DnJzLV26fSr7mteVbvjSHsqebL3scp/z9n9IjWpZsp/ixyn/P2f0jfAzk5lq7dPpV9y23Kt3hpF2VLNl72OU/5+z+kdlRzZ+9jlP+fs/pG+BnJzLV26fSr7kt+VbujSLsqObP3scp/z9n9I7Kjmywx9jHKf8/Z/SN8DOTmSrt0+lX3Hb8q8s1p0fssZITPc9PjNa0n2y980wNIvJ/SSyyuPKXJ7J+8LpqbquybDWVdtp0KVKnSmtpU/VR6iZjDClg8F3PSGZ1yvGTsh3e63qnU10xMTHI4M8hnrpZ1UWNNNWybgTvbK+yIN7KIwIjAVXxACYhclppWE6qX63Zy/w10+Dam/LQbVTe0M5f4a6PBtbfl5P0kcU962ni6GpZU4F7r63ggAaO+AAAAB5LpZcm3OH3jr/IpeXQ6WXJtzh946/wAil56K0NcK7x1Tcw3DNyPeK+j5IExGJEYkzwh2LZbLEEzwhMRgRGCVUsQAyiMFUsQRGC/Op7VQ5sdSgxfnU9poc2OpwjTXsXHsvm2o52RhvHbblmA4Q04AAAAAAAAAAAAAAAAAAAAAAAAAAc9N4e37T+Gp+FLoWc9FtnG2V8+7W0uuXadD/wAa+dj3b5L1Gw+CYjEiMU7/AInbXzxBv+JImI4yuSRBEcZJnEmcUxGAkiCIwXU6EvJYzed7qzxitUrrqdCbksZvO91Z4xWuU6XOFNj1SPy1JqI4L28B59SgAAACvjW0dqzW86++qxLB1fGto7Vmt5199Vibvo54prtt/F1r7P40K8yIxIjFluepn1xBuBMRiu2EkQRGLLZBsgiOMkQliCI4yCVUkQG83sojBVJEERgBEYqpKaSIxZbINkG/eqliDfvSERxkXxBEcZNsm2WW5cliDcCd4kiDeyiMCIwFV8QAmIXJaaSISJEsRgsH1U3tHOZ+GujwbW35aDaqb2jnM/C3R1Wtvy8n6SeKi9bTxdDTsq/K6+t4IAGjseAAAA8l0suTdnD7x1/kUvxGK6HSx5N2cPvHX+RS9M8Iei9DXCu8dU3MNzzajGwr6PkgmeEJiMCIwS7E2eIAZRGCqWIIjAAiMV8QL86ntNXzY6lBsRivxqO01fNjqcK027Fx7L5tqGd2xY7bcvoA4M0wAAAAAAAAAAAAAAAAAAAAAAAAAAc89q22qun7pS63Qw557Rtr6zn0ut2rQ9s3zse7fNeIxwfPf8SRMRxl25DEERxkmcSZxTEYCSIIjBIKxCSIF1OhNyWM3ne6s8YrVK0Riup0JuSxm973VnjFa5Vpd4U2PVI/LUlh7eA89rgAAABXxrZ4xqs1vOvvqsSwdXzrZu1ZredffVYm76OeKa7bfxdaSy+PCvTcCYjF6o2H3RBEYstkGyCI4yRCWIIjjIJVSRAbzeyiMFUkQRGAERiqkppIjFlsg2Qb96qWIN+9IRHGRfEERxk2ybZZblyWINwJ3iSIN7KIwIjAVXxACYhclppIhIkSxGARHGSI4yTOIkiMVg+qnnGxZzPwt0dVrb8tBtVNGFjzmfhbo6rW35eUNJPFRetp4uhpeVvllfW8EADRmOAAAAeS6WXJuzh946/yKYIjBdBpY8m7OH3jr/IpgejNDPCq8dU3MN1zYj3ivo+SAGURg7E2qIIjAAiMV8QJiMSIxTM4LkkQTOC/Co7RV8yOpQfEcZX4VHaKvmR1OEabdi49l8207PCMIsdtuX0AcGaUAAAAAAAAAAAAAAAAAAAAAAAAAAOeat21tOf6U9boZc81LbTpTO7GXbNDv13sfnEFtGOCIjjJM4kzimIwdsRxBEYJBWISRARGJEYslUsQLp9Cfks5ve91Z4xWqWF0+hPyWc3ve6s8YrXKdLvCmx6pH5al2GD28B57AAAABXzrZu1ZredffVYlgyvrWyxjVZredffVYm76OOKa7bfxdaWx+PCvSIxZbINkERxl6oiGSiCI4yCVUkQG83sojBVJEERgBEYqpKaSIxZbINkG/eqliDfvSERxkXxBEcZNsm2WW5cliDcCd4kiDeyiMCIwFV8QAmIXJaaSISJEsRgERxkiOMkziJIjEmcWURgRGArsJIhYLqp/amc38Jc/Va2/LQXVT+1c5v4S5+q2N+nk/STxUXraeLoaTljgX2vreCABozGAAAAPJtLHk3Zw+8df5FMC5/Sx5N+cPvHX+RTFEYPRmhnhVeOqbmG8ZrR8Hr6byQRGADsURi2qIExGJEYpmcFySIJnAiOMkRxlIliBffUdoq+ZHUoQX32ftFXzI6nCNNuxcey+baXnjsWG23L6AODNIAAAAAAAAAAAAAAAAAAAAAAAAAAHPLMzMuhmlOFGZ+BzzxGDtmh3672PziK0jHAiMEg7bELYgIjEiMWSqWIATEYqr4giMV02hPyWc3ve6s8YrVLUzwhdLoT7NFnN73urPGK1yjS7wpseqR+WpdVGEPbwHntYAAAAK+tbLsqs1vOvr9CWCq+tbJ2rNbzr7/Qm76OOKe67fxdaa7/1IV7RHGQS9UsrEBvN7KIwVSRBEYARGKqSmkiMWWyDZD/WZtM1OcDPDf8AXZMZuMnad83nZ7JTt1ZZ6FfVVM0aijToUKVP1VbSo0dlKsoRhjjt3b0dtb2V2s5tbaqKaY2ZmcIjozPAhJwKYxl/k9+9L3n6RTSt96S09KWH/XI0FNK3jmktPSlh/wBdid+XIvNll/6UelSLay5aO3DwaI4ybZe8/SK6Vs/xSWnpSw/67L6RXSsj+KS09KWH/XXb8uRebLL/ANKPSki3seXjtw8G3D3n6RbSs96S09KWH/XPpFtKz3pLT0pYf9dXflyLzZZf+lHpSReLHl47cPB97KIwe8RoLaVcfxSWnpSw/wCufSL6VfvS2npSw/65vy5F5ssv/Sj0r4vFjy8duHg494+kX0q/eltPSlh/1yNBfSr45pbT0pYf9Zdvy5E5ssv/AEo9KSLzYcvHbh4REJf6bOHm2y2zU5R0sks4FxU7pvahU0LRSs1Kuqq2Yq6ePqaXqqulSo7cJ4v80y9jbWd4s4tbGqKqZ4MTE4xMcmJjZfXRhVGqpnGAiOMkRxkmcUiWIxJnFlEYERgK7CSIATEYqxCSIWB6qf2rnN/CXP1Wxv00G1VHtbObz7n6rY35eT9JXFRetp4uho2Wfl1fW8EADRWLAAAAeTaWHJvzh946/wAimJc7pYcm/OH3jr/IpiejdDMf6VeOqbmG9ZqR8Hr6byQJiMSIxTM4OxtsiCZwIjjJEcZSJYgAiMVYhJEERivvs/teq5lHqUJbl9tn9r1XMo9ThGm7YuPZfNtJzzjDeG23L6AOCtGAAAAAAAAAAAAAAAAAAAAAAAAAAY1myrpz/Rlz0uhSv2VFZP8AQnqc9btuh2PlvY/OLKoxCIxIjFk7arEAJiMVV8QRGKZnhBM8IIjBWISxBEYLptCjks5ve91Z4xWqWl0uhRyWc3ve6s8YrXKNL3Cmx6pH5ai0jgPbgHnpCAAAAK+9bJ2rNbzr66rEsEV962TtWa7nX11WJvGjjinuu38XWnu39WFexvN7KIweqWYiCIwAiMVUlNJEYstkGyDfvVSxBv3tv9V9yhL5/FK1+N2RqC2+1X3KDvmf7JWvxuyNWz34nr30kor1HvFXQWlAPIrXAAAAAAAAFUGse5S1r7zWDwaTV6I4y2i1jsftlrXP9TWDwaTV2Zxew8zuEFz6nT4G9XCMbtZ9CCZxZRGBEYDZth98QAmIxViEkQRGLIFUkQsB1VHtfOdz7m6rY36aC6qjtGc7n3N1Wxv08naS+Ki9bTxdDQ8tfLrTreCABorFAAAAPJtLDk35w+8df5FMcRiud0r+ThnC7x1/kUxzOD0boY4VXjqm5pb7mnGN2r6byQTOBEcZIjjKXY23RABEYqxCSIIjFluNyVUkQL67N7WquZR6lCkRivrs3taq5lHqcH03bFx7L5to+esYRYbbcvqA4K0QAAAAAAAAAAAAAAAAAAAAAAAAAB8rTss1bP8AQpdTnsiMXQtWUIraulV0pmIp0Zozh8LTnsWGj53Y5w+kLD/tHTNHedOT82ovPu6ZjV6jDCMfi6rHwwpMKsRad2LDR87sc4fSFh/2h2LDR87sc4fSFh/2jpWujm/y1fcyrHAVZRGKZnhC0zsWOj73Y5wukLF/tCNVjo+R/DDOF0hYv9orGlHN7lq+5lJExCrOIwStM7Flo+92GcLpCxf7Q7Flo+92GcLpCxf7RXXSze5avuZXxXSqzXS6FHJZze97qzxiteTdiy0fe7DOF0hYv9o2dzXZurkzS5A3Nm6yctVutN23HU0qiz1ttp0KdfSozTpU8adKhRo0ZnGlO6jDQ9IOeOS848n2d3uM1TVTXqpxjDgamqPKttK4qjCH+qAcjRAAAACvvWx7arNbzr66rEsEV+a2LtWa7nX11WJvGjjinuu38XW+i6/1o/zjK94jACIxeqmbppIjFlsg2Qb96qWIN+9IRHGRfEERxlt9qv5x0hL5/FK1+N2RqDtlt/qv4/bBXz+KVr8bsjV89+J299JKO9x7xV0FpIDyI1gAAAAAAABVDrHuUtao/qaweDSavxGDaHWO8pW195rB4NJq89i5ncT9z6nT4G/ZPj4LZ9CAExGLZYh98QRGLIFUkQJiMSIxJnhCuykiFgGqpw9ZznYfyrm6rY36aC6qmMKnOdzrm6ra36eTdJfFTetp4uhoGXOBf7TrflgAaKxIAAADyfSv5OGcLvHX+RTHEcZXnZzMhrHnMyBv3IG8LdXWOzX7Y6djrbRU0YpU6ujS40YnZM/G1ToarzNlEz65nJynpfFVWeP/AGy7Lo2zyyTm3cLawyhXNNVVeMYUzPA1MRxug23N7K11yfYV0W84TM47EzxoVvCyehqv80sYeuZwcrqXu+pmzR/8UvvQ1YWZeI/9TLnLWlOP/bX2SP8A4JdE11s2o+kq7iWwb8+To+dPalWjEYstyzShqxsxUY+uZYZeUvcwttjj9Fl/RQ1ZuYGjh6rKPLmnh/KvCy7f8LMsnS1m3Hzq+4n0q79WTo489pWIRGK0Khq1dHyhh6q9csqeE/8AdeVRt/wqIfehq39HehjjXZV0/jvOhs/wqlk6Xc3Y/wCzuf1XRnbk6OW7X6quNkL6bN7WquZR6mslDVz6ONGcaVmykp/HenmoNnqFGKFCjQo7qMREOW6Sc8MnZ1xdouGq971eOqjD42oww4M8rLWM5MsXbKu8vc+P8uqxxjDZw9DIBy5qwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAr81sXas13Ovr9CWBq/NbDGNVmu519dVibxo34p7rt/F1vpuf9an/OMr3iMWWyDZBv3vVbPxBv3pCI4yL4giOMm2TbLLcuSxBubfasDlB3z+KVr8bsjUFt9qwOUHfP4pWvxuyNVz34nb30kob5HwevoLSAHkRqoAAAAAAACqLWO8pW195rD4NJq82h1jvKVtfeaweDSavxGL2LmbxP3PqdPgdCydHwWz6EERiyBsz74gTEYkRiTPCFdlJEEzwhMRgRGCVUsQ3+1VXas53Oub9Nb9NBdVT2vOfzrl/TW/TybpM4qb1tPF0OeZe4YWnW/LAA0RiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGNOnRq6FKnTnCjRiZmfga609YRomUJwo5y6+nzbivDy1LYa1+1K78HS6nPjEYOj5gZo3HOmLxN9qqjeeow1MxHxtVjjjTPIjkL6adUuAp6xHRToxjRy6t9P4IuS2eWrfCnrGdFmhj6nKu9qeH8m5rRt/wAaMKhx0eNE2QuXtO6p9RJFlC3GnrItF+hOFG/L9p7N9G563y4P56esq0ZqP1Nsylp/FdM7P8aapaIxZbl8aKMgxx7Tuo9VfFjStgrNZlo2UMfU1eVtPD+TdVDb/jWw+FPWd6OVCf8ApuzLSns/7bsqPLXwqmTEYpI0VZAjZ1fdfovi70rUaetD0eaOHqcnMu6eP8m7rLs/xtMNnM3eXV0ZzMh7ly+uGz2uou6/bJQtlmq7XQo0K6jQpbopxRpUqMT8VKVCmyF2OiPyaM3PeKo8rQ9IOZ2TM27jZW9xirVVV4TjOPAwmUdtZU2dMTD10ByZ8wAAAAr91sPas10/0r6/QlgSv3Ww9qzXc6+uqxN40b8U912/i631XL+vT1/Ar4370hEcZeq2wxBEcZNsm2WW5cliDcCd4kiDe2+1YMYaQV8/ila/G7I1DiMG3mrB5QV8/ila/G7I1bPfidvfST5EF9j4PX0Fo4DyG1IAAAAAAABVHrG4x0lbX3msHg0msDaDWN8pS195rD4NJq+9jZm8T9z6nT4HRcmx8Es+hAmIxIjEmeENm2WQiCZ4QmIwIjBKqWIAZRGCqWIb+aqrZQznx8Ny/prfpoLqq/qc5/x3L+mt+nkzSZxU3raeLoc4y/wxtOt+WABojDgAAAPw8t8sblzfZJXrlrlFTrqN2XNZqVqtU1NX6unFXR34UeMtfuyK6N32/lD0VS9J6LpXcnHOF3kr/Ipnde0dZj5MzpuNreL9NWqpr1MamYjgYRPInkttzeyJdsqWNVpb44xOHAn7I+xan2RXRu+38oeiqXpHZFdG6f3/AJQ9FUvSVWRGLLZDoWtBm9ybTuo9VsUZoZP5NXbj0LUeyKaN/wBv5Q9FUvSOyKaN/wBv5Q9FUvSVXb94rrP5vcm07qPVXxmdk7k1duPQtS7Ipo3/AG/lD0VS9I7Ino3/AG/lD0VS9JVd8MpiMdsms/m9ybTuo9VdGZmTp49Xbj0LUOyJ6N8/v/KHoql6TZWxWupvCxWe32eZmqtNVQrqGMYT6mlETGMfFKhtevkvGGTN0R94Wf5ui5lpIzNydmpRdqrhNXvk146qYn4upwwwiOTLWM58iXbJFNlN3x/mxxxnHYw+z7X6gDlbUgAAAAAAAAAAAAAAAAAAAAAAAAAHxtftSu/B0upz5Og21+1K78HS6nPk7fob2L72PdprKMcQiMSIxZbnbn0RBuBMRiu2EkQRGLLZBsgiOMkQliCI4yuy0SOTTm57xVHlUmrstEjk05ue8Nn8rkmmDhZd+qbmXz3v4sPXAHnt8AAAAAr91sHas13OvrqsSwJX9rYMPWs12P8AKvrqsTeNG/FPddv4ut9dx+UU9fwSr4iOMm2TbLLc9WtliDcCd4kiDeyiMCIwFV8QNvNWDygr5/FK1+N2RqG291YPKBvmf7JWvxuyNWz44nb30k+RDfowu1fQWjAPITTgAAAAAAAFUmsb5Slq7zWHwaTWCIxbQaxqMdJS1d5rD4NJq/M8IexszeDm/c+p0+B0jJkfBLPoQTPCExGBEYJbOyUQAyiMFUsQRGABEYr4hv5qqt2c/wD8L+mt+mgmqq3Z0P8Awv6a37eTdJvFVetp4uhzbODhjadb8sADQ2GAAAAeT6V3Jxzhd5K/yKZ4jFcxpXcnHOF3krvIpp2Q9H6F+FV46puaXR8y4+C2nTeSDZBv3m/eOy7DdYjAT8MnwymIx2yqviMSIx2ykFUsQL2cmdmTd1R941HzdFRNvXtZORhk9dce5YqjwIcJ03f07l0bTcNBz9jCiw225fogPP7nIAAAAAAAAAAAAAAAAAAAAAAAAAD5Wr2rXfg6XU58YjF0HWr2rXfg6XU589zuGhvYvvY92+iwjHE3AmIxdv2H1RBEYstkGyCI4yRCWIIjjIJVSRAuw0R+TTm57xVHlUn712OiRs0ac3PeKo8rkemHhZd+qbmXy3yMKI6L1wB57Y4AAAAV/a2CMarNdzr66rEsBV/a1/tWa/nX1+hN50bcU912/i632ZP+U09fwSr63Ane9WNoiDeyiMCIwFV8QAmIXJaaSIev6MOf/wClwzg2zLv9aX64fou6a66/oX6P+hPU+rrams9c9X63WY4es4ep9T/3Y47MJ8hS+S/XGwyld67peqdVRXGExjMYx0YmJ7Urq7Km1omiuMYlYB2Vz+4X/NP/AAyNa3x9gX/NP/DV/wARxkmcWoa2ma/Mv47T13yxki6T8z759KwDsrn9wv8Amn/hp7K1/cL/AJp/4jQCIwFdbTNfmX8dp66+Mj3OfmffPpb/APZWv7hf80/8Q7K1/cL/AJp/4jQBMQrraZr8y/jtPXXxkW5cp98+lv8AxrWcf4hv80/8Q7Kx/cN/mj/iNAg1s81uZfx2nrr4yJceU++fS397Kx/cN/mj/iJjWr4/xDf5o/4jQKIxJnhCutnmtP1X8dp66+Mh3H/r++r0vUNI7Pb9MBnKrc4UZM/qD67Y6iyfQf0b9FYetxMeq9c9bob8d3qdnuvMIjAiMEtzuVzsMn3ei63anU0URERGMzhEbHBnGe3LLWNjTY0RZ0RhEbADKIwfU+mIIjAAiMV8QJiMSIxTM4LkkQ361Vn8Z8d5f01v00E1Ve/Ofj/Uv6a37eS9JvFVetp4uhzPOLhladb8sADQ2FAAAAeT6V3Jxzhd5K/yKad+9cvpW8nLOF3kr/IpoekNC3Cq8dU3NLpOZPyS06byQJ+GT4ZTEY7ZdlbtEYkRjtlIKpYgN5vZRGCqSIIjBezk9suC7I+86nwIUTr2bgjC4rtj70qfAhwjTf8A07j0bTcOf5/RhTd9tuX94Dz+5uAAAAAAAAAAAAAAAAAAAAAAAAAA+Vq9rV34Ol1OfN0GWn2tW8yl1OfSIxdw0NbF97H5x9V2jHEiMWWyDZBEcZdviH2xBEcZBKqSIDeb2URgr9kJIgiMF1+iTyas3PeKo8qlBdfok8mrNz3iqPK5Hph4WXfqm5l8l/jCiOi9cAeemLAAAAFf+tf7Vmv519dViWAK/wDWvbarNfzr66rE3nRtxT3Xb+Lrfbk75TT1/BKvreyiMCIwHq1tUQAmIXJaaSISJEsRgERxkiOMkziL4jEmcWURgRGArsJYgBMRxlWISRBEcWQKpIgTEYkRiTPCFdlJEEzwhMRgRGCVUsQAyiMFUsQRGABEYr4gTEYkRimZwXJIgmcCI4yRHGUiWIb8aqz6rOf8Vy/prftoJqrfq853xXL+mt+3kvSbxVXraeLocvzj4Z2u1/LAA0NhAAAAHlGlbycs4XeSv8imn4ZXLaVvJyzg95K/yKaojHbL0hoW4VXjqm5h0vMiMbpadN5IIjHbKQdmbzEBvN7KIwVSRBEYJBVJEC9q4owuS74+9arwIUSxC9u5YwuawR961XgQ4Npv+JcejabhzzSBwKbvtty/tAcAc2AAAAAAAAAAAAAAAAAAAAAAAAAAfK0+1q3mUupz7bIdBNp9rVvMpdTn2iOMu46Gti+9j84+y6RjiRHGQS7e++IDeb2URgr9kJIgiMAIjFVLTSRGK6/RJ5NWbrvFUeVSlshdbok8mrN13iqPK5Fph4WXfqm5l8WUYwojovXAHnpiAAAABoBrXe1Zr+dfXVYm/wC0A1rvas1/OvrqsTedG3FRddv4ut92TflVPX8Eq+wTEPV7bqaSISJEsRgERxkiOMkziL4jEmcWURgRGArsJYgBMRxlWISRBEcZZAqkiBMRiRGJM8IV2UkQTPCExGBEYJVSxADKIwVSxBEYAERiviBMRiRGKZnBckiCZwIjjJEcZSJYgAiMVYhJEN+NVb2zOd8VzfprftoJqrtlZnN5tzfpjft5L0ncVV62ni6HLc5eGdrtfywANCYIAAAB5RpWcnLOD3kr/IprXKaVnJyzg95K/wAimt6R0LcKrx1Tcw6dmNGN0tOm8kBhiRGLKIwdmb1EERgkFUkQEQRDISRAvaufZdFhj72qvBhRKvbumMLrscfe9X4MODacPiXHo2m4c60hRhTd9vuX9YDgDmgAAAAAAAAAAAAAAAAAAAAAAAAAD5Wn2vW8yl1OfZ0FWj2vW8yl1OfZ3HQzsX3sfnH3XPjhvN7KIwdw+yGRiCIwAiMVUtNJEYstkGyDfvVSRBv3rrtErk1Zuu8VR5VKS63RK5NWbrvFZ/K5Dph4WXfqm5l8GUo97p6L1sB56YYAAAAaAa13tWa/nX11WJv+0B1rkY1WbDnX11WJvOjXiouu38XW+/Jfyujr+CVfcQkS9XtyiMAiOMkRxkxmRfEYkziyiMCIwFdhLEAJiOMqxCSIIjjLIFUkQJiMSIxJnhCuykiCZ4QmIwIjBKqWIAZRGCqWIIjAAiMV8QJiMSIxTM4LkkQTOBEcZIjjKRLEAERirEJIgiMWW43JVSRDfXVX9tzm825uu2N+2gmqv7dnM5tzddsb9vJWk7iqvW08XQ5VnNGGVLXa/lgAaEwIAAADyjSs5OWcHvJX+RTXEYrlNKzk55we8ld5FNu56R0K8Krx1Tcw6jmJHwO16byQbkg7O3uICIIhkJIgBMRxlWISRBEcZXt3ZGF22SPuFX4MKJNsyvdu6MLvssfcaHgw4Lpx+Lcey+bc40iRhF22+5f0AOAOZAAAAAAAAAAAAAAAAAAAAAAAAAAPnaO0VnMpdTn23ugm0dorOZPU5+IjB3HQzsX3sfnGQuMfG6xEYARGLuLKU0kRiy2QbIN+9VJEG/ekPhk2V8QRHGV1uiVt0a83XeKo8qlLfK63RK5NebrvFUeVyLTFwru/VNzL4MqRhZ09F62A88sGAAAANAda32rNhzr66rE3+aA61vtWbDnX11WJvOjXiouu38XWyGSvldHX8Eq/SI4yRHGTe9Xt0iMTbLKIwIjAV2EsQAmI4yrEJIgiOMv3Mj8i8qsv7+qcmMjLjtV73raaNOnVWSzUfVVlOjQozSpTEfBETP8A+H4rY/V88qPJz5HePitYxmW79XkzJtvfbOImqzoqqiJ2JmImeCsvFpNhY12scaJntP8AH0NEPSWrIxo5nb/jnVdCOuk+1HQ60mqURS9h++sPhmqj/wB65YcHnTJlbjWFn+L1mr78l45Sn7/SpvjQx0n6WEUc0N67fdr7PH/yPrQ0KNKKlPqYzR3hj8NsssddauLFuvJlnjWFl2q/XV35bzGxRT9/pU9UNCDSmp44ZpbXGHu3jYo6659aGgvpVU49VRzUV0fHe9gjrr1wAtnTJlvjWNl2q/XV3573Hzae1PpVC0dA7StmImM1U7fdvu7Y/SH2jQI0qpmInNpVR8M33d/+ut0Fs6Y8uz9FZdzX/wDob9N85WntT6VSFHQD0pqU4Tm/stH4ZvqxeStfahq/NKGlj6rImwUMPdvmybf8KxbSLZ0xZf8A+uy7mr11d+m+8rT2p9Kpyjq+NJ2aOM5J3XR+Cb4s/kpPpR1eWkzMRM5PXNEz7t71Oz/9rXxbOmDOCfmWXc1eub9V+5FPan0qp6Ors0lZmIm6bhox7s3tQ8z6UNXNpI0pwmx5OUfhm9Y8lFaoLNd/OHkWfcz6xv13/kU9qfSqwoauDSMpfVRkvQ+O9KXkq33oatzSImjjNpyTo/BN51nkqlpApOl3OKf+vuZ9ZXfsyh/b2v1VeRq1tIScMbzyNjH3byr9n/8AB9qOrQz/AMzhN/5EUY92bxtP+3WeiydLmcc8ejuP1N+zKP8Ab2msGhXoyZf6OtZlhSy4vK4rXF/0bBFl/Uy0Vtb6n1j6I9X6v1yqoYY+u0cMMd07uOz4NEyzle85dvteUL3hvSvDHCMI4ERTHA6EQwd8vdpfreq8W3xpw+6MPIAMY+UAAAB5TpV8nPOD3kr/ACKbVyWlXyc84PeSv8im16S0K8Kbx1Tc0up5hR8Dtem8kBEEQydmb7EAJiOMqxCSIIjjJtmTbMsojBVLEERgvcsHtGz/AIKh1QojXu2PZZKiPudHqcE04/FuPZfNuaaRti7bfcvsA4A5iAAAAAAAAAAAAAAAAAAAAAAAAAA+df2is5k9Tn4dA9f2ms5s9Tn4iMXctDGxfex+cZPJ0fG63lIjFlsg2Qb97uLKxBv3pD4ZNlfEHwybZNssty5LEG5dXol8mvN13iqPKpUXV6JfJrzdd4qjyuQ6YuFd36puZY3K0e9U9F62A88MCAAAANAta12rNhj/ACr66rE39aBa1qMarNhzr66rE3nRrxUXXb+LrZHJPyyjr+CVfm2WURgRGA9YbDeIgBMRxlWISRBEcZZAqkiBsfq+I/bRZOT953j4rWNcYjFsfq+p/bRZORH2nePitY17O3hDfepV/ll89/j4Ja9LPgW1gPGrmwAAAAAAAAAAAAAAAAAAAAAAADynSr5OecHvJX+RTbELktKvk6Zwe8lf5FN70loV4U3jqm5pdVzBjG52vTeSAExHGXZ4hv8AEERxk2zJtmWURgqliCIwAVXC96yxhZqmPudHqUQr37PsqKuP6EdTgWnHYuHZfNuZaRti7bfcvoA4C5iAAAAAAAAAAAAAAAAAAAAAAAAAAwru01nNnqc/OyHQNXdpp82epz8797uWhjYvvY/OMrkzg6rreU370h8Mu47LLRB8Mm2TbLLcuSxBuBO8SRBvXVaJfJrzdd4qjyqV4jBdRol8mzN13iqPK5Dpj4V3fqm5li8rx71T0XrYDzw18AAAAaB61ntWbDnX11WJv40D1rPas2HOvnqsTetGvFRddv4utkskcG+0dfwSr9BMRxl6wiG9xBEcZZAqkiBMRiRGJM8IV2UkQTPCGx+r5jDShyd+R3j4rWNcYjBsfq+eVDk78jvHxWsa9ndwgvvUq/yy+fKMYXO16WfAtqAeNHMgAAAAAAAAAAAAAAAAAAAAAAAHlOlVydM4HeSu8im9chpVcnTOB3kr/IpwiOMvSehThTeOqbml1jR/HwK16byQRHGTbMm2ZZRGDs7oMQRGACq4AAXwVOyqoR/RjqUPr4aEYUKMfBDgWnH6h2XzbmWkb6tt9wyAcBcxAAAAAAAAAAAAAAAAAAAAAAAAAAYV3aqfNnqc/ToFru1U+bPU5+vhl3LQxsX3sfnGWyXGOr63lPhk2ybZZbnc2aiDckN4kiDeyiMCIwFV8QLqNEvk2Zuu8VR5VK66jRL5NmbrvFUeVyHTHwru/VNzLF5ZjCyp6PketgPO7XAAAABoHrWe1ZsOdfXVYm/jQTWsRjVZsOdfXVYm9aNeKi67fxdbJ5G+XUdfwSr9iOMsgesW/RAmIxIjEmeEK7KSIJnhCYjAiMEqpYgbHavnlQ5O/I7x8VrGuLZDV8xhpQZPfIrx8VrGvZ3cIL71Kv8ALL5soxhcrXpZ8C2gB4zcuAAAAAAAAAAAAAAAAAAAAAAAAeU6VXJ0zgd5K7yKcNsyuP0quTpnA7yV3kU5RGD0noU4U3jqm5pda0e/IrXp/JBEYAO0OggAAAC+KNkRCh2IxmIXxuA6cvqHZfNuY6Rvq233AA4E5kAAAAAAAAAAAAAAAAAAAAAAAAAAwre1U+bPU5+tsy6Ba3tVPmy5/NzuehfYvvY/OMzkmMdX1vKbkhvdyZuIN7KIwIjAVXxACYhVLEYEQuL0WMu8h7u0ds39hvDLK47LaKm5KihWVNdeNTQp0KW3ZSozSxifjU6panndmrRnZdrO7V2s2eoq1WMRjjwJjDZjkvnvlyi+URRM4YSve9kfN53eZO9KVHpHsj5vO7zJ3pSo9JRDEcZNstA1mLvzZPcR6z4IyBTPz/u/Ve97I+bzu8yd6UqPSPZHzed3mTvSlR6SiOIwFdZe782T3EesujN6mfpPu/Ve57I+bzu8yd6UqPSPZHzed3mTvSlR6SiNMRxk1l7vzZPcR6y+M3KZ+k+79V9t05QXBf8AQrKy4r8u+8qNTMRWUrJaaFdFCZ3RPqZnDHCd7RTWr9qzYc6+eqxP0dVf9jGcH5fYPm65+drV+1ZsOdfPVYms5tZHpyBn7Z5Opr1UUTVwcMMcbGqdjg8l8dxu0XXKtNjE44Y/llX+mIxIjEmeEPSmy3eIJnhCYjAiMErksQAyiMFUsQRGDY7V9cqDJ75FePitY1xbH6vrlQZPfIrx8VrGu53cIL71Kv8ALL5MpR8CtelnwLNs62djI3MxkpOWeXVrtFnuyLTV2X1dRZ6VdS9cp4+pj1NHbh/0zteNdkO0Zp/hBfPRFd5n8Gsf5OVKPdv6xdVYqwmcHG8wtH+Ss5ck+7b5VXFerqp/lmIjCIjk0zyWsZFyHdsoXbe1rM44zHAn9Fr3ZDtGbugvnoiu8x2Q3Rn7oL56IrvMqhiOMpbprP5v8ta91T6rMxmpceTV249C13shujP3QXz0RXeY7Iboz90F89EV3mVRbiIxV1ns3+Wte6p9VdGaVx5NXbj0LXY1hmjPP8IL56IrvMnshejP3QXz0RXeZVHuSrrPZv8ALWvdU+qvjNG4Tx6u3HoWt9kM0Z+6C+eiK7zHZC9Gif4QXz0RXeZVJEYstxrPZv8ALWvdU+qvjM/J/Jq7ceha12QrRo7oL56IrvMdkK0aO6C+eiK7zKpRXWdzf5a17qn1V8Zm5P5NXbj0LWuyFaNHdBfPRFd5jshWjR3QXz0RXeZVN8MpiOMms7m9y1r3VPqrozMyfPHq7cehaz2QnRp7oL46IrvMdkJ0ae6C+OiK7zKpxXWdzf5a17qn1V8ZlZOnj1duPQtY7ITo090F89EV3mI1hGjTP/3++eiK7zKp4jFluV1nM3uWte6p9VfGZGTeTX249C1bsg+jV3QXx0TXeY7IPo1d0F8dE13mVVBrOZvcta91T6i+Mx8m8mvtx6FqvZB9Grugvjomu8yeyDaNX8/3x0TXeZVTEMjWcze5a17qn1F0Zi5M5Nfbj0LVOyDaNf8AP98dE13mOyDaNf8AP98dE1vmVVpiOMq6zeb3LWvdU+ovjMPJnJr7ceqtT7ILo17/ANX746JrfMdkG0a/5/vjomt8yqzbMsojBXWbze5a17qn1F8ZhZL5avtx6qxbPvpr5hsvcz2VuRuTl83pW3ne92VllstCsu2soUaVZSwwiaU7I+NXSDdM2c1rjmpd67tcZqmmqdVOqmJnHCI40RyGwZIyNd8iWVVldpnCqceDOPGw5EADZGXAAAATQ206MfDC+JQ/VRjW0I/pR1r4HAdOP1Dsvm3MdI31bb7gAcCcyAAAAAAAAAAAAAAAAAAAAAAAAAAY1na6fNlz+OgOs7XS5sufze7noX2L72PzjN5Hj4/W8pvZRGBEYDubOxACYhVJEEQkSqliMAiOMkRxk2yL4jE2yyiMCIwFdhLEAJiOMqxCSIIjjLIFUkQsR1V/2MZwfl9g+brn5+tWjGqzYc6+eqxP0NVf9jGcH5fYPm65+drV+05sedfPVYnBbL/lDrz4iWr0x/rv+co0AmeEJiMCIwS743GIAZRGCqWIIjAAiMV8QNj9Xzyn8n/kV4eLU2uMRi2Q1ffKfyfj7yvDxam1/O/hBfepV/ll8mU4+BWvSz4G3+sgnDRz/wDPWLwa1VjEcZWm6yHk6Ue/9i8CtVZtR0RcT3ZKvBSx+asfANtPkDcbiIxdRiG0RBEYstxuSqkiAiMSIxZblUkQbgFdhLEYCfhk+GUxHGVV8RiRHGUgqliAiMSIxZblUkQbkgqkiAiCIZCSIATEcZViEkQRHGTbMm2ZZRGCqWIIjABVcAAAAAAAA+ln219XH9OOte+ohssY2mpj7pR617zgGnHZuHZfNuY6Rtm7bfcgDgbmQAAAAAAAAAAAAAAAAAAAAAAAAADGs7XS5suf6IwdANZ2ul8Uuf53TQv9e7H5xncixjq+t5QExDubPxBEJEqpYjAIjjJEcZNsi+IxNssojAiMBXYSxACYjjKsQkiCI4yyBVJECYjEiMSZ4QbKSIWI6rD7GM4Py+wfN1r87Wq9qzY86+eqxP0dVhGGTGcH5fYPm61+drVe05sedfPVY3BbL/lDrz4iWq0R/r2H+fEaAgyiMHfW6RBEYAERiviBMRiRGKZnBckiCZwbHavqP2z+T8/eV4eLU2uMRxlsfq+uU9k/8ivDxam13O/hBfepV/ll8mVI+A23Sz4G3usi5OtD8YLF4Fcq03LStZHOGjtVfDlDYvm65VrEYtT0RR/t3slXkY/NSPgG2nyERiy3G5LqDaIgIjEiMWW5VJEG4BXYSxGAn4ZPhlMRxlVfEYkRxlIKpYgIjEiMWW4SRBuSC5JEBEEQyEkQAmI4yrEJIgiOMm2ZNsyyiMFUsQRGACq4AAAAAAAAAB9rHGNsqI+6Uete6ojsEY26zx91odcL3HANOPxrj2XzbmGkbZu233IA4G5mAAAAAAAAAAAAAAAAAAAAAAAAAAxrPqKXxS5/nQDT+opfFLn/AIh3TQt9e7F5xn8h/P63lIhIl3RsURgERxkiOMm2RfEYm2WURgRGArsJYgBMRxlWISRBEcZZAqkiBMRiRGJM8INlJEEzwhMRgRGCVyWIWIarH7GM4Hy+wfN1r87Wq9qzY86+eqxv0dVj9jGcH5fYPm61+frVO1ZsedfPVY3A7L/lDrz4iWpUR/uD/OUaAxGADvsRi3WIExGJEYpmcFySIJnAiOMkRxlIliBsfq+uU9cHyK8PFqbXDc2P1fXKeuD5DeHi1Nrud8f7fvvUq/yy+PKsfALbpavA261knJ3qI93KKxfN1yrjctH1ks/tebP8OUdj+ar1XLVNEXE72SryMbmnH+n7afIERiRGLLc6g2qINwCuwliMBPwyfDKYjjKq+IxIjjKQVSxARGJEYstwkiDckFySICIIhkJIgBMRxlWISRBEcZNsybZllEYKpYgiMAFVwAAAAAAAAAAAD+i7oxvCyx92oeFC9tRLdkY3lZI+71fhQvaef9OPxrj2XzbmGkbZu233IA4I5mAAAAAAAAAAAAAAAAAAAAAAAAAAxp/UUvilQA6AX+U9ibNX72mSnQ1m9Bv+Y2edlmjvfeljNpvTU7E4YanVfZOzqmSyff6blqsacccPuxUVERxler7E2av3tMlOhrN6B7E2av3tMlOhrN6Df9ea7cyVd1HoZP8Aj1HKT21FW2WURgvT9ibNX72mSnQ1m9A9ifNZ72mSvQ1m9A157rzJV3cehdGcFHKT21FgvT9ifNZ72mSvQ1m9A9ifNZ72mSvQ1m9BWNM915kq7uPQujOKiPo57ai2I4yyXoexPms97TJXoazegexPms97TJXoazega9F15kq7uPQvjOOz/wCue2ovTEYr06Oa7NnRiKNHN1kxERuiLos/oJ9jDNp73mTPRNn9A16LtzJV3ceqrGctEfRz2/0UVzPCExGC9P2MM2vveZM9E2f0D2Mc2vve5M9E2f0DXpu3MdXdx6q+M57OPo57f6KLRel7GGbX3vMmeibP6B7GObX3vcmeibP6CuvTduY6u7j1V0Z02cfRT2/0ae6rKMMmM4Hy+wfN1r8/WqdqzY86+eqxt5rmybydycoVtXk9cF3XXQr5ilW0bFZauoinMbppRQiMcMZ3v0nOt/OmjOqc5KLHGMfiarD6PUfGwno7H2ML/FYjKPu+KOtj/bhs4eRQSmIxX6jfde3nHvvs2b37v/j+L9qguZwIjjK/QNe3nHvvs10Z4YfQ/i/aoMNy/MNe3nHvvs10Z5YfQfi/aoMiMWyGr72aTtwfIbw8WprYxj8saXv4tk+2uPuPU70pqpx3pjhjGGOG84xw6MIb3nZ7qsK7DeOGqiYx1XJ2rVPWTT+15sv4x2P5qvVdxGK/AYnNHSVvq5O/h/uXen801Y6vU7OHAw1FXI5L5skZyfwq77w3lquDM46rDZ60qEdwvuG0a93OHffZsrGe+H0H4v2qEU/DK+0Ne/nDvvs12/zzv+P9qhOI4ylfWK69/OHffZrt/vnf8f7VChEYr6w17+cO++zXxn7h9X/H+1QtuSvoFdfDnDvvs10Z/wDO/wCP9qhciF9Aa+HOHffZqxpBw+rfj/aoZF8wa+POHffZr40h4fVvx/sUNRHGTbMr5RXXx5w777NdGkXD6t+P9ihyIwF8Ya+XOHffZq643O34/wBihwXxhr5c4d99ma43O34/2KHBfGGvlzh332Zrjc7fj/YocF8Ya+XOHffZmuNzt+P9ihwXxhr5c4d99ma43O34/wBihwXxhr5c4d99ma43O34/2KHBfGGvlzh332Zrjc7fj/YocF8Ya+XOHffZmuNzt+P9iia6oxvSxx7toq/CheyDn+fGfG/nNhO8N5by1XztVjqtT/bThhqft2WsZx5xb8E2c7y1Gox+djjjh9kcgAaE1kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB/9k="></p>"""
    s = "Hello {{name}}"
    comms_cmd.send_personalized_emails(
        email_subject="{{name}}",
        raw_html=s,
        uow=FakeUnitOfWork(),
        auth_acl=auth_acl,
        task=comms_cmd.send_image_email,
    )

    assert False
