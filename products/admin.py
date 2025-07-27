from django.contrib import admin
from .models import Category, Product, ProductImage, Variant

# Inline for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display
    fields = ['image', 'img_preview']
    readonly_fields = ['img_preview']

# Inline for Variant
class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1  # Number of empty forms to display
    fields = ['size', 'color', 'stock']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'sku', 'brand']
    search_fields = ['name', 'sku', 'brand']
    list_filter = ['category', 'brand']
    inlines = [ProductImageInline, VariantInline]  # Add inlines for ProductImage and Variant

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