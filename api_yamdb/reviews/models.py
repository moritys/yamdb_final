from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_usernames


class CategoryGenreModel(models.Model):
    """Общая модель для категорий и жанров."""
    name = models.CharField(max_length=256, verbose_name='Название')

    class Meta:
        abstract = True
        verbose_name = 'Название'
        verbose_name_plural = 'Название во множественном числе'
        ordering = ['id']

    def __str__(self):
        return self.name


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        validators=[validate_usernames],
        null=True,
        unique=True
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        verbose_name='О себе',
        null=True,
        blank=True
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff or self.is_superuser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact="me"),
                name="username_is_not_me"
            )
        ]


class Category(CategoryGenreModel):
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='URL категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(CategoryGenreModel):
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='URL жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Slug категории'
    )
    genre = models.ManyToManyField(Genre, related_name='titles')
    name = models.CharField(
        max_length=256, verbose_name='Название', default='Title name'
    )
    year = models.IntegerField(verbose_name='Год выпуска', default=2000)
    description = models.CharField(
        max_length=256, verbose_name='Описание', null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['id']

    def __str__(self):
        return self.name


class ReviewCommentModel(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата отзыва', auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        abstract = True
        ordering = ('pub_date',)


class Review(ReviewCommentModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_author',
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews_title',
    )
    score = models.IntegerField()

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            ),
        ]


class Comment(ReviewCommentModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments_author',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments_review',
    )
