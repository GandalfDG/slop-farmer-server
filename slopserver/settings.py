from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    db_url: str = "sqlite+pysqlite:///test_db.sqlite"
    token_secret: str = "5bcc778a96b090c3ac1d587bb694a060eaf7bdb5832365f91d5078faf1fff210"
    altcha_secret: str = "0460de065912d0292df1e7422a5ed2dc362ed56d6bab64fe50b89957463061f3"
    resend_token: str = "re_NXpjzbqR_KgAbu72PKjYHcquX24WvnN3i"

    sender_email: str = "slopfarmer@jack-case.pro"

settings = ServerSettings()
