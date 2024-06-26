from factory import Factory, Faker

from shatoon.results import Result


class ResultFactory(Factory):
    class Meta:
        model = Result

    command = Faker("word")
    stdout = Faker("sentence")
    stderr = Faker("sentence")
    return_code = Faker("random_int")
