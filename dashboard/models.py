from django.db import models


class Banner(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(
        blank=True
    )

    image = models.ImageField(
        upload_to="banners/"
    )

    button_text = models.CharField(
        max_length=50,
        default="Shop Now"
    )

    button_link = models.CharField(
        max_length=200,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title



class InstagramPost(models.Model):

    image = models.ImageField(
        upload_to="instagram/"
    )

    caption = models.TextField(
        blank=True
    )

    link = models.URLField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )


    def __str__(self):
        return self.caption[:30]



class Offer(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    discount = models.CharField(
        max_length=50
    )

    image = models.ImageField(
        upload_to="offers/",
        blank=True,
        null=True
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):
        return self.title