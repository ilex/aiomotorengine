from preggy import expect
import unittest
from nose.tools import eq_, ok_, raises
from nose.tools import assert_not_equal as ne_

from aiomotorengine import Document, PasswordField
from aiomotorengine.fields.password_field import md5, PasswordType
from tests import AsyncTestCase, async_test


class User(Document):
    __collection__ = 'users'
    password = PasswordField(required=True)


class TestPasswordType(unittest.TestCase):

    def test_md5(self):
        eq_(md5('xxx'), 'f561aaf6ef0bf14d4208bb46a4ccb3ad')

    def test_password_type(self):
        x = PasswordType('xxx', crypt_func=md5, is_crypted=False)
        eq_(x.value, 'f561aaf6ef0bf14d4208bb46a4ccb3ad')
        eq_(x, 'xxx')
        ne_(x, 'yyy')
        ne_(x, 5)

        y = PasswordType(
            'f561aaf6ef0bf14d4208bb46a4ccb3ad', crypt_func=md5, is_crypted=True
        )
        eq_(y, 'xxx')
        eq_(y, x)

        z = PasswordType('xxx')
        eq_(z, x)


class TestPasswordField(AsyncTestCase):

    def setUp(self):
        super().setUp()
        self.drop_coll(User.__collection__)

    def test_password_field(self):
        u = User(password='xxx')

        eq_(u.password, 'xxx')

        son = u.to_son()
        ok_('password' in son)
        eq_(son['password'], 'f561aaf6ef0bf14d4208bb46a4ccb3ad')

    def test_password_field_to_son(self):
        field = PasswordField()

        value = field.to_son(PasswordType('xxx'))
        eq_(value, 'f561aaf6ef0bf14d4208bb46a4ccb3ad')

        value = field.to_son('xxx')
        eq_(value, 'f561aaf6ef0bf14d4208bb46a4ccb3ad')

    @raises(TypeError)
    def test_password_field_to_son_wrong_value(self):
        field = PasswordField()
        field.to_son(5)

    @async_test
    async def test_password_field_save_and_load(self):
        user = User(password='xxx')
        result = await user.save()

        ok_(result._id is not None)
        ok_(user._id is not None)

        id = result._id
        # get by id
        user1 = await User.objects.get(id=id)
        ok_(user1 is not None)
        eq_(user1.password, user.password)

        # get by passowrd
        user2 = await User.objects.get(password='xxx')

        ok_(user2 is not None)
        eq_(user2._id, id)
        eq_(user2.password, 'xxx')
        eq_(user2.password, user.password)

        # test string representation
        eq_(str(user2.password), 'f561aaf6ef0bf14d4208bb46a4ccb3ad')

        # change password with new and save
        user2.password = 'yyy'
        eq_(user2.password, 'yyy')
        await user2.save()

        # try load user with old password
        user3 = await User.objects.get(password='xxx')
        ok_(user3 is None)

        # try load user with new password
        user4 = await User.objects.get(password='yyy')
        ok_(user4 is not None)
        eq_(user4._id, id)

    def test_create_password_field(self):
        field = PasswordField(db_field="test")
        expect(field.db_field).to_equal("test")

    def test_validate_enforces_password_type(self):
        field = PasswordField()

        expect(field.validate(1)).to_be_false()

    def test_is_empty(self):
        field = PasswordField()
        expect(field.is_empty(None)).to_be_true()
        expect(field.is_empty("")).to_be_true()
        expect(field.is_empty("123")).to_be_false()

    def test_validate_only_if_not_none(self):
        field = PasswordField(required=False)

        expect(field.validate(None)).to_be_true()
