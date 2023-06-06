from django import forms
from .models import *
from django.core.validators import RegexValidator

letras = RegexValidator(r'^[a-zA-Z " " éáíóúñÑÁÉÍÓÚ]*$', 'Solo se pueden ingresar letras ')
numeros = RegexValidator(r'^[0-9]*$', 'Solo se pueden ingresar numeros')
numerosYletras = RegexValidator(r'^[0-9a-zA-Z " "éáíóúñÑÁÉÍÓÚ]*$', 'Solo se pueden ingresar numeros y letras')

class Filter(forms.Form):
    Filtering = forms.ChoiceField(
        label='Filtrar   ',
        choices=[
            ('nada', 'Ninguna'),
            ('subasta', 'Subastas'),
            ('directa', 'Ventas directas'),
        ]
    )

class productCreate(forms.Form):
    name = forms.CharField( max_length = 40, 
                            required = True, 
                            label = "Nombre(s)",
                            
                            error_messages={
                                "required": "No puede estar vacío",
                            },
                            widget = forms.TextInput(attrs = {
                                "class": "form-control"
                                }
                            ))
    
    marca = forms.CharField( max_length = 40,
                             required = True,
                             label = "Marca",
                             
                             error_messages={
                                 "required": "No puede estar vacío",
                             },
                             widget = forms.TextInput(attrs= {
                                 "class": "form-control"
                             })
                             )
    
    category = forms.ModelChoiceField( required = True, 
                                    label = "Categoria",
                                    queryset = categories.objects.all(),
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget = forms.Select(attrs = {
                                        "class": "form-control"
                                        }
                                    ))

    subCategory1 = forms.ModelChoiceField(   required = True, 
                                label = "Subcategoria 1",
                                queryset = SubCategory1.objects.filter().order_by('Subcategoria1'),
                                error_messages={
                                    "required": "No puede estar vacío",
                                },
                                widget = forms.Select(attrs = {
                                    "class": "form-control",
                                    }
                                ))
    
    subCategory2 = forms.ModelChoiceField(   required = True, 
                                label = "Subcategoria 2",
                                queryset = SubCategory2.objects.filter().order_by('Subcategoria2'),
                                error_messages={
                                    "required": "No puede estar vacío",
                                },
                                widget = forms.Select(attrs = {
                                    "class": "form-control",
                                    }
                                ))
    
    mainImage = forms.ImageField(label = "Imagen principal", 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))

    image2 = forms.ImageField(label = "Imagen 2",
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))

    image3 = forms.ImageField(label = "Imagen 3", 
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    image4 = forms.ImageField(label = "Imagen 4", 
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    image5 = forms.ImageField(label = "Imagen 5", 
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    image6 = forms.ImageField(label = "Imagen 6", 
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    image7 = forms.ImageField(label = "Imagen 7", 
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    image8 = forms.ImageField(label = "Imagen 8", 
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    image9 = forms.ImageField(label = "Imagen 9", 
                              required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    image10 = forms.ImageField(label = "Imagen 10", 
                               required = False, 
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget=forms.FileInput(attrs={
                                        "class" : "form-control",
                                        "type": "file"
                                    }))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subCategory1"].queryset = SubCategory1.objects.none()
        self.fields["subCategory2"].queryset = SubCategory2.objects.none()

        if "category" in self.data:
            try:
                categories = int(self.data.get("category"))
                
                self.fields["subCategory1"].queryset = SubCategory1.objects.filter(Cat_id = categories)
                

                if "subCategory1" in self.data:
                    try:
                        subCategory1 = int(self.data.get("subCategory1"))
                        
                        self.fields["subCategory2"].queryset =  SubCategory2.objects.filter(SubCat1_id = subCategory1)
                    
                    except (ValueError, TypeError):
                        pass
            
            except (ValueError, TypeError):
                pass