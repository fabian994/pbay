from django import forms

class MyForm(forms.Form):
    calle1 = forms.CharField(max_length = 200)
    calle2 = forms.CharField(max_length = 200)
    ciudad = forms.CharField(max_length = 200)
    estado = forms.CharField(max_length = 200)
    pais = forms.CharField(max_length = 200)
    cp = forms.CharField(max_length = 200)

    
    