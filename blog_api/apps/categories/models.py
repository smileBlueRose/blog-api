from autoslug import AutoSlugField

from django.db.models import CharField, Model


class Category(Model):
    name = CharField(max_length=100, null=False)
    slug = AutoSlugField(populate_from="name", unique=True, null=False)

    class Meta:
        db_table = "categories"
        verbose_name = "category"
        verbose_name_plural = "categories"
