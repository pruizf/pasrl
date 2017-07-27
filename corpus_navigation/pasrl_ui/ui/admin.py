from django.contrib import admin

# Register your models here.
from .models import Document, Sentence, Proposition, Actor, ActorMention, Predicate, PredicateMention, Point, PointMention

admin.site.register(Document)
admin.site.register(Sentence)
admin.site.register(Proposition)
admin.site.register(Actor)
admin.site.register(ActorMention)
admin.site.register(Predicate)
admin.site.register(PredicateMention)
admin.site.register(Point)
admin.site.register(PointMention)
