from django import forms


# creating a form
class Calculator(forms.Form):
    day = forms.IntegerField(help_text='insert')


class YourForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    increase = forms.CharField(required=False, max_length=5)


class newonef(forms.Form):
    name = forms.CharField(max_length=20)

   