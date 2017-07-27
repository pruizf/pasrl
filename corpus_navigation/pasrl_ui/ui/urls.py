from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # agree-disagree template
    url(r'^agd$', views.index_agd, name='index_agd'),
    # single solr document on right pane
    url(r'^solrdoc', views.solrdoc, name='solrdoc'),
    # single sentence on right (from DB, NOT from Solr!)
    url(r'^dbsen', views.dbsen, name='dbsen'),
    # main view (actors/actions + right pane)
    url(r'^actors/(sen|doc|dbp|kp|rgl)/(actor|action|point|cop|year|conf|default)', views.actors, name="actors"),
    url(r'^actors/(sen|doc|dbp|kp|rgl)', views.actors, name="actors"),
    url(r'^actions/(sen|doc|dbp|kp|rgl)/(actor|actiontype|point|cop|year|conf|default)/', views.actions, name='actions'),
    url(r'^actions/(sen|doc|dbp|kp|rgl)', views.actions, name='actions'),
    # get propositions for a keyphrase or entity, or sentence
    #note: apptly can't mix positional and kwargs (https://code.djangoproject.com/ticket/9760)
    #url(r'^ekprop/([0-9.]+)/(ek|sen)', views.ekprop, name='ekprop'),
    url(r'^ekprop/([-10-9.]+)/(ek|sen)/(.+)/$', views.ekprop, name='ekprop'),
    url(r'^ekprop/([-10-9.]+)/(sen)/$', views.ekprop, name='ekprop'),
    # agree-disagree view
    url(r'^agrdis', views.agrdis, name='agrdis'),
    # get sentences for a keyphrase or entity, used in agrdis
    url(r'^eksent/([0-9.]+)/(.+)/', views.eksent, name='eksent'),
    # pagination
    url(r'^pager-reset', views.pager_reset, name='pager_reset'),
    url(r'^pager-prev', views.pager_prev, name='pager_prev'),
    url(r'^pager-next', views.pager_next, name='pager_next'),
    # fullsent is used for tests only
    url(r'^fullsent/([0-9]+)/', views.fullsent, name='fullsent'),
]
