from django.contrib import admin

from shop.models import Order, Categorie, Produit, Cart, ShippingAddress, Stock, Vente

# Register your models here.
admin.site.register(Produit)
admin.site.register(Categorie)
admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(ShippingAddress)
admin.site.register(Vente)
admin.site.register(Stock)