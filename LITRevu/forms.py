from django import forms
from .models import Ticket, Review

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'headline', 'body']

        widgets = {
            'rating': forms.NumberInput(attrs={'placeholder': 'Rating (0-5)'}),
        }
        


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)