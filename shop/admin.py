from django.contrib import admin

from shop.models import Order, Categorie, Produit, Cart, ShippingAddress

# Register your models here.
admin.site.register(Produit)
admin.site.register(Categorie)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(ShippingAddress)