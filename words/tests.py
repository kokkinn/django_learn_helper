from googletrans import Translator
from faker import Faker

faker = Faker()
translator = Translator()
word1 = faker.word()
print(word1)
tr = translator.translate(str(word1), src="en", dest="ru")
word2 = tr.text
print(word2)
