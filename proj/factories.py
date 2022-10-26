import factory

from .models import User, Category, Product, Order, OrderItem, Delivery, DeliveryLineItem


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('email')

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    description = factory.Faker('text')
    category = factory.SubFactory(CategoryFactory)

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    date = factory.Faker('date_time')

class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('pyint', min_value=1, max_value=10)

class DeliveryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Delivery

    order = factory.SubFactory(OrderFactory)
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    country = factory.Faker('country')
    zip_code = factory.Faker('postcode')

class DeliveryLineItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeliveryLineItem

    delivery = factory.SubFactory(DeliveryFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('pyint', min_value=1, max_value=10)