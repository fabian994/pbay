from django import forms
from .models import *
from django.core.validators import RegexValidator

letras = RegexValidator(r'^[a-zA-Z " " éáíóúñÑÁÉÍÓÚ]*$', 'Solo se pueden ingresar letras ')
numeros = RegexValidator(r'^[0-9]*$', 'Solo se pueden ingresar numeros')
numerosYletras = RegexValidator(r'^[0-9a-zA-Z " "éáíóúñÑÁÉÍÓÚ]*$', 'Solo se pueden ingresar numeros y letras')
numerosYletrasSimbolos = RegexValidator(r'^[0-9a-zA-Z \séáíóúñÑÁÉÍÓÚ\.\-\#]*$', 'Solo se pueden ingresar numeros y letras')

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
    
    brand = forms.CharField( max_length = 40,
                             required = True,
                             label = "Marca",
                             
                             error_messages={
                                 "required": "No puede estar vacío",
                             },
                             widget = forms.TextInput(attrs= {
                                 "class": "input-field"
                             })
                             )
    
    model = forms.CharField( max_length = 40,
                             required = False,
                             label = "Modelo (opcional)",
                             widget = forms.TextInput(attrs= {
                                 "class": "input-field"
                             })
                             )
    
    title = forms.CharField( max_length = 40,
                            validators=[numerosYletrasSimbolos],
                             required = True,
                             label = "Título",
                             
                             error_messages={
                                 "required": "No puede estar vacío",
                             },
                             widget = forms.TextInput(attrs= {
                                 "class": "input-field"
                             })
                             )
    
    condition = forms.ChoiceField( required = True,
                                  label = "Condición",
                                  choices=(("","---"),("true","Nuevo"),("false","Usado")),
                                  error_messages={
                                      "required": "No puede estar vacío"
                                  },
                                  widget= forms.Select(attrs={
                                      "class": "input-field"
                                  }))
    
    about = forms.CharField ( required = True,
                             label = "Descripción",
                             error_messages={
                                 "requirer": "No puede estar vacío",
                             },
                             widget= forms.Textarea(attrs={
                                 "class": "form-control",
                                 "rows": 4,
                                 "cols": 40,
                             }))
    
    vendType = forms.ChoiceField( required = True,
                                  label = "Tipo de venta ",
                                  choices=(("","---"),("true","Subasta"),("false","Venta Inmediata")),
                                  error_messages={
                                      "required": "No puede estar vacío"
                                  },
                                  widget= forms.Select(attrs={
                                      "class": "input-field"
                                  }))
    
    publishDate = forms.DateField(   
                                required = True,
                                label = "Fecha de Publicación",
                                widget=forms.DateInput(attrs={
                                    "class" : "input-field",
                                    "type": "date"
                                })
                                )
    
    promote = forms.ChoiceField( required = True,
                                  label = "Destacar",
                                  choices=(("","---"),("true","Si"),("false","No")),
                                  error_messages={
                                      "required": "No puede estar vacío"
                                  },
                                  widget= forms.Select(attrs={
                                      "class": "input-field"
                                  }))
    
    category = forms.ModelChoiceField( required = True, 
                                    label = "Categoria",
                                    queryset = categories.objects.all(),
                                    error_messages={
                                        "required": "No puede estar vacío",
                                    },
                                    widget = forms.Select(attrs = {
                                        "class": "input-field"
                                        }
                                    ))

    subCategory1 = forms.ModelChoiceField(   required = True, 
                                label = "Subcategoria 1",
                                queryset = SubCategory1.objects.filter().order_by('Subcategoria1'),
                                error_messages={
                                    "required": "No puede estar vacío",
                                },
                                widget = forms.Select(attrs = {
                                    "class": "input-field",
                                    }
                                ))
    
    subCategory2 = forms.ModelChoiceField(   required = True, 
                                label = "Subcategoria 2",
                                queryset = SubCategory2.objects.filter().order_by('Subcategoria2'),
                                error_messages={
                                    "required": "No puede estar vacío",
                                },
                                widget = forms.Select(attrs = {
                                    "class": "input-field",
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

class productDirectSale(forms.Form):
    inventory = forms.IntegerField(    max_value=999999,
                                        required = True, 
                                        label = "Inventario",
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.TextInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))

    cost = forms.IntegerField(    max_value=999999,
                                        required = True, 
                                        label = "Costo",
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.TextInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))
    
    shippingFee = forms.IntegerField(    max_value=999999,
                                        required = True, 
                                        label = "Costo de Envio",
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.TextInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))
    
    RemovalDate = forms.DateField(   
                                required = True,
                                label = "Fecha de Retiro",
                                widget=forms.DateInput(attrs={
                                    "class" : "form-control",
                                    "type": "date"
                                })
                                )
    
    # promote = forms.ChoiceField( required = True,
    #                             label = "Promocionar: ",
    #                             choices=(("","---"),("YES", "Si"), ("NO", "No")),
    #                             error_messages={
    #                                 "required": "No puede estar vacío",
    #                             },
                                
    #                             widget = forms.Select(attrs = {
    #                                 "class": "form-control"
    #                                 }
    #                             ))
    
class productAuction(forms.Form):
    duration = forms.ChoiceField(required = True, 
                                        choices = (("", "---"),
                                                   ("3", "3 Dias"), 
                                                   ("5", "5 Dias"),
                                                   ("10", "10 Dias"),), 
                                        label = "Duracion de Subasta",
                                        widget = forms.Select(attrs = {
                                                    "class": "form-control",
                                                },
                                        ))
    
    initialOffer = forms.IntegerField(    max_value=999999,
                                        required = True, 
                                        label = "Oferta Inicial",
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.NumberInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))

    minimumOffer = forms.IntegerField(    max_value=999999,
                                        required = True, 
                                        label = "Oferta Minima",
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.NumberInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))
    
    shippingFee = forms.IntegerField(    max_value=999999,
                                        required = True, 
                                        label = "Costo de Envio",
                                        error_messages={
                                            "required": "No puede estar vacío",
                                        },
                                        widget = forms.NumberInput(attrs = {
                                            "class": "form-control"
                                            }
                                        ))

class productPromote(forms.Form):
    PromoDuration = forms.ChoiceField(required = True, 
                                        choices = (("", "---"),
                                                   ("5", "5 Días, Costo: $100"),
                                                   ("10", "10 Días, Costo: $150"),
                                                   ("15", "15 Días, Costo: $200"),
                                        ), 
                                        label = "Duracion de Subasta",
                                        widget = forms.Select(attrs = {
                                                    "class": "form-control",
                                                },
                                        ))
