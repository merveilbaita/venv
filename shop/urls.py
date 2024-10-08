from django.urls import path
from shop.views import *

urlpatterns = [
    path('', index, name='index'),
    path('catalogue', catalogue, name='catalogue'),
    path('detail/<str:slug>/', detail, name='detail'),
    path('detail/<str:slug>/add-to-cart', add_to_cart, name='add_to_cart'),
    path('cart/', panier, name='cart'),
    path('cart/delete/<int:order_id>/', delete_cart, name='delete_cart'),
    path('cart/update/<int:order_id>/', update_quantity, name='update_quantity'),
    path('checkout/', checkout, name='checkout'),
    path('save_address/', save_address, name='save_address'),
    path('ord', admin_order, name='admin_order'),
    path('dash', admin_dash, name='admin_dash'),
    path('prod', produit, name='produit'),
    path('ord/orders/delete/<int:order_id>/', delete_order, name='delete_order'),
    path('adr', adress, name='adress'),
    path('regle/', privacy_policy, name='regle'),
    path('ajouter-produit-vente/<int:produit_id>/', ajouter_produit_vente, name='ajouter_produit_vente'),
    path('voir-facture/', voir_facture, name='voir_facture'),
    path('facture/<int:vente_id>/', facture_vente, name='facture_vente'),
    path('ventes-du-jour/', ventes_du_jour, name='ventes_du_jour'),

    
]