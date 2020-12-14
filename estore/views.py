from django.shortcuts import render, redirect
from .forms import UserForm, RegisterForm, ForgetForm, AvatarForm, GoodsForm, DescriptionForm
from estore.models import Buyer, Shopkeeper, EmailVerifyRecord, Address, Goods, ShoppingCar, Order, Comments
from OnlineStore.settings import EMAIL_FROM
from random import Random
from django.core.mail import send_mail
from django.http import HttpResponse
from django.db.models import Q, Avg
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage


# Create your views here.
def index(request):
    if request.session.get('is_login'):
        username = request.session.get('user_name')
        try:
            user = Buyer.objects.get(username=username)
        except:
            user = Shopkeeper.objects.get(username=username)
        avg_sales = Goods.objects.aggregate(Avg('sales'))
        recommand = Goods.objects.filter(sales__gt=avg_sales['sales__avg'], is_selling=1, stock__gt=0)
        paginator = Paginator(recommand, 1)
        if request.method == "GET":
            page = request.GET.get('page')
            try:
                recommand = paginator.page(page)
            except (PageNotAnInteger, InvalidPage, EmptyPage):
                # 有错误, 返回第一页。
                recommand = paginator.page(1)
        return render(request, 'index.html', locals())
    else:
        return render(request, 'index.html')


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        username = request.POST.get('username1')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        position = request.POST.get('position')
        if not position:
            position = 1
        request.session['position'] = position
        if register_form.is_valid():
            email = register_form.cleaned_data['email']
            if password1 != password2:
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                if len(username) > 20:
                    message = '用户名过长!'
                    return render(request, 'register.html', locals())
                else:
                    if len(password1) < 4:
                        message = '密码少于四个字符！'
                        return render(request, 'register.html', locals())
                    else:
                        import string
                        s = string.digits + string.ascii_letters + string.punctuation
                        for i in password1:
                            if i not in s:
                                message = '密码中有不符合规范的字符！'
                                return render(request, 'register.html', locals())
                        for i in username:
                            if i not in s:
                                message = '用户名中有不符合规范的字符！'
                                return render(request, 'register.html', locals())
                        else:
                            same_buyer_username = Buyer.objects.filter(username=username)
                            same_buyer_email = Buyer.objects.filter(email=email)
                            same_shopkeeper_username = Shopkeeper.objects.filter(username=username)
                            same_shopkeeper_email = Shopkeeper.objects.filter(email=email)
                            if same_buyer_username or same_shopkeeper_username:
                                message = '用户已经存在，请重新选择用户名！'
                                return render(request, 'register.html', locals())
                            if same_buyer_email or same_shopkeeper_email:
                                message = '该邮箱已被注册！'
                                return render(request, 'register.html', locals())

                            if position == 'buyer':
                                new_user = Buyer.objects.create()
                            else:
                                new_user = Shopkeeper.objects.create()
                            new_user.username = username
                            new_user.password = password1
                            new_user.email = email
                            new_user.is_active = 0
                            new_user.save()
                            send_email_code(email, 'register')
                            return HttpResponse('请前往邮箱验证!')
        else:
            error = register_form.errors
            return render(request, 'register.html', locals())
    register_form = RegisterForm()
    return render(request, 'register.html', locals())


def login(request):
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = Buyer.objects.filter(username=username)  # Buyer or not?
            if not user:
                user = Shopkeeper.objects.filter(username=username)  # if not, find it in Shopkeeper
            if user:
                user = user[0]
                if user.is_active == 0:
                    message = '您尚未激活，请前往邮箱验证!'
                    email = user.email
                    send_email_code(email, 'register')
                    return render(request, 'login.html', locals())
                else:
                    if user.password == password:
                        request.session['is_login'] = True
                        request.session['user_id'] = user.id
                        request.session['user_name'] = user.username
                        return redirect('index')
                    else:
                        message = '密码输入错误！'
                        return render(request, 'login.html', locals())
            else:
                message = '用户名不存在！'
                return render(request, 'login.html', locals())
        else:
            error = login_form.errors
            return render(request, 'login.html', locals())
    login_form = UserForm()
    return render(request, 'login.html', locals())


