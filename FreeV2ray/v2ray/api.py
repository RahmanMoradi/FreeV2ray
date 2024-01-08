import base64
import json
from uuid import uuid4
from datetime import datetime, timedelta

from pyxui import XUI
from pyxui.errors import NotFound
from pyxui.config_gen import config_generator
from faker import Faker

from FreeV2ray.app import config
from FreeV2ray.v2ray import models


class V2ray:
    def __init__(self, username: str, password: str):
        self.xui = None
        self.username = username
        self.password = password

        full_address = "https://" + config.get("V2RAY_ADDRESS") + ":2053"
        # if database was not empty:
        if models.XuiSession.select().first():
            last_session = models.XuiSession.select().order_by(models.XuiSession.id.desc()).get()
            if last_session:
                self.xui = XUI(
                    full_address=full_address,
                    panel="sanaei",
                    session_string=last_session.session_string
                )
                try:
                    self.xui.get_inbounds()
                except:
                    self.xui = None

        # if there was no session stored:
        if not self.xui:
            self.xui = XUI(
                full_address=full_address,
                panel="sanaei",
            )
            self.xui.login(self.username, self.password)
            models.XuiSession.create(session_string=self.xui.session_string, created_at=datetime.now())

    def create_client(self, email: str):
        uuid = str(uuid4())
        expire_days = int(config.get("EXPIRE_TIME"))
        expire_date = datetime.now() + timedelta(expire_days)
        expire_timestamp = int(expire_date.timestamp() * 1000)

        client = self.xui.add_client(
            inbound_id=config.get("INBOUND_ID"),
            email=email,
            uuid=uuid,
            enable=True,
            flow="",
            limit_ip=int(config.get("LIMIT_IP")),
            total_gb=int(config.get("TOTAL_GB")),
            expire_time=expire_timestamp,
            telegram_id="",
            subscription_id=""
        )
        if not client["success"]:
            return False

        return self.generate_config(email)

    def get_client(self, email: str):
        try:
            return self.xui.get_client(int(config.get("INBOUND_ID")), email=email)
        except NotFound:
            return False

    def get_or_create_client(self, email: str) -> tuple:
        if client := self.get_client(email):
            return client, False

        return self.create_client(email), True

    def extend_client_date(self, email: str):
        client = self.get_client(email)
        if not client:
            return False

        expire_days = int(config.get("EXPIRE_TIME"))
        expire_date = datetime.now() + timedelta(expire_days)
        expire_timestamp = int(expire_date.timestamp() * 1000)

        return self.xui.update_client(
            inbound_id=int(config.get("INBOUND_ID")),
            email=client.get("email"),
            uuid=client.get("id"),
            enable=client.get("enable"),
            flow="",
            limit_ip=client.get("limitIp"),
            total_gb=client.get("totalGB"),
            expire_time=expire_timestamp,
            telegram_id=client.get("tgId"),
            subscription_id=client.get("subId"),
        )

    def generate_config(self, email: str, protocol: str = "vmess"):
        client = self.get_client(email)
        payload = {
            "add": config.get("V2RAY_ADDRESS"),
            "aid": "0",
            "host": config.get("V2RAY_HOST"),
            "id": client["id"],
            "net": "ws",
            "path": config.get("V2RAY_PATH"),
            "port": config.get("V2RAY_PORT"),
            "ps": client.get("email"),
            "scy": "auto",
            "sni": config.get("V2RAY_SNI"),
            "tls": "tls",
            "type": "none",
            "v": "2"
        }

        # Convert the JSON object to a string
        json_string = json.dumps(payload)
        # Convert the string to bytes
        byte_data = json_string.encode('utf-8')
        # Encode the bytes
        encoded_data = base64.b64encode(byte_data)

        return protocol + "://" + encoded_data.decode()


if __name__ == "__main__":
    panel = V2ray(config.get("PANEL_USERNAME"), config.get("PANEL_PASSWORD"))
    result = panel.get_client("799041666")
    print(result)
