from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem


admin.site.site_header = 'Storefront Administration'
admin.site.site_title = 'Storefront Admin'
admin.site.index_title = 'Store Overview'
admin.site.index_template = 'admin/index.html'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['unit_price']
    min_num = 1
    verbose_name_plural = 'Order items'


@admin.action(description='Mark selected products as active')
def make_active(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f'{updated} product(s) marked active.')


@admin.action(description='Mark selected products as inactive')
def make_inactive(modeladmin, request, queryset):
    updated = queryset.update(is_active=False)
    modeladmin.message_user(request, f'{updated} product(s) marked inactive.')


@admin.action(description='Mark selected orders as shipped')
def mark_shipped(modeladmin, request, queryset):
    updated = queryset.update(status='shipped')
    modeladmin.message_user(request, f'{updated} order(s) marked shipped.')


@admin.action(description='Mark selected orders as cancelled')
def mark_cancelled(modeladmin, request, queryset):
    updated = queryset.update(status='cancelled')
    modeladmin.message_user(request, f'{updated} order(s) marked cancelled.')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25
    ordering = ['name']
    fields = ['name', 'slug']
    readonly_fields = ['product_count']

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Products'

    class Media:
        css = {'all': ('store/admin.css',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'price', 'inventory', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'inventory', 'is_active']
    list_select_related = ['category']
    autocomplete_fields = ['category']
    ordering = ['name']
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'category', 'description')}),
        ('Inventory & pricing', {'fields': ('price', 'inventory', 'is_active')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at']
    actions = [make_active, make_inactive]

    class Media:
        css = {'all': ('store/admin.css',)}

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge badge-success">Active</span>')
        return format_html('<span class="badge badge-muted">Inactive</span>')

    active_badge.short_description = 'Status'
    active_badge.admin_order_field = 'is_active'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email']
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    actions = [mark_shipped, mark_cancelled]
    readonly_fields = ['created_at']
    fieldsets = (
        (None, {'fields': ('customer_name', 'customer_email', 'status')}),
        ('Order details', {'fields': ('created_at',)}),
    )

    class Media:
        css = {'all': ('store/admin.css',)}

    def status_badge(self, obj):
        color_map = {
            'draft': 'badge-muted',
            'paid': 'badge-primary',
            'shipped': 'badge-success',
            'cancelled': 'badge-danger',
        }
        cls = color_map.get(obj.status, 'badge-muted')
        return format_html('<span class="badge {0}">{1}</span>', cls, obj.get_status_display())

    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
