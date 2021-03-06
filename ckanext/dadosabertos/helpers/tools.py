# -*- coding: utf-8 -*-
from ckan.lib.base import c, g, h, model
import ckan.logic
from ckan.logic import get_action
from random import shuffle
from copy import deepcopy


def trim_string(s, tamanho):
    s = unicode(s)
    return s if (len(s) < tamanho) else s[:(tamanho - 5)].rsplit(u" ", 1)[0] + u"..."

def trim_letter(s, tamanho):
    s = unicode(s)
    return s if (len(s) < tamanho) else s[:(tamanho)] + u"..."


def resource_count():
    ''' Return total number of resources on current CKAN platform

        @return int
    '''
    try:
        # resource search
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}
        data_dict = {
            'query':{},
            'facet.field':g.facets,
            'offset':0,
            'limit':0,
            'order_by': None,
        }
        query = ckan.logic.get_action('resource_search')(context,data_dict)
        return query['count']
    except Exception as e:
        return 0


def most_recent_datasets():
        """ Return most recent datasets
        """
        import ckan.lib.dictization as d
        from ckan.logic import get_action
        from sqlalchemy import desc

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author}

        query = model.Session.query(model.Package, model.Activity)
        query = query.filter(model.Activity.object_id==model.Package.id)
        query = query.filter(model.Activity.activity_type == 'new package')
        query = query.filter(model.Package.state == 'active')
        query = query.order_by(desc(model.Activity.timestamp))
        query = query.limit(5)
        most_recent_from_bd = query.all()
        most_recent_datasets = [
            (
                g.site_url + '/dataset/' + dataset.name,
                dataset.title,
                dataset.author,
                activity.timestamp.isoformat(),
            )   for dataset, activity in most_recent_from_bd]

        most_recent_datasets = []
        for dataset, activity in most_recent_from_bd:
            dataset.link = 'dataset/' + dataset.name
            dataset.time = activity.timestamp.strftime("%d/%m/%Y")
            most_recent_datasets.append(dataset)


        return most_recent_datasets



def get_featured_datasets(group_name='dados-em-destaque', number_of_datasets=3):
    """ Return a list of mainly datasets from a group

        @params group_name:string (group name)
                number_of_datasets:int (number of datasets to be returned)
        @return list<packages> (list of datasets)
    """
    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author}

    query = model.Session.query(model.Package, model.Activity)
    query = query.filter(model.Group.name==unicode(group_name))
    query = query.limit(5)
    most_recent_from_bd = query.all()
    most_recent_datasets = [
        (
            g.site_url + '/dataset/' + dataset.name,
            dataset.title,
            dataset.author,
            activity.timestamp.isoformat(),
        )   for dataset, activity in most_recent_from_bd]

    most_recent_datasets = []
    for dataset, activity in most_recent_from_bd:
        dataset.link = 'dataset/' + dataset.name
        dataset.time = activity.timestamp.strftime("%d/%m/%Y")
        most_recent_datasets.append(dataset)


    return most_recent_datasets




    context = {'model': model, 'session': model.Session,
               'user': c.user or c.author}

    data_dict = {'id': unicode(group_name)}
    return get_action('group_show')(context,data_dict)
    packages = deepcopy(get_action('group_show')(context,data_dict)['packages'])
    shuffle(packages)
    packages = packages[:int(number_of_datasets)]
    featured_datasets = []
    for package in packages:
        featured_datasets.append(
            (
            g.site_url+'dataset/'+package['name'],
            package['title'],
            package['notes']
            )
        )

    return featured_datasets
