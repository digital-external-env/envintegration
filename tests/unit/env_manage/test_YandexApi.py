import asyncio
import os
import unittest

import dotenv

from env_manage import YandexApi


dotenv.load_dotenv("../../.env")
token = os.getenv("client_token")


class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.api = YandexApi(client_token=token)
        self.loop = asyncio.get_event_loop_policy().get_event_loop()

    def test_get_home_info(self):
        result = self.loop.run_until_complete(self.api.get_smart_home_info())
        assert result["status"] == "ok"  # nosec B101


if __name__ == "__main__":
    unittest.main()