def logout(request):
    if not request.session.get('is_login', None):
        return redirect("index")
    else:
        request.session.flush()
        return redirect('index')


def random_str(randomlength=8):
    randomstr = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        randomstr += chars[random.randint(0, length)]
    return randomstr


def send_email_code(email, send_type):
    code = random_str()
    email_record = EmailVerifyRecord()
    # 将给用户发的信息保存在数据库中
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    send_title = ''
    send_body = ''
    # 如果为注册类型
    if send_type == "register":
        send_title = "注册激活链接"
        send_body = "请点击下面的链接激活你的账号:http://127.0.0.1:8000/estore/activate/{0}".format(code)
        # 发送邮件
        send_mail(send_title, send_body, EMAIL_FROM, [email])
    if send_type == 'forget':
        send_title = "重置密码链接"
        send_body = "请点击下面的链接重置密码:http://127.0.0.1:8000/estore/reset_password/{0}".format(code)
        # 发送邮件
        send_mail(send_title, send_body, EMAIL_FROM, [email])


def activate(request, code):
    if code:
        email_ver_list = EmailVerifyRecord.objects.filter(code=code)
        if email_ver_list:
            email_ver = email_ver_list[0]
            email = email_ver.email
            try:
                user = Buyer.objects.get(email=email)
            except:
                user = Shopkeeper.objects.get(email=email)
            user.is_active = 1
            user.save()
            return redirect('login')


