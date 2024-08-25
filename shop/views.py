import datetime
from django.contrib import messages
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LigneVente, ShippingAddress, Vente
from django.db import transaction
from django.db.models import F
import uuid
from django.utils.text import slugify
from django.db.models import Sum, FloatField
from datetime import datetime



from shop.models import Produit , Categorie, Cart, Order

# Create your views here.


def index(request):
    produits = Produit.objects.order_by()[:3]
    return render(request, 'index.html', context={'produits':produits})



def adress(request):
    adresses = ShippingAddress.objects.all()
    return render(request, 'adresse_dash.html', context={'adresses':adresses})

def catalogue(request):
    categorie_smartphone = Categorie.objects.get(nom="smartphone")
    produit_smartphone = Produit.objects.filter(categorie=categorie_smartphone)

    catalogue_ordinateur = Categorie.objects.get(nom="ordinateur")
    produit_ordinateur = Produit.objects.filter(categorie=catalogue_ordinateur)

    catalogue_accessoire = Categorie.objects.get(nom="accessoires")
    produit_accessoires = Produit.objects.filter(categorie=catalogue_accessoire)

    context={
        'produit_smartphone':produit_smartphone,
        'produit_ordinateur':produit_ordinateur,
        'produit_accessoires':produit_accessoires
    }

    return render(request, 'catalogue_produit.html', context)

    
def detail(request, slug):
    produit = get_object_or_404(Produit, slug=slug)
    return render(request, 'detail_produit.html', context={'produit':produit})



def add_to_cart(request, slug):
    user = request.user
    produit = get_object_or_404(Produit, slug=slug)
    
    # Récupérer ou créer un panier pour l'utilisateur
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Vérifier si l'utilisateur a déjà une commande pour ce produit non finalisée
    order, created = Order.objects.get_or_create(user=user, produit=produit, ordered=False)
    
    if created:
        # Si la commande n'existe pas encore, l'ajouter au panier
        cart.orders.add(order)
    else:
        # Si la commande existe, augmenter la quantité
        order.qte_order += 1
        order.save()
    
    return redirect(reverse("detail", kwargs={"slug": slug}))
 


def panier(request):
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour voir votre panier.")
        return redirect('login')

    cart = get_object_or_404(Cart, user=request.user)
    total = cart.get_total()
    return render(request, 'view_cart.html', context={'orders': cart.orders.all(), 'total': total})

    
def delete_cart(request, order_id):
    if request.user.is_authenticated:
        try:
            # Récupérer l'article (order) spécifique dans le panier de l'utilisateur
            order = get_object_or_404(Order, id=order_id, user=request.user, ordered=False)
            
            # Supprimez l'article du panier
            order.delete()
            messages.success(request, "L'article a été supprimé de votre panier.")
        except Order.DoesNotExist:
            messages.error(request, "Cet article n'existe pas ou n'est pas dans votre panier.")
    else:
        messages.error(request, "Vous devez être connecté pour gérer votre panier.")
    
    return redirect(reverse('cart'))

