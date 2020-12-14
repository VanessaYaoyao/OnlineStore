from django import forms
from captcha.fields import CaptchaField
from estore.models import Goods

class UserForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128)
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput)
    verification = CaptchaField()

class RegisterForm(forms.Form):
    email = forms.EmailField(label='邮箱',error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式错误'})
    verification = CaptchaField(error_messages={'error':'验证码填写错误'})

class ForgetForm(forms.Form):
    email = forms.EmailField(label='邮箱',error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式错误'})
    verification = CaptchaField(error_messages={'error':'验证码填写错误'})

class AvatarForm(forms.Form):
    avatar = forms.ImageField(error_messages = {'invalid': '请上传正确格式的图片'},required=False)

class GoodsForm(forms.ModelForm):
    class Meta:
        fields = ['title', 'description', 'picture','stock']
        model = Goods

class DescriptionForm(forms.ModelForm):
    class Meta:
        fields = ['description']
        model = Goods
