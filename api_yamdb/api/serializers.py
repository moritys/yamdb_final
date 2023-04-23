import datetime as dt

from django.db.models import Avg
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_usernames


class CategoryGenreSerializer(serializers.ModelSerializer):
    """Общий класс для категорий и жанров."""

    class Meta:
        lookup_field = 'slug'


class ReviewCommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'


class CommentSerializer(ReviewCommentSerializer):

    class Meta:
        model = Comment
        exclude = ('review',)


class ReviewSerializer(ReviewCommentSerializer):

    class Meta:
        model = Review
        exclude = ('title',)
        extra_kwargs = {'score': {'min_value': 1, 'max_value': 10}, }

    def validate(self, data):
        user = self.context.get('request').user
        title_id = (self.context.get('request').parser_context.get('kwargs')
                    .get('title_id'))
        title = get_object_or_404(Title, id=title_id)
        if (
                Review.objects.filter(title=title, author=user).exists()
                and self.context.get('request').method == 'POST'
        ):
            raise ValidationError('Действие запрещено, отзыв уже создан')
        return data


"""
По каким-то причинам поле exclude не наследуется от родительского.
Пришлось оставить его в дочерних классах.
"""


class CategorySerializer(CategoryGenreSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(CategoryGenreSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializerPost(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, year):
        if year > dt.date.today().year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения из будущего!'
            )
        return year


class TitleSerializerGet(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
        )

    def get_rating(self, obj):
        score_avg = \
            Review.objects.filter(title_id=obj.id).aggregate(Avg('score'))[
                'score__avg']
        if score_avg is None:
            return None
        return int(score_avg)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()), validate_usernames
        ],
        max_length=150,
        required=True,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        max_length=254
    )

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class UserEditSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150, validators=[validate_usernames]
    )
    email = serializers.EmailField(max_length=254)

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User
        read_only_fields = ('role',)


class RegisterDataSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        validators=[validate_usernames],
        max_length=150
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if (
            User.objects.filter(username=username).exists()
            and User.objects.get(username=username).email != email
        ):
            raise serializers.ValidationError('username уже используется')
        if (
            User.objects.filter(email=email).exists()
            and User.objects.get(email=email).username != username
        ):
            raise serializers.ValidationError('email уже существует')
        return data

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError('Username "me" is not valid')
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
