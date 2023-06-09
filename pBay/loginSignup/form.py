from django import forms
from django.core.validators import RegexValidator

Correo=RegexValidator(
            regex='^^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Ingrese una dirección de correo electrónico válida.',
            code='invalid_email'
        )
letras = RegexValidator(r'^[a-zA-Z " " éáíóúñÑÁÉÍÓÚ]*$', 'Solo se pueden ingresar letras ')
numeros = RegexValidator(r'^[0-9]*$', 'Solo se pueden ingresar numeros')
numerosYletras = RegexValidator(r'^[0-9a-zA-Z " "éáíóúñÑÁÉÍÓÚ]*$', 'Solo se pueden ingresar numeros y letras')
contraVal = RegexValidator(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,16}$', 'Debe de cumplir con los requisitos de contraseña')
#"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,10}$"


class MiFormulario(forms.Form):
    campo1 = forms.CharField( max_length = 30, 
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
                            widget=forms.PasswordInput(attrs = {
                                            "class": "form-control"
                                        }))

class directionForm(forms.Form):
     campo = forms.CharField( max_length = 20, 
                            required = True, 
                            label = "Direccion",
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
     
class ListForm(forms.Form):
     campo = forms.CharField( max_length = 20, 
                            required = True, 
                            label = "Direccion",
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))



class signUpForm(forms.Form):
    name = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Nombre(s)",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))

    lastNames = forms.CharField( max_length = 80, 
                                required = True, 
                                label = "Apellido Paterno",
                                validators=[letras],
                                error_messages={
                                    "required": "No puede estar vacío",
                                },
                                widget = forms.TextInput(attrs = {
                                    "class": "form-control"
                                    }
                                ))
                                    
    birthDate = forms.DateField(   
                                    required = True,
                                    label = "Fecha de Nacimiento",
                                    widget=forms.DateInput(attrs={
                                        "class" : "form-control",
                                        "type": "date"
                                    })
                                    )
                                    
    curp = forms.CharField( max_length = 18, 
                            min_length = 18, 
                            required = False, 
                            label = "CURP",
                            validators=[numerosYletras],
                            error_messages={
                                "required": "No puede estar vacío",
                                "min_length": "El CURP debe ser de 18 caracteres..."
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
    
    official_id = forms.ImageField(label = "Identificación Oficial (INE, Pasaporte, etc )", 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))

    direction1 = forms.CharField( max_length = 80, 
                                required = True, 
                                label = "Apellido Paterno",
                                validators=[letras],
                                error_messages={
                                    "required": "No puede estar vacío",
                                },
                                widget = forms.TextInput(attrs = {
                                    "class": "form-control"
                                    }
                                ))
    
    country = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Pais",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))

    city = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Ciudad",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
    
    state = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Estado",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
    
    postalCode = forms.IntegerField(    max_value=99999,
                                        required = True, 
                                        label = "Codigo Postal",
                                        validators=[numeros],
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.TextInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))
    
    phoneNumber = forms.CharField(  max_length = 10,
                                    min_length = 10, 
                                    required = False, 
                                    label = "Numero Telefonico",
                                    validators=[numeros],
                                    error_messages={
                                        "required": "No puede estar vacío",
                                        "min_length": "El numero telefonico debe ser de 10 caracteres..."
                                    },
                                    widget = forms.TextInput(attrs = {
                                            "class": "form-control"
                                        }
                                    ))
    
    mail = forms.EmailField(   required = True, 
                                label = "Correo Electronico",
                                error_messages={
                                    "required": "No puede estar vacío",
                                    "invalid": "El formato de correo esta mal",
                                },
                                widget = forms.EmailInput(attrs = {
                                    "class": "form-control",
                                    "type": "email"
                                    }
                                ))
    
    c_mail = forms.EmailField(   required = True, 
                                label = "Confirmar Correo Electronico",
                                error_messages={
                                    "required": "No puede estar vacío",
                                    "invalid": "El formato de correo esta mal",
                                },
                                widget = forms.EmailInput(attrs = {
                                    "class": "form-control",
                                    "type": "email"
                                    }
                                ))

    password = forms.CharField(max_length = 16,
                               min_length = 8,
                               required = True, 
                                label = "Contraseña",
                                validators=[contraVal],
                                error_messages={
                                    "required": "No puede estar vacío",
                                    "invalid": "No contiene las especificaciones",
                                },
                                widget=forms.PasswordInput(attrs = {
                                            "class": "form-control"
                                        }))
    c_password = forms.CharField(max_length = 16,
                               min_length = 8,
                               required = True, 
                                label = "Contraseña",
                                validators=[contraVal],
                                error_messages={
                                    "required": "No puede estar vacío",
                                    "invalid": "No contiene las especificaciones",
                                },
                                widget=forms.PasswordInput(attrs = {
                                            "class": "form-control"
                                        }))

