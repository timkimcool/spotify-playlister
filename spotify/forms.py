from django import forms

class ArtistInfoForm(forms.Form):
    artist_id = forms.CharField(label='artist', max_length=100)