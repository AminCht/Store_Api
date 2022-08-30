from djoser.serializers import UserSerializer as BaseUserSer, UserCreateSerializer as BaseUserCreateSer


class UserCreateSerializer(BaseUserCreateSer):
    class Meta(BaseUserCreateSer.Meta):
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']


class UserSerializer(BaseUserSer):
    class Meta(BaseUserSer.Meta):
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email']