def buyer_center(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    if request.method == "POST":
        avatar_form = AvatarForm(request.POST, request.FILES)
        if avatar_form.is_valid():
            avatar = avatar_form.cleaned_data['avatar']
            user.avatar = avatar
            user.save()
            return redirect('buyer_center')
        else:
            error = avatar_form.errors
            return render(request, 'buyer_center.html', locals())
    avatar_form = AvatarForm()
    user_dict = {'user': user}
    address = user.address_set.all()
    return render(request, 'buyer_center.html', locals())


def shop_center(request):
    username = request.session.get('user_name')
    user = Shopkeeper.objects.get(username=username)
    user_dict = {'user': user}
    return render(request, 'shop_center.html', locals())


def editing(request):
    username = request.session.get('user_name')
    user = Shopkeeper.objects.get(username=username)
    if request.method == "POST":
        avatar_form = AvatarForm(request.POST, request.FILES)
        shop_name = request.POST.get('shop_name')
        if avatar_form.is_valid():
            avatar = avatar_form.cleaned_data['avatar']
            if shop_name:
                user.shop_name = shop_name
            if avatar:
                user.avatar = avatar
            user.save()
            return redirect('shop_center')
        else:
            error = avatar_form.errors
            return render(request, 'editing.html', locals())
    avatar_form = AvatarForm()
    return render(request, 'editing.html')


def add_address(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        phone = request.POST.get('phone')
        province = request.POST.get('province')
        city = request.POST.get('city')
        detail = request.POST.get('detail')
        if recipient and phone and province and city and detail:
            import re
            phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
            res = re.search(phone_pat, phone)
            if not res:
                message = '手机号格式错误！'
                return render(request, 'add_address.html', locals())
            try:
                new_address = Address.objects.get(the_buyer=user)
                new_address.recipient = recipient
                new_address.phone = phone
                new_address.province = province
                new_address.city = city
                new_address.detail = detail
                new_address.save()
            except:
                new_address = Address.objects.create(recipient=recipient, phone=phone,
                                                     province=province, city=city, detail=detail, the_buyer=user)
            return redirect('buyer_center')
        else:
            message = '填写内容不能为空！'
            return render(request, 'add_address.html', locals())

    else:
        return render(request, 'add_address.html')


def change_password(request):
    username = request.session.get('user_name')
    try:
        user = Buyer.objects.get(username=username)
    except:
        user = Shopkeeper.objects.get(username=username)
    user_dict = {'user': user}
    real_password = user.password
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        if old_password == '' or new_password1 == '' or new_password2 == '':
            message = '填写内容不能为空！'
            return render(request, 'change_password.html', locals())
        else:
            if new_password2 != new_password1:
                message = '两次密码不相同！'
                return render(request, 'change_password.html', locals())
            else:
                if len(new_password1) < 4:
                    message = '密码少于四个字符！'
                    return render(request, 'change_password.html', locals())
                else:
                    import string
                    s = string.digits + string.ascii_letters + string.punctuation
                    for i in new_password1:
                        if i not in s:
                            message = '密码中有不符合规范的字符！'
                            return render(request, 'change_password.html', locals())
                    else:
                        if old_password != real_password:
                            message = '旧密码填写错误！'
                            return render(request, 'change_password.html', locals())
                        else:
                            user.password = new_password1
                            user.save()
                            if user.is_shopkeeper:
                                return redirect('shop_center')
                            else:
                                return redirect('buyer_center')
    else:
        return render(request, 'change_password.html', locals())


def forget_password(request):
    if request.method == 'POST':
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = forget_form.cleaned_data['email']
            user = Buyer.objects.filter(email=email)
            if not user:
                user = Shopkeeper.objects.filter(email=email)

            if user:
                send_email_code(email, 'forget')
                return HttpResponse('请前往邮箱验证！')
            else:
                message = '该邮箱尚未注册！'
                return render(request, 'forget_password.html', locals())
        else:
            error = forget_form.errors
            return render(request, 'forget_password.html', locals())
    forget_form = ForgetForm()
    return render(request, 'forget_password.html', locals())


def reset_password(request, code):
    if code:
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 != password2:
                message = '两次输入的密码不相同！'
                return render(request, 'reset_password.html', locals())
            else:
                if len(password1) < 4:
                    message = '密码少于四个字符！'
                    return render(request, 'reset_password.html', locals())
                else:
                    import string
                    s = string.digits + string.ascii_letters + string.punctuation
                    for i in password1:
                        if i not in s:
                            message = '密码中有不符合规范的字符！'
                            return render(request, 'reset_password.html', locals())
                    else:
                        email_ver_list = EmailVerifyRecord.objects.filter(code=code)
                        if email_ver_list:
                            email_ver = email_ver_list[0]
                            email = email_ver.email
                            try:
                                user = Buyer.objects.get(email=email)
                            except:
                                user = Shopkeeper.objects.get(email=email)
                            user.password = password1
                            user.save()
                            return redirect('login')
        else:
            return render(request, 'reset_password.html', locals())


def manage_goods(request):
    username = request.session.get('user_name')
    user = Shopkeeper.objects.get(username=username)
    # is_selling_goods = Goods.objects.filter(the_shopkeeper=user, is_selling=1)
    # is_not_selling_goods = Goods.objects.filter(the_shopkeeper=user, is_selling=0)
    all_goods = Goods.objects.filter(the_shopkeeper=user)
    paginator = Paginator(all_goods, 3)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            all_goods = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            all_goods = paginator.page(1)

    return render(request, 'manage_goods.html', locals())


def add_goods(request):
    username = request.session.get('user_name')
    user = Shopkeeper.objects.get(username=username)
    if request.method == 'POST':
        category = request.POST.get('category')
        price = request.POST.get('price')
        goods_form = GoodsForm(request.POST, request.FILES)
        if goods_form.is_valid():
            description = goods_form.cleaned_data['description']
            title = goods_form.cleaned_data['title']
            description = goods_form.cleaned_data['description']
            picture = goods_form.cleaned_data['picture']
            stock = goods_form.cleaned_data['stock']
            Goods.objects.create(title=title, description=description, price=price,
                                 picture=picture, the_shopkeeper=user, category=category, stock=stock)
            return redirect('manage_goods')
        else:
            error = goods_form.errors
            return render(request, 'add_goods.html', locals())
    goods_form = GoodsForm()
    return render(request, 'add_goods.html', locals())


def check_goods(request, id):
    username = request.session.get('user_name')
    try:
        user = Shopkeeper.objects.get(username=username)
    except:
        user = Buyer.objects.get(username=username)
    try:
        the_goods = Goods.objects.get(id=id)
        if the_goods.is_selling == 0:
            message = '该商品已下架！'
    except:
        message = '该商品不见了~'
    flag = ShoppingCar.objects.filter(the_buyer=user,the_goods_id=id)
    if request.method == "POST":
        ShoppingCar.objects.create(the_goods_id=id, the_buyer=user)
        message = '成功加入购物车!'
    return render(request, 'check_goods.html', locals())


def delete_goods(request, id):
    the_goods = Goods.objects.get(id=id)
    the_goods.delete()
    return redirect('manage_goods')


def is_selling(request, id):
    the_goods = Goods.objects.get(id=id)
    the_goods.is_selling = 1
    the_goods.save()
    return redirect('manage_goods')


def is_not_selling(request, id):
    the_goods = Goods.objects.get(id=id)
    the_goods.is_selling = 0
    the_goods.save()
    return redirect('manage_goods')


def edit_goods(request, id):
    the_goods = Goods.objects.get(id=id)

    # old_description = the_goods.description
    # old_title = the_goods.title
    # old_picture = the_goods.picture
    # old_price = the_goods.price
    # old_stock = the_goods.stock

    if request.method == "POST":
        picture_form = AvatarForm(request.POST, request.FILES)
        description_form = DescriptionForm(request.POST,request.FILES)
        price = request.POST.get('price')
        title = request.POST.get('title')
        stock = request.POST.get('stock')
        if price:
            if float(price)<0:
                message = '商品价格不能小于零'
                return render(request, 'edit_goods.html', locals())
            the_goods.price = price
        if title:
            the_goods.title = title
        if stock:
            if float(stock)<0:
                message = '商品库存不能小于零'
                return render(request, 'edit_goods.html', locals())
            stock = int(float(stock))
            the_goods.stock = stock
        the_goods.save()

        if  picture_form.is_valid():
            picture = picture_form.cleaned_data['avatar']
            if picture:
                the_goods.picture = picture
                the_goods.save()
        else:
            picture_errors = picture_form.errors
            return render(request, 'edit_goods.html', locals())
        if description_form.is_valid():
            description = description_form.cleaned_data['description']
            the_goods.description = description
            the_goods.save()
            return redirect('manage_goods')
        else:
            edit_errors = description_form.errors
            return render(request, 'edit_goods.html', locals())
    description_form = DescriptionForm()
    picture_form = AvatarForm()
    return render(request, 'edit_goods.html', locals())


def category(request, num):
    the_category = Goods.objects.filter(category=num, is_selling=1)
    paginator = Paginator(the_category, 6)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            the_category = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            the_category = paginator.page(1)
    return render(request, 'category.html', locals())


def shopping_car(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    shopping_car_goods = ShoppingCar.objects.filter(the_buyer=user)
    paginator = Paginator(shopping_car_goods, 3)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            shopping_car_goods = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            shopping_car_goods = paginator.page(1)
    return render(request, 'shopping_car.html', locals())


def delete_shopping_car(request, id):
    the_goods = ShoppingCar.objects.get(id=id)
    the_goods.delete()
    return redirect('shopping_car')


def my_money(request):
    username = request.session.get('user_name')
    try:
        user = Buyer.objects.get(username=username)
    except:
        user = Shopkeeper.objects.get(username=username)
    if request.method == 'POST':
        add_money = request.POST.get('add_money')
        if float(add_money) <= 0:
            message = '数值不符合规范！'
            return render(request, 'my_money.html', locals())
        if float(add_money)>10000:
            message = '一次充值次数不能大于一万！'
            return render(request, 'my_money.html', locals())
        else:
            money = user.money
            whole_money = float(money) + float(add_money)
            user.money = whole_money
            user.save()
            message = '充值成功！'
            return render(request, 'my_money.html', locals())

    return render(request, 'my_money.html', locals())


def buying(request, id):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    goods = Goods.objects.get(id=id)
    price = goods.price
    if not Address.objects.filter(the_buyer=user):
        message = '您尚未填写收货地址！'
        return render(request, 'buying.html', locals())
    else:
        address = Address.objects.get(the_buyer=user)
    if request.method == "POST":
        count = request.POST.get('count')
        count = float(count)
        count = round(count)
        if int(count) <= 0:
            message = '商品数量必须大于0！'
            return render(request, 'buying.html', locals())
        else:
            if int(count)>goods.stock:
                message = '购买失败，商品库存量小于您所需数量！'
                return render(request, 'buying.html', locals())
            order = Order.objects.create(total_count=count, total_price=(int(count) * price),
                                         address=address, goods=goods, buyer=user, order_status=1,
                                         goods_picture=goods.picture, goods_title=goods.title, goods_price=goods.price)

            return redirect('create_order', order.id)

    else:
        return render(request, 'buying.html', locals())


def create_order(request, id):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    whole_money = user.money
    order = Order.objects.get(id=id)
    goods = order.goods
    shopkeeper = order.goods.the_shopkeeper
    total_price = order.total_price
    if request.method == "POST":
        if float(whole_money) < float(total_price):
            message = '余额不足！'
        else:
            goods.sales += 1
            goods.save()
            left_money = float(whole_money) - float(total_price)
            user.money = left_money
            user.save()
            shopkeeper.money += total_price
            shopkeeper.save()
            order.order_status = 2
            order.save()
            message = '支付成功！您可在我的订单页面查看订单详情。'
    return render(request, 'create_order.html', locals())


def my_order(request):
    username = request.session.get('user_name')
    try:
        user = Buyer.objects.get(username=username)
    except:
        user = Shopkeeper.objects.get(username=username)
    return render(request, 'my_order.html', locals())


def waiting_for_paying(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    no_pay = Order.objects.filter(buyer=user, order_status=1)
    paginator = Paginator(no_pay, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            no_pay = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            no_pay = paginator.page(1)
    return render(request, 'waiting_for_paying.html', locals())


def waiting_for_sending(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    no_send = Order.objects.filter(buyer=user, order_status=2)
    paginator = Paginator(no_send, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            no_send = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            no_send = paginator.page(1)
    return render(request, 'waiting_for_sending.html', locals())


def waiting_for_receiving(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    no_receive = Order.objects.filter(buyer=user, order_status=3)
    paginator = Paginator(no_receive, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            no_receive = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            no_receive = paginator.page(1)
    return render(request, 'waiting_for_receiving.html', locals())


def waiting_for_comment(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    no_comment = Order.objects.filter(buyer=user, order_status=4)
    paginator = Paginator(no_comment, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            no_comment = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            no_comment = paginator.page(1)
    return render(request, 'waiting_for_comment.html', locals())


def done(request):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    done = Order.objects.filter(buyer=user, order_status=5)
    paginator = Paginator(done, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            done = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            done = paginator.page(1)
    return render(request, 'done.html', locals())


def check_shop(request, id):
    all_goods = Goods.objects.filter(the_shopkeeper_id=id, is_selling=1)
    paginator = Paginator(all_goods, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            all_goods = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            all_goods = paginator.page(1)
    return render(request, 'check_shop.html', locals())


def check_order(request, id):
    order = Order.objects.get(id=id)
    goods = order.goods
    username = request.session.get('user_name')
    try:
        user = Buyer.objects.get(username=username)
    except:
        user = Shopkeeper.objects.get(username=username)
    if request.method == "POST":
        if user.is_shopkeeper:
            action = request.POST.get('action')
            if action == "1":
                order.order_status = 3
                order.save()
                goods.stock -= 1
                goods.save()
                message = '发货成功！您可在已处理订单中查看详情。'
            else:
                order.shop_action = 0
                order.save()
                message = '该订单已被拒绝！'
        else:
            order.order_status = 4
            order.save()
            message = ' 确认收货成功！'
    return render(request, 'check_order.html', locals())


def delete_order(request, id):
    username = request.session.get('user_name')
    user = Buyer.objects.get(username=username)
    order = Order.objects.get(id=id)
    shopkeeper = order.goods.the_shopkeeper
    if order.order_status == 2:
        total_price = order.total_price
        left_money = user.money
        user.money = float(total_price) + float(left_money)
        user.save()
        shop_money = shopkeeper.money
        shopkeeper.money = float(shop_money) - float(total_price)
        shopkeeper.save()
    order.delete()
    return redirect('my_order')


def waiting_for_dispose(request):
    username = request.session.get('user_name')
    user = Shopkeeper.objects.get(username=username)
    no_dispose = Order.objects.filter(Q(goods__the_shopkeeper=user, order_status=2) &
                                      Q(goods__the_shopkeeper=user, shop_action=1))
    paginator = Paginator(no_dispose, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            no_dispose = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            no_dispose = paginator.page(1)
    return render(request, 'waiting_for_dispose.html', locals())


def have_disposed(request):
    username = request.session.get('user_name')
    user = Shopkeeper.objects.get(username=username)
    have_disposed = Order.objects.filter(Q(goods__the_shopkeeper=user, order_status__gt=2)
                                         | Q(goods__the_shopkeeper=user, shop_action=0))
    paginator = Paginator(have_disposed, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            have_disposed = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            have_disposed = paginator.page(1)
    return render(request, 'have_disposed.html', locals())


def make_comment(request, id):
    username = request.session.get('user_name')
    try:
        user = Shopkeeper.objects.get(username=username)
    except:
        user = Buyer.objects.get(username=username)
    order = Order.objects.get(id=id)
    goods = order.goods
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            message = '输入内容不能为空！'
        else:
            Comments.objects.create(content=content, the_goods=goods, commenter=user)
            order.order_status = 5
            order.save()
            return redirect('goods_comment', order.goods.id)
    return render(request, 'make_comment.html', locals())


def goods_comment(request, id):
    username = request.session.get('user_name')
    goods = Goods.objects.get(id=id)
    comments = Comments.objects.filter(the_goods=goods)
    paginator = Paginator(comments, 2)
    if request.method == "GET":
        page = request.GET.get('page')
        try:
            comments = paginator.page(page)
        except (PageNotAnInteger, InvalidPage, EmptyPage):
            # 有错误, 返回第一页。
            comments = paginator.page(1)
    return render(request, 'goods_comment.html', locals())


def delete_comment(request, id):
    the_comment = Comments.objects.get(id=id)
    the_comment.content = ''
    the_comment.commenter = ''
    the_comment.save()
    return redirect('goods_comment',the_comment.the_goods_id)


def reply(request, id):
    username = request.session.get('user_name')
    the_comment = Comments.objects.get(id=id)
    if request.method == 'POST':
        shop_reply = request.POST.get('reply')
        if not shop_reply:
            message = '输入内容不能为空！'
        else:
            the_comment.reply = shop_reply
            the_comment.save()
            return redirect('goods_comment', the_comment.the_goods.id)
    return render(request, 'reply.html', locals())


def delete_reply(request, id):
    the_comment = Comments.objects.get(id=id)
    the_comment.reply = ''
    the_comment.save()
    return redirect('goods_comment', the_comment.the_goods.id)


def search(request):
    sc = request.GET.get('search',None)
    search_goods = None
    if sc:
        search_goods = Goods.objects.filter(Q(title__icontains=sc))
    return render(request, 'search_result.html', locals())
