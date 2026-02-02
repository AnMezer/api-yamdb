from django.contrib.auth.tokens import default_token_generator

class MyTokenGenerator(default_token_generator):
    def make_token(self, user, confirmation_code):
        