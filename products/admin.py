from django.contrib import admin
from .models import Category, Product, ProductImage, Variant, Banner, BannerImage

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

# Inline for BannerImage
class BannerImageInline(admin.TabularInline):
    model = BannerImage
    extra = 1  # Number of empty forms to display
    fields = ['image', 'order', 'img_preview']
    readonly_fields = ['img_preview']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    search_fields = ['name']
    list_filter = ['parent']
    ordering = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'stock', 'sku', 'brand']
    search_fields = ['name', 'sku', 'brand']
    list_filter = ['category', 'brand']
    inlines = [ProductImageInline, VariantInline]  # Add inlines for ProductImage and Variant
    ordering = ['name']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'img_preview']
    search_fields = ['product__name']
    readonly_fields = ['img_preview']
    list_filter = ['product']
    ordering = ['product']

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock']
    search_fields = ['product__name', 'size', 'color']
    list_filter = ['size', 'color']
    ordering = ['product']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at', 'updated_at']
    search_fields = ['title', 'description']
    list_filter = ['is_active', 'created_at']
    inlines = [BannerImageInline]  # Add inline for BannerImage
    ordering = ['-created_at']

@admin.register(BannerImage)
class BannerImageAdmin(admin.ModelAdmin):
    list_display = ['banner', 'image', 'order', 'img_preview']
    search_fields = ['banner__title']
    list_filter = ['banner']
    readonly_fields = ['img_preview']
    ordering = ['banner', 'order']