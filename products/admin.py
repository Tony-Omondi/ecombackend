from django.contrib import admin
from .models import Category, Product, ProductImage, Variant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'sku', 'brand']
    search_fields = ['name', 'sku', 'brand']
    list_filter = ['category', 'brand']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'img_preview']
    search_fields = ['product__name']
    readonly_fields = ['img_preview']

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock']
    search_fields = ['product__name', 'size', 'color']
    list_filter = ['size', 'color']