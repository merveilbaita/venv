from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.utils import timezone



class Categorie(models.Model):
    nom = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    designation = models.CharField(max_length=120)
    slug = models.SlugField(max_length=100)
    desc_courte = models.TextField(blank=True, null=True)
    desc_longue= models.TextField(blank=True, null=True)
    prix = models.IntegerField()
    qte = models.IntegerField(default=0, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    image_produit = models.ImageField(upload_to='produit_image', blank=True, null=True)
    categorie = models.ForeignKey("Categorie", on_delete=models.CASCADE)
    create_at = models.DateTimeField(default=timezone.now)

    # Champs pour les images supplémentaires
    image_similaire_1 = models.ImageField(upload_to='produit_image', blank=True, null=True)
    image_similaire_2 = models.ImageField(upload_to='produit_image', blank=True, null=True)
    image_similaire_3 = models.ImageField(upload_to='produit_image', blank=True, null=True)

    def __str__(self):
        return self.designation
    

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    qte_order = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.produit.designation} ({self.qte_order})" 
    
    def complete_order(self):
        produit = self.produit
        if produit.qte >= self.qte_order:
            produit.qte -= self.qte_order
            produit.save()
            self.ordered = True
            self.ordered_date = timezone.now()
            self.save()
        else:
            raise ValidationError(f"Le produit {produit.designation} n'a pas assez de stock.")
        
    def get_total(self):
        total = sum(order.produit.prix * order.qte_order for order in self.orders.all())
        return total

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , null=True, blank=True)
    orders = models.ManyToManyField(Order)
    ordered_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = sum(order.produit.prix * order.qte_order for order in self.orders.all())
        return total

class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    adresse = models.CharField(max_length=255)
    ville = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.adresse