from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """test unauthenticated recipe api access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe api access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@morrissp.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Tets retrieving recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Tets retrieving recipes for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test2@morrissp.com',
            'password123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    
    # def test_create_ingredient_successful(self):
    #    """Test Creating a new ingredient"""
    #    payload = {'name': 'Test Ingredient'}
    #    self.client.post(INGREDIENT_URL, payload)

    #    exists = Ingredient.objects.filter(
    #        user=self.user,
    #        name=payload['name']
    #    ).exists()

    #    self.assertTrue(exists)

    # def test_create_ingredient_invalid(self):
    #    """test create an invalid ingredient"""
    #    payload = {'name': ''}
    #    res = self.client.post(INGREDIENT_URL, payload)

    #   self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    