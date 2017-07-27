from django.db import models

# Create your models here.

# The data : documents and sentences

class Document(models.Model):
    ISSUE_TYPES = (("daily", "daily"), ("summary", "summary"))
    name = models.CharField(max_length=255)
    date = models.DateField()
    copyear = models.IntegerField(default=-1)
    author = models.CharField(max_length=255)
    issue = models.IntegerField(default=-1)
    itype = models.CharField(max_length=10, choices=ISSUE_TYPES,
                             default="daily")
    # should actually create a class Cop for COP number and city etc.
    cop = models.CharField(max_length=100, default="99")
    city = models.CharField(max_length=100, default="")
    def __unicode__(self):
        return self.name


class Sentence(models.Model):
    name = models.CharField(max_length=255, default="")
    document = models.ForeignKey(Document)
    text = models.TextField()
    def __unicode__(self):
        return (str(self.id) + "-" + str(self.name) + "-" + self.text)

# The analysis output : actor(s), predicate, point
# Each mention is related to his 'lemma'
class Actor(models.Model):
    name = models.CharField(max_length=255)
    atype = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
    
class ActorMention(models.Model):
    actor = models.ForeignKey(Actor)
    text = models.CharField(max_length=255)
    def __unicode__(self):
        return self.text
    
class Predicate(models.Model):
    name = models.CharField(max_length=255)
    ptype = models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
    
class PredicateMention(models.Model):
    predicate = models.ForeignKey(Predicate)
    text = models.CharField(max_length=255)
    def __unicode__(self):
        return self.text

class Point(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name

class PointMention(models.Model):
    point = models.ForeignKey(Point)
    text = models.CharField(max_length=255)
    start = models.IntegerField(default=-1)
    end = models.IntegerField(default=-1)
    def __unicode__(self):
        return self.text

# A sentence can be analyzed as several propositions
class Proposition(models.Model):
    sentence = models.ForeignKey(Sentence)
    actorMention = models.ForeignKey(ActorMention)
    predicateMention = models.ForeignKey(PredicateMention)
    pointMention = models.ForeignKey(PointMention)
    conf = models.FloatField(default=-1.0)
    def __unicode__(self):
        return (str(self.id) + ": " + self.actorMention.text + "-" + self.predicateMention.text + "-" + self.pointMention.text)

                        
class KeyPhrase(models.Model):
    sentence = models.ForeignKey(Sentence)
    pointmentions = models.ManyToManyField(PointMention)
    text = models.TextField()
    start = models.IntegerField()
    end = models.IntegerField()
    def __unicode__(self):
        return self.text


class Entity(models.Model):
    name = models.TextField()
    active = models.BooleanField(default=True)
    etype = models.CharField(max_length=50, default="dbp")
    # for reegle thesaurus, store the term id (numeric) here
    eurl = models.CharField(max_length=50, default="")
    def __unicode__(self):
        return self.text


class EntityMention(models.Model):
    active = models.BooleanField(default=True)
    sentence = models.ForeignKey(Sentence)
    entity = models.ForeignKey(Entity)
    pointmentions = models.ManyToManyField(PointMention)
    text = models.TextField()
    start = models.IntegerField()
    end = models.IntegerField()
    confidence = models.FloatField()
    linker = models.CharField(max_length=50, default="def")
    def __unicode__(self):
        return u"{} => {}".format(self.text, self.entity.name)


class AgrDis(models.Model):
    """AgreeDisagree relations"""
    # https://stackoverflow.com/questions/22538563
    # (reverse accessor for foreign keys clashing)
    actorMention1 = models.ForeignKey(ActorMention, related_name='%(class)s_a1')
    actorMention2 = models.ForeignKey(ActorMention, related_name='%(class)s_a2')
    pointMention = models.ForeignKey(PointMention)
    RELTYPES = (("agree", "agree"), ("disagree", "disagree"))
    reltype = models.CharField(max_length=100, choices=RELTYPES)
    def __unicode__(self):
        return u"{}:{}-{}-{}".format(str(self.id), self.actorMention1.name,
                                     self.actorMention2.name, self.reltype)
