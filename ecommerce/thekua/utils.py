import random
from django.utils.text import slugify


def generate_otp():
    return str(random.randint(100000,999999))

def send_otp(destination,otp):
    print(f"OTP sent to {destination}: {otp}")

def generate_unique_slug(model_class, value, slug_field="slug"):
    base_slug = slugify(value)
    slug = base_slug
    count = 1

    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{count}"
        count += 1

    return slug