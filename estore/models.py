from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


# Create your models here.
class Buyer(models.Model):
    username = models.CharField(max_length=128, verbose_name='用户名')
    password = models.CharField(max_length=256, verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱')
    is_active = models.IntegerField(default=1, verbose_name='是否激活')
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_shopkeeper = models.IntegerField(default=0)
    money = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='买家钱包',default=0)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = '买家信息管理'
        verbose_name_plural = verbose_name

class Address(models.Model):

    recipient = models.CharField(verbose_name='收件人',max_length=128)
    phone = models.CharField(max_length=128,verbose_name='手机号')
    province = models.CharField(verbose_name='省份',max_length=128)
    city = models.CharField(verbose_name='城市',max_length=128)
    detail = models.CharField(verbose_name='详细地址',max_length=128)
    the_buyer = models.ForeignKey('Buyer',on_delete=models.CASCADE)

    class Meta:
        verbose_name = '买家地址管理'
        verbose_name_plural = verbose_name

class Shopkeeper(models.Model):
    username = models.CharField(max_length=128, verbose_name='用户名')
    password = models.CharField(max_length=256, verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱')
    shop_name = models.CharField(max_length=128, blank=True, verbose_name='店铺名')
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    is_active = models.IntegerField(default=1, verbose_name='是否激活')
    is_shopkeeper = models.IntegerField(default=1)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    money = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='卖家钱包',default=0)

    def __str__(self):
        return str(self.username)

    class Meta:
        verbose_name = '卖家信息管理'
        verbose_name_plural = verbose_name


class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    # 包含注册验证和找回验证
    send_type = models.CharField(verbose_name=u"验证码类型", max_length=10,
                                 choices=(("register", u"注册"), ("forget", u"找回密码")))
    send_time = models.DateTimeField(verbose_name=u"发送时间", auto_now_add=True)

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return '{0}({1})'.format(self.code, self.email)


class Goods(models.Model):
    title = models.CharField(max_length=128,verbose_name='商品名')
    description = RichTextUploadingField(verbose_name='商品详情',blank=True)
    price = models.FloatField(verbose_name='商品价格')
    picture = models.ImageField(upload_to='avatar/%Y%m%d/',verbose_name='商品封面图')
    choice=(
        (0,'百货'),
        (1,'女装'),
        (2,'男装'),
        (3,'母婴'),
        (4,'美妆'),
        (5,'食品'),
        (6,'鞋包'),
        (7,'家纺'),
        (8,'运动'),
        (9,'书籍')
    )
    category = models.IntegerField(verbose_name='商品类别',choices=choice,default=0)
    is_selling = models.IntegerField(verbose_name='是否上架',default=0)
    the_shopkeeper = models.ForeignKey('Shopkeeper',on_delete=models.CASCADE,verbose_name='所属店铺')
    stock = models.IntegerField(default=1, verbose_name='商品库存')
    sales = models.IntegerField(default=0, verbose_name='商品销量')

    def __str__(self):
        return str(self.title)
    class Meta:
        verbose_name = '商品信息管理'
        verbose_name_plural = verbose_name

class Comments(models.Model):
    content = models.TextField(verbose_name='评论内容',blank=True)
    comment_time = models.DateTimeField(auto_now_add=True,verbose_name='评论时间')
    commenter = models.CharField(max_length=128,verbose_name='评论人',blank=True)
    reply = models.TextField(verbose_name='回复',blank=True)
    the_goods = models.ForeignKey('Goods',on_delete=models.CASCADE)

    def __str__(self):
        return str(self.content)
    class Meta:
        verbose_name = '商品评论'
        verbose_name_plural = verbose_name

class ShoppingCar(models.Model):
    the_goods = models.ForeignKey('Goods',on_delete=models.CASCADE,verbose_name='商品')
    the_buyer = models.ForeignKey('Buyer',on_delete=models.CASCADE,verbose_name='买家',default='')

    def __str__(self):
        return str(self.the_goods)
    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成')
    )

    goods = models.ForeignKey('Goods',verbose_name='商品',on_delete=models.CASCADE)
    goods_title = models.CharField(max_length=128, verbose_name='商品名')
    goods_price = models.FloatField(verbose_name='商品价格')
    goods_picture = models.ImageField(upload_to='avatar/%Y%m%d/', verbose_name='商品封面图')
    buyer = models.ForeignKey('Buyer', verbose_name='买家',on_delete=models.CASCADE)
    address = models.ForeignKey('Address', verbose_name='地址',on_delete=models.CASCADE)
    total_count = models.IntegerField(default=1, verbose_name='商品数量')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name='订单状态')
    creat_time = models.DateTimeField(auto_now_add=True,verbose_name='订单生成时间')
    shop_action = models.IntegerField(default=1,verbose_name='店家操作')
    def __str__(self):
        return str(self.buyer)
    class Meta:
        verbose_name = '订单信息'
        verbose_name_plural = verbose_name
