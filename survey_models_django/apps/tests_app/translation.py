from modeltranslation.translator import register, TranslationOptions
from .models import Test

@register(Test)
class TestTranslationOptions(TranslationOptions):
    fields = ('title', 'description')