PASRL-UI
========

* Django app to navigate a corpus annotated by PASRL

* Requires django v1.8.4

* App presented in Ruiz, Clément and Poibeau 2016 ([LREC](http://www.lrec-conf.org/proceedings/lrec2016/pdf/636_Paper.pdf) and [DH](http://dh2016.adho.org/abstracts/81) conferences), also part of my thesis [(Ruiz Fabo, 2017)](https://sites.google.com/site/thesisrf/thesis_prf_final.pdf).
* A _help_ site for the app is https://sites.google.com/site/climatenlp/home

Setup
-----

* Create a mysql DB according to the infos on pasrl\_ui/settings.py
* Create a log for the app with write access (/var/log/django/pasrl\_ui.log, as in pasrl\_ui/settings.py, or modify the path to the log in the settings file and create it at that path)
* Run

        $ python manage.py migrate
        $ python manage.py createsuperuser
        $ python manage.py runserver #server de dev

Reloading data
--------------

Using a Django [fixture](https://docs.djangoproject.com/en/1.11/ref/django-admin/#django-admin-loaddata), created from the delimited outputs of PASRL (propositions extracted from the corpus).

    $ python manage.py flush
    $ python manage.py migrate
    # from ./pasrl_ui/ext_scripts, run
    ./create_fixture.sh INPUT_FILE
    # this will create ../ext_data/json/INPUT_FILE_final.json, which you do loaddata on
    $ python manage.py loaddata INPUT_FILE_final.json
    $ python manage.py createsuperuser

Running
-------

Normal way for a Django app:

    python manage.py runserver PORT_NUMBER

Apps
----

* ui :  http://localhost:PORT_NUMBER/ui
* admin : http://localhost:PORT_NUMBER/admin


