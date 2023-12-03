from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import datetime
from .models import Product, Order
from django.http import HttpResponseRedirect

class OrderTestCase(TestCase):
    def setUp(self):
        # test user
        self.user = User.objects.create(username='testuser', password='12345')
        # test product
        self.product = Product.objects.create(name='testproduct', price=10.00, description='testdescription', image='testimage')

    def test_order(self):
        # login test user
        self.client = Client()
        self.client.login(username='testuser', password='12345')

        # add product to cart
        self.client.post(reverse('add_to_cart', args=[self.product.id]), follow=True)

        # go to shopping cart
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

        data = {
            'shipping_address': 'testaddress',
            'payment_method': 'testpayment',
        }

        response = self.client.post(reverse('place_order'), data=data, follow=True)

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.status_code, 302)

        response ,= self.client.get(response.url)
        self.assertEqual(response.status_code, 200)

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.quantity, 1)
        self.assertEqual(order.total, self.product.price)
        self.assertEqual(order.date.date(),datetime.now().date())
        self.assertEqual(order.shipping_address, 'testaddress')
        self.assertEqual(order.payment_method, 'testpayment')



# Create your tests here.
