from django import forms
from .models import *

class Filter(forms.Form):
    Filtering = forms.ChoiceField(
        label='Filtrar   ',
        choices=[
            ('nada', 'Ninguna'),
            ('subasta', 'Subastas'),
            ('directa', 'Ventas directas'),
        ]
    )

class categoriesForm(forms.Form):
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