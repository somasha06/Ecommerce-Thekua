from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from thekua.models import Role, Category, SubCategory, Product, ProductVariant
from django.utils.text import slugify
from decimal import Decimal
import random
import os
from django.core.files import File
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with products and images'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database with images...')

        # 1. Setup default users
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin')
        admin_user.save()
        Role.objects.get_or_create(user=admin_user, role=Role.ADMIN, active=True)
        
        seller_user, _ = User.objects.get_or_create(
            username='thekua_brand',
            defaults={'email': 'brand@thekua.com'}
        )
        seller_user.set_password('password123')
        seller_user.save()
        Role.objects.get_or_create(user=seller_user, role=Role.SELLER, active=True)

        # 2. Define data structure with Images
        # Map generic filenames to the actual files we copied
        # project_root/seed_source/filename.png
        SOURCE_DIR = os.path.join(settings.BASE_DIR, 'seed_source')

        categories_data = {
            "Traditional Sweets": {
                "subcats": ["Thekua Special", "Laddoo Varieties", "Barfi & Kalakand"],
                "products": [
                    {
                        "name": "Classic Jaggery Thekua",
                        "sub": "Thekua Special",
                        "desc": "Authentic Bihari style Thekua made with organic jaggery (gud), whole wheat flour, and pure ghee.",
                        "price": "399.00",
                        "weight": "500g",
                        "image": "classic.png"
                    },
                    {
                        "name": "Dry Fruit Stuffed Thekua",
                        "sub": "Thekua Special",
                        "desc": "A premium twist on the classic! Enriched with cashews, almonds, and raisins.",
                        "price": "549.00",
                        "weight": "400g",
                        "image": "dryfruit.png"
                    },
                     {
                        "name": "Sugar-Free Multigrain Thekua",
                        "sub": "Thekua Special",
                        "desc": "Guilt-free indulgence. Made with 5 supergrains and natural sweeteners.",
                        "price": "499.00",
                        "weight": "400g",
                        "image": "multigrain.png"
                    },
                     {
                        "name": "Mini Thekua Bites",
                        "sub": "Thekua Special",
                        "desc": "Bite-sized delights perfect for tea time snacking.",
                        "price": "249.00",
                        "weight": "250g",
                        "image": "mini.png"
                    },
                    {
                        "name": "Besan Ghee Laddoo",
                        "sub": "Laddoo Varieties",
                        "desc": "Melt-in-mouth Besan Laddoos made with pure cow ghee and premium gram flour.",
                        "price": "450.00",
                        "weight": "500g",
                        "image": "laddoo.png"
                    }

                ]
            },
            "Healthy Snacks": {
                "subcats": ["Dry Fruit Bites", "Roasted Namkeen", "Fox Nut (Makhana)"],
                "products": []
            },
             "Festive Packs": {
                "subcats": ["Wedding Boxes", "Diwali Hampers", "Corporate Gifts"],
                "products": []
            }
        }

        for cat_name, data in categories_data.items():
            category, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})
            
            for sub_name in data["subcats"]:
                SubCategory.objects.get_or_create(
                    category=category,
                    name=sub_name,
                    defaults={'slug': slugify(sub_name)}
                )
            
            # Create Products
            for p in data["products"]:
                sub = SubCategory.objects.filter(name=p["sub"]).first()
                if sub:
                    product, created = Product.objects.get_or_create(
                        name=p["name"],
                        subcategory=sub,
                        defaults={
                            "description": p["desc"],
                            "seller": seller_user,
                            "starting_from": p["price"],
                            "is_active": True,
                            "slug": slugify(p["name"])
                        }
                    )

                    # Handle Image Upload
                    if p["image"]:
                        image_path = os.path.join(SOURCE_DIR, p["image"])
                        if os.path.exists(image_path):
                            with open(image_path, 'rb') as f:
                                product.image.save(p["image"], File(f), save=True)
                                self.stdout.write(f"Attached image to {p['name']}")
                    
                    if created:
                        ProductVariant.objects.create(
                            product=product,
                            weight=p["weight"],
                            price=Decimal(p["price"]),
                            stock=100,
                            sku=random.randint(10000, 99999),
                            is_active=True
                        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded data with images!'))
