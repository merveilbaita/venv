# Generated by Django 5.0.7 on 2024-08-25 13:36

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_vente_nom_client_vente_numero_vente'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vente',
            name='prix_unitaire',
        ),
        migrations.RemoveField(
            model_name='vente',
            name='produit',
        ),
        migrations.RemoveField(
            model_name='vente',
            name='quantite',
        ),
        migrations.RemoveField(
            model_name='vente',
            name='total',
        ),
        migrations.AlterField(
            model_name='vente',
            name='numero_vente',
            field=models.CharField(default=uuid.uuid4, max_length=100, unique=True),
        ),
        migrations.CreateModel(
            name='LigneVente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.IntegerField()),
                ('prix_unitaire', models.IntegerField()),
                ('produit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shop.produit')),
                ('vente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='shop.vente')),
            ],
        ),
    ]
