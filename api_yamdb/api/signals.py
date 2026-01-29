from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

from reviews.models import Title, Review


@receiver([post_save, post_delete], sender=Review)
def update_title_rating(sender, instance, **kwargs):
    """Обновляет рейтинг произведения.
    Вызывается после сохранения или удаления записи в модели Review
    """
    title_id = instance.title_id
    reviews = Review.objects.filter(title_id=title_id)
    if reviews:
        avg_rating = reviews.aggregate(Avg('score'))['score__avg']
        rating = round(avg_rating)
    else:
        rating = None
    Title.objects.filter(id=title_id).update(rating=rating)
