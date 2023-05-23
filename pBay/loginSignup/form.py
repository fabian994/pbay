from django import forms
from django.core.validators import RegexValidator

Correo=RegexValidator(
            regex='^^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Ingrese una dirección de correo electrónico válida.',
            code='invalid_email'
        )

class MiFormulario(forms.Form):
    campo1 = forms.CharField( max_length = 20, 
                            required = True, 
                            label = "Correo",
                            validators=[Correo],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
    
    campo2 = forms.CharField( max_length = 20, 
                            required = True, 
                            label = "Correo",
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
