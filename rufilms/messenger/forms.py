from django import forms


class PhraseForm(forms.ModelForm):

    topic=forms.CharField(max_length=20)
    phrases=forms.Textarea()

    def __init__(self,*args, **kwargs):
        # dunno how to change it by default in models so used it
        if kwargs.get('instance'):  # :)
            kwargs.get('instance').phrases='&'.join(kwargs.get('instance').phrases)  # merge phrases list
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['phrases'] = cleaned_data['phrases'].split('&')
        return cleaned_data

    class Meta:
        fields=['topic','phrases']