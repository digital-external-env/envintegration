import unittest

from pes_digenv import TextEmotionApi


class TestApi(unittest.TestCase):
    def setUp(self) -> None:
        self.api = TextEmotionApi()

    def test_is_toxic(self):
        self.assertTrue(self.api.is_toxic('Ты дурак'))
        self.assertTrue(self.api.is_toxic('Ну и лошара'))
        self.assertTrue(self.api.is_toxic('От тебя воняет'))
        self.assertTrue(self.api.is_toxic('Вот ты собака ползаборная'))
        self.assertFalse(self.api.is_toxic('Люблю милых котиков'))
        self.assertFalse(self.api.is_toxic('Обратись к психотерапевту, это действительно может тебе помочь'))
        self.assertFalse(self.api.is_toxic('Работаем не покладая рук!'))

    def test_get_mat(self):
        self.assertFalse(self.api.get_mat('Ты дурак'))
        self.assertTrue(self.api.get_mat('Ты мудила'))
        self.assertTrue(self.api.get_mat('Хуйня из-под коня'))
        self.assertFalse(self.api.get_mat('Ты такая милая'))
        self.assertTrue(self.api.get_mat('хуегномы угрожают бомбардировкой'))
        self.assertFalse(self.api.get_mat('Казахстан угрожает нам бомбардировкой'))
        self.assertFalse(self.api.get_mat('Мудоёбище должно нас не заметить. Иначе мы попадём в просак'))
    def test_emotion(self):
        self.assertTrue(self.api.emotion('Мне так плохо'))
        self.assertTrue(self.api.emotion('Завтра выходной!'))
        self.assertTrue(self.api.emotion('Такая ясная погода!'))
        self.assertTrue(self.api.emotion('Ты адекватный?!'))
        self.assertTrue(self.api.emotion('Корабли лавировали-лавировали да не вылавировали'))
        self.assertTrue(self.api.emotion('Мне так хорошо!'))
        

if __name__ == "__main__":
    unittest.main()
