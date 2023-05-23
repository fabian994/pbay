from django import forms

class MiFormulario(forms.Form):
    campo1 = forms.CharField( max_length = 20, 
                            required = True, 
                            label = "Correo",
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
