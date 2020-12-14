from django.contrib import admin

# Register your models here.
from .models import Goods,Buyer,Shopkeeper

class CategoryFilter(admin.SimpleListFilter):
    title = "商品种类"
    parameter_name = 'category'
    def lookups(self, request, model_admin):
        return (
            (0, '百货'),
            (1, '女装'),
            (2, '男装'),
            (3, '母婴'),
            (4, '美妆'),
            (5, '食品'),
            (6, '鞋包'),
            (7, '家纺'),
            (8, '运动'),
            (9, '书籍')
        )
    def queryset(self, request, queryset):
        if self.value() in ['0','1','2','3','4','5','6','7','8','9']:
            return queryset.filter(category =self.value())
class IsSellingFilter(admin.SimpleListFilter):
    title = '是否上架'
    parameter_name = 'is_selling_or_not'
    def lookups(self, request, model_admin):
        return (
            ('1','已上架'),
            ('0','待上架')
        )
    def queryset(self, request, queryset):
        if self.value() in ['0','1']:
            return queryset.filter(is_selling =self.value())

@admin.register(Goods)
class Goods(admin.ModelAdmin):
    list_display = ['title','price','the_shopkeeper']
    search_fields = ('title',)
    actions_selection_counter = True
    list_filter = (CategoryFilter,IsSellingFilter)
    actions = ['is_selling0','is_selling1']

    def is_selling0(self,request,queryset):
        row_updated = queryset.update(is_selling=1)
        self.message_user(request, '修改了{}条字段'.format(row_updated))
    is_selling0.short_description = '上架商品'

    def is_selling1(self,request,queryset):
        row_updated = queryset.update(is_selling=0)
        self.message_user(request, '修改了{}条字段'.format(row_updated))
    is_selling1.short_description = '下架商品'

class ActiveFilter(admin.SimpleListFilter):

    title = '是否激活'
    parameter_name = 'is_active_or_not'
    def lookups(self, request, model_admin):
        return (
            ('1','已激活'),
            ('0','未激活')
        )
    def queryset(self, request, queryset):
        if self.value() in ['0','1']:
            return queryset.filter(is_active =self.value())


@admin.register(Buyer)
class Buyer(admin.ModelAdmin):
    list_display = ['username','email']
    search_fields = ('username',)
    actions_selection_counter = True
    list_filter = (ActiveFilter,)
    actions = ['is_active0', 'is_active1','no_money']

    def is_active0(self, request, queryset):
        row_updated = queryset.update(is_active=0)
        self.message_user(request, '修改了{}条字段'.format(row_updated))

    is_active0.short_description = '冻结账号'

    def is_active1(self, request, queryset):
        row_updated = queryset.update(is_active=1)
        self.message_user(request, '修改了{}条字段'.format(row_updated))

    is_active1.short_description = '激活账号'

    def no_money(self, request, queryset):
        row_updated = queryset.update(money=0)
        self.message_user(request, '修改了{}条字段'.format(row_updated))

    no_money.short_description = '冻结资金'

@admin.register(Shopkeeper)
class Shopkeeper(admin.ModelAdmin):
    list_display = ['username', 'email','shop_name']
    search_fields = ('username',)
    actions_selection_counter = True
    list_filter = (ActiveFilter,)
    actions = ['is_active0', 'is_active1','no_money']

    def is_active0(self, request, queryset):
        row_updated = queryset.update(is_active=0)
        self.message_user(request, '修改了{}条字段'.format(row_updated))

    is_active0.short_description = '冻结账号'

    def is_active1(self, request, queryset):
        row_updated = queryset.update(is_active=1)
        self.message_user(request, '修改了{}条字段'.format(row_updated))

    is_active1.short_description = '激活账号'

    def no_money(self, request, queryset):
        row_updated = queryset.update(money=0)
        self.message_user(request, '修改了{}条字段'.format(row_updated))

    no_money.short_description = '冻结资金'


# admin.site.register(Goods)