def update_quantity(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_quantity = int(request.POST.get('qte_order', 1))
        order.qte_order = new_quantity
        order.save()

        # Recalculer le total du panier
        total = sum(o.qte_order * o.produit.prix for o in request.user.cart.orders.all())

        return JsonResponse({'total': total})


@login_required
def checkout(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            if cart.orders.exists():
                with transaction.atomic():
                    total_prix = 0
                    out_of_stock = False
                    for order in cart.orders.all():
                        produit = order.produit
                        if produit.qte >= order.qte_order:
                            total_prix += produit.prix * order.qte_order
                        else:
                            messages.error(request, f"Le produit {produit.designation} n'a pas assez de stock.")
                            out_of_stock = True
                            break

                    if not out_of_stock:
                        for order in cart.orders.all():
                            try:
                                order.complete_order()
                                # messages.debug(request, f"Produit: {order.produit.designation}, Quantité commandée: {order.qte_order}, Quantité mise à jour: {order.produit.qte}")
                            except ValidationError as e:
                                messages.error(request, str(e))
                                out_of_stock = True
                                break

                        if not out_of_stock:
                            cart.orders.clear()
                            messages.success(request, "Commande validée avec succès.")
                            return redirect('cart')
                        else:
                            return redirect('cart')
            else:
                messages.error(request, "Votre panier est vide.")
        except Cart.DoesNotExist:
            messages.error(request, "Vous n'avez pas de panier.")
    else:
        messages.error(request, "Vous devez être connecté pour valider votre commande.")

    return redirect('index')

@login_required
def save_address(request):
    if request.method == "POST":
        adresse = request.POST.get('adresse')
        ville = request.POST.get('ville')
        telephone = request.POST.get('telephone')
        
        if adresse and ville and telephone:
            # Enregistrer l'adresse de livraison
            ShippingAddress.objects.create(user=request.user, adresse=adresse, ville=ville, telephone=telephone)
            #messages.success(request, "Adresse de livraison enregistrée avec succès.")
            # Appeler la vue checkout
            return checkout(request)
        else:
            messages.error(request, "Veuillez remplir tous les champs.")
    return redirect('cart')  # Redirigez l'utilisateur vers le panier en cas d'erreur

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def admin_order(request):
    if request.user.is_authenticated:
        order = Order.objects.all()
        return render(request, 'admin_order.html', context={"orders":order})
    

@login_required
@user_passes_test(is_admin)
def admin_dash(request):
    if request.user.is_authenticated:
        return render(request, 'admin_dash.html')
    

@login_required
@user_passes_test(is_admin)
def produit(request):
    if request.user.is_authenticated:
        produit = Produit.objects.all()
        return render(request, 'produit.html', context={"produits":produit})
    
@login_required
@user_passes_test(is_admin)
def delete_order(request, order_id):
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, id=order_id)
            order.delete()
            messages.success(request, "La commande a été supprimée avec succès.")
        except Order.DoesNotExist:
            messages.error(request, "Cette commande n'existe pas.")
    return redirect('admin_order')

def privacy_policy(request):
    context = {
        'current_year': timezone.now().year,
    }
    return render(request, 'privacy_policy.html', context)





@login_required
def ajouter_produit_vente(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    vente_id = request.session.get('vente_id')

    if not vente_id:
        vente = Vente.objects.create(vendeur=request.user, type_vente='en boutique')
        request.session['vente_id'] = vente.id
    else:
        vente = get_object_or_404(Vente, id=vente_id)

    if request.method == 'POST':
        quantite = int(request.POST.get('quantite'))
        LigneVente.objects.create(
            vente=vente,
            produit=produit,
            quantite=quantite,
            prix_unitaire=produit.prix,
        )
        messages.success(request, "Produit ajouté à la vente.")
        return redirect('catalogue')   # Redirige vers le catalogue pour ajouter d'autres produits

    return render(request, 'ajouter_produit_vente.html', {'produit': produit})


@login_required
def facture_vente(request, vente_id):
    vente = get_object_or_404(Vente, id=vente_id)
    return render(request, 'facture.html', context={'vente': vente})


@login_required
def voir_facture(request):
    vente_id = request.session.get('vente_id')
    if not vente_id:
        messages.error(request, "Aucune vente en cours.")
        return redirect('catalogue')

    vente = get_object_or_404(Vente, id=vente_id)
    
    if request.method == 'POST':
        # Finaliser la vente, comme enregistrer la date, nom du client, etc.
        vente.nom_client = request.POST.get('nom_client')
        vente.save()
        # Nettoyer la session
        del request.session['vente_id']
        messages.success(request, "Vente finalisée avec succès.")
        return redirect(reverse('facture_vente', kwargs={'vente_id': vente.id}))

    return render(request, 'voir_facture.html', {'vente': vente})


def ventes_du_jour(request):
    today = timezone.localdate()  # Date locale du jour
    selected_date_str = request.GET.get('date', today.strftime('%Y-%m-%d'))  # Date sélectionnée ou aujourd'hui par défaut
    
    try:
        selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today  # En cas de date invalide, utiliser la date du jour

    start_of_day = timezone.make_aware(datetime.combine(selected_date, datetime.min.time()))
    end_of_day = timezone.make_aware(datetime.combine(selected_date, datetime.max.time()))

    ventes = Vente.objects.filter(date_vente__range=(start_of_day, end_of_day))
    total_vendu = LigneVente.objects.filter(vente__in=ventes).aggregate(
        total=Sum(F('quantite') * F('prix_unitaire'), output_field=FloatField())
    )['total'] or 0

    context = {
        'ventes': ventes,
        'today': today,
        'selected_date': selected_date,
        'total_vendu': total_vendu,
    }
    return render(request, 'ventes_du_jour.html', context)