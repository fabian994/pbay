from django import forms

class Orden(forms.Form):
    Sorting = forms.ChoiceField(
        label='Ordenar por   ',
        choices=[
            ('ascendente', 'Ascendente'),
            ('descendente', 'Descendente'),
        ]
    )

class Filter(forms.Form):
    Filtering = forms.ChoiceField(
        label='Filtrar   ',
        choices=[
            ('nada', 'Ninguna'),
            ('subasta', 'Subastas'),
            ('directa', 'Ventas directas'),
        ]
    )