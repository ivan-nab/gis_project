from gis_project.settings.local import *

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack_elasticsearch.elasticsearch5.Elasticsearch5SearchEngine',
        'URL': 'http://elastic:changeme@elastic:9200/',
        'INDEX_NAME': 'haystack-test',
    },
}