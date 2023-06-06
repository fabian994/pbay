from django.db import models

# Create your models here.
class categories(models.Model):
    Categoria = models.CharField(max_length=40)
    def __str__(self):
        return self.Categoria 

class SubCategory1(models.Model):
    Cat = models.ForeignKey(categories, on_delete=models.CASCADE)
    Subcategoria1 = models.CharField(max_length=40)
    def __str__(self):
        return self.Subcategoria1
    
class SubCategory2(models.Model):
    SubCat1 = models.ForeignKey(SubCategory1, on_delete=models.CASCADE)
    Subcategoria2 = models.CharField(max_length=40)
    def __str__(self):
        return self.Subcategoria2