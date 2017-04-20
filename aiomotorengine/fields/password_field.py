import six
import hashlib
try:
    from secrets import compare_digest
except ImportError:
    from hmac import compare_digest

from aiomotorengine.fields.base_field import BaseField


def md5(string):
    return hashlib.md5(bytes(string, 'utf8')).hexdigest()


def sha256(string):
    return hashlib.sha256(bytes(string, 'utf8')).hexdigest()


class PasswordType:
    '''Type to represent a password for PasswordField in python.

    Usage:

    .. testcode:: modeling_fields

        password = PasswordType('xxx')
        assert password == 'xxx' # True

        # create password with encrypted value for 'xxx'
        other = PasswordType(
            'cd2eb0837c9b4c962c22d2ff8b5441b7b45805887f051d39bf133b583baf6860',
            is_crypted=True)
        assert password == other # True

    Arguments:

    * `value` - value of the password, could be crypted or not crypted,
                according to `is_crypted`.
    * `crypt_func` - crypt function witch takes string and return its crypted
                     value, by default `sha256` algorithm is used.
    * `is_crypted` - if True - value is crypted, if False - value will be
                     crypted with `crypt_func`.

    .. versionchanged:: 0.9.0.2

        * Move from `md5` to `sha256`.
        * Fix possible timing attack, issue #3.

    '''

    def __init__(self, value, crypt_func=sha256, is_crypted=False):
        if is_crypted:
            self.value = value
        else:
            self.value = crypt_func(value)
        self.crypt_func = crypt_func

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, six.string_types):
            return compare_digest(self.crypt_func(other), self.value)
        elif isinstance(other, PasswordType):
            return compare_digest(self.value, other.value)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class PasswordField(BaseField):
    '''Field responsible for storing encrypted password.

    Usage:

    .. testcode:: modeling_fields

        class User(Document):
            password = PasswordField(required=True)

        async def go():
            user = User(password='xxx')

            # note that after field is created or assigned with value
            # it contains only encrypted value
            hash_str = 'cd2eb0837c9b4c962c22d2ff8b5441b7b45805887f051d39bf133b583baf6860'
            assert str(user.password) == hash_str

            await user.save()  # note that password is saved to db in crypted form


            # now you can use not encrypted password in filters
            user = await User.objects.get(password='xxx')
            # or in comparison
            user = await User.objects.get(id=1)
            user.password == 'xxx'
            # because 'xxx' will be crypted automatically

    Available arguments (apart from those in `BaseField`):

    * `crypt_func` - crypt function witch takes string and returns its crypted
                     value, by default `sha256` from `hashlib` is used.
    '''

    def __init__(self, crypt_func=sha256, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crypt_func = crypt_func

    def from_son(self, value):
        return PasswordType(value, crypt_func=self.crypt_func, is_crypted=True)

    def to_son(self, value):

        if isinstance(value, six.string_types):
            return self.crypt_func(value)
        elif isinstance(value, PasswordType):
            return value.value
        raise TypeError('The type of the value should be the PasswordType')

    def get_value(self, value):
        if isinstance(value, six.string_types):
            return PasswordType(
                value, crypt_func=self.crypt_func, is_crypted=False
            )
        return value

    def validate(self, value):
        if value is None:
            return True

        if isinstance(value, PasswordType):
            return True

        return False

    def is_empty(self, value):
        return value is None or value == ""
