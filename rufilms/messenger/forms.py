from django import forms
from .models import Subtitle, Script, Phrases, Button
from django.db.models import Q,QuerySet


class PhraseForm(forms.ModelForm):

    topic=forms.CharField(max_length=20)
    phrases=forms.Textarea()

    class Meta:
        fields=['topic','phrases', 'entry_of_scripts','buttons']

    def __init__(self,*args, **kwargs):
        # dunno how to change it by default in models so used it
        if kwargs.get('instance'):  # :)
            kwargs.get('instance').phrases='&'.join(kwargs.get('instance').phrases)  # merge phrases list
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['phrases'] = cleaned_data['phrases'].split('&')
        return cleaned_data




class SubtitleForm(forms.ModelForm):

    class Meta:
        model=Subtitle
        fields='text',\
               'video_file'


class M2MSlugRelatedField(forms.CharField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.delimiter = kwargs.get('delim', '&')

    def to_python(self, value):
        value=super().to_python(value)
        return value.split(self.delimiter)

    def prepare_value(self, value):
        print(value)
        if value is not None:
            if isinstance(value, list):
                return self.delimiter.join([v.topic for v in value[::-1]])
        else:
            return self.empty_value


class RelatedObjectsMixin:

    def get_related_object(self):
        related_field = list(filter(lambda x: 'related_phrases' in x, self.Meta.fields)).pop()
        return related_field

    def related_field_clean(self, cleaned_data):
        related_field=self.get_related_object()
        print(related_field)
        query = Q(topic__in=[])
        for topic in cleaned_data[related_field]:
            query.add(Q(topic=topic), Q.OR)
        script_qs = Phrases.objects.filter(query)
        cleaned_data[related_field] = script_qs
        return cleaned_data



class ScriptForm(forms.ModelForm, RelatedObjectsMixin):
    script_related_phrases = M2MSlugRelatedField(widget=forms.Textarea)
    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):  # :)
            kwargs.get('instance').topics='&'.join(kwargs.get('instance').topics)  # merge phrases list
        super().__init__(*args,**kwargs)
    class Meta:
        model=Script
        fields='script_related_phrases', 'script_name','topics'

    def clean(self):
        cleaned_data=super().clean()
        cleaned_data=self.related_field_clean(cleaned_data)
        return cleaned_data




class ButtonForm(forms.ModelForm, RelatedObjectsMixin):
    button_related_phrases = M2MSlugRelatedField(widget=forms.Textarea)

    class Meta:
        model= Button
        fields='text', 'button_related_phrases', 'lang'

    def clean(self):
        cleaned_data=super().clean()
        cleaned_data = self.related_field_clean(cleaned_data)
        return cleaned_data