class updateInfoForm(forms.Form):
    name = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Nombre(s)",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))

    lastNames = forms.CharField( max_length = 80, 
                                required = True, 
                                label = "Apellido Paterno",
                                validators=[letras],
                                error_messages={
                                    "required": "No puede estar vacío",
                                },
                                widget = forms.TextInput(attrs = {
                                    "class": "form-control"
                                    }
                                ))
                                    
    country = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Pais",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))

    city = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Ciudad",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
    
    state = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Estado",
                            validators=[letras],
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
    
    postalCode = forms.IntegerField(    max_value=99999,
                                        required = True, 
                                        label = "Codigo Postal",
                                        validators=[numeros],
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.TextInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))
    
    phoneNumber = forms.CharField(  max_length = 10,
                                    min_length = 10, 
                                    required = False, 
                                    label = "Numero Telefonico",
                                    validators=[numeros],
                                    error_messages={
                                        "required": "No puede estar vacío",
                                        "min_length": "El numero telefonico debe ser de 10 caracteres..."
                                    },
                                    widget = forms.TextInput(attrs = {
                                            "class": "form-control"
                                        }
                                    ))
    

    # VALIDATIONS

    # def clean_curp(self):
    #     curp = self.cleaned_data.get("curp")
    #     for instance in Padron.objects.all():
    #         if instance.curp == curp:
    #             raise forms.ValidationError("El CURP " + curp + " ya esta registrada") 
    #     return curp

    def clean_name(self):
        name = self.cleaned_data.get("name")   
        name = name.replace("á" , "a")
        name = name.replace("é" , "e")
        name = name.replace("í" , "i")
        name = name.replace("ó" , "o")
        name = name.replace("ú" , "u")
        name = name.replace("ñ" , "nh")
        name = name.replace("Á" , "A")
        name = name.replace("É" , "E")
        name = name.replace("Í" , "I")
        name = name.replace("Ó" , "O")
        name = name.replace("Ú" , "Ú")
        name = name.replace("Ñ" , "Nh")
        return name

    def clean_lastName(self):
        lastName = self.cleaned_data.get("lastName")  
        lastName = lastName.replace("á" , "a")
        lastName = lastName.replace("é" , "e")
        lastName = lastName.replace("í" , "i")
        lastName = lastName.replace("ó" , "o")
        lastName = lastName.replace("ú" , "u")
        lastName = lastName.replace("ñ" , "nh")
        lastName = lastName.replace("Á" , "A")
        lastName = lastName.replace("É" , "E")
        lastName = lastName.replace("Í" , "I")
        lastName = lastName.replace("Ó" , "O")
        lastName = lastName.replace("Ú" , "Ú")
        lastName = lastName.replace("Ñ" , "Nh")
        return lastName

    def clean_momLastName(self):
        momLastName = self.cleaned_data.get("momLastName")   
        momLastName = momLastName.replace("á" , "a")
        momLastName = momLastName.replace("é" , "e")
        momLastName = momLastName.replace("í" , "i")
        momLastName = momLastName.replace("ó" , "o")
        momLastName = momLastName.replace("ú" , "u")
        momLastName = momLastName.replace("ñ" , "nh")
        momLastName = momLastName.replace("Ñ" , "Nh")
        momLastName = momLastName.replace("Á" , "A")
        momLastName = momLastName.replace("É" , "E")
        momLastName = momLastName.replace("Í" , "I")
        momLastName = momLastName.replace("Ó" , "O")
        momLastName = momLastName.replace("Ú" , "Ú")
        momLastName = momLastName.replace("Ñ" , "Nh")
        return momLastName


    def clean_postalCode(self):
        postalCode = self.cleaned_data.get("postalCode")

        if len(str(postalCode)) != 5:
            raise forms.ValidationError("El codigo postal debe ser de 5 caracteres...")
        
        return postalCode

    def clean_phoneNumber(self):
        phoneNumber = self.cleaned_data.get("phoneNumber")
        mail = self.cleaned_data.get("mail")
        if ((phoneNumber == "") and (mail == "")):  
            raise forms.ValidationError("Introduce al menos un metodo de contacto")  
        return phoneNumber

    def clean_mail(self):
        phoneNumber = self.cleaned_data.get("phoneNumber")
        mail = self.cleaned_data.get("mail")
        if ((phoneNumber == "") and (mail == "")):  
            raise forms.ValidationError("Introduce al menos un metodo de contacto")  
        return mail  
