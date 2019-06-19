# -*- coding: utf-8 -*-
from extend_me import Extensible

from ...plugin import Plugin

from . import graphml_yed


SKIP_MODEL_FIELDS = [
    'id',
    'create_date',
    'create_uid',
    'write_date',
    'write_uid',
    '__last_update',
    'display_name',

    'message_is_follower',
    'message_follower_ids',
    'message_partner_ids',
    'message_channel_ids',
    'message_ids',
    'message_last_post',
    'message_unread',
    'message_unread_counter',
    'message_needaction',
    'message_needaction_counter',
    'website_message_ids',

    'activity_ids',
    'activity_state',
    'activity_user_id',
    'activity_type_id',
    'activity_date_deadline',
    'activity_summary',

    'website_meta_title',
    'website_meta_description',
    'website_meta_keywords',
    'website_published',
    'website_url',
    'website_description',

    'rating_ids',
    'rating_last_value',
    'rating_last_feedback',
    'rating_last_image',
    'rating_count',
]


class Model(graphml_yed.NodeBigEntity):

    """ Odoo model abstraction layer
    """

    def __init__(self, obj, *args, **kwargs):
        self._object = obj
        if obj.model_name != obj.name:
            node_label = "%s\n(%s)" % (
                self._object.model_name, self._object.name)
        else:
            node_label = self._object.model_name
        node_attributes = '\n'.join((
            f for f in self.fields if f not in SKIP_MODEL_FIELDS))
        super(Model, self).__init__(
            node_label, node_attributes, *args, **kwargs)

    def __eq__(self, other):
        return self._object == other._object

    def __hash__(self):
        return hash(self._object.name)

    @property
    def name(self):
        return self._object.name

    @property
    def object(self):
        return self._object

    @property
    def client(self):
        return self._object.client

    @property
    def fields(self):
        return self._object.columns_info


class ModelRelation(object):

    """ Model relation abstraction layer.
        Represents relation betwen models
    """

    def __init__(self, source, target, field_name):
        self.source = source
        self.target = target
        self.field_name = field_name

        self._ir_field = None

        assert (self.source.client ==
                self.target.client), ("Source and targed binded to "
                                      "different clients")

    @property
    def client(self):
        return self.source.client

    @property
    def field_info(self):
        return self.source.fields[self.field_name]

    @property
    def ir_field(self):
        if self._ir_field is None:
            r = self.client['ir.model.fields'].search_records(
                [('model', '=', self.source.object.name),
                 ('name', '=', self.field_name)])
            if r and len(r) == 1:
                self._ir_field = r[0]
            else:
                self._ir_field = False
        return self._ir_field

    @property
    def rel_field_name(self):
        return self.field_info.get('relation_field', None)

    @property
    def rel_field_info(self):
        if self.rel_field_name:
            return self.target.fields[self.rel_field_name]
        return None

    @property
    def rel_type(self):
        return self.field_info['type']

    def __eq__(self, other):
        if self.client != other.client:
            return False

        if self.source == other.source and self.field_name == other.field_name:
            return True

        if self.rel_type != other.rel_type:
            return False

        if self.target != other.source or self.source != other.target:
            return False

        return False

    def __hash__(self):
        return hash(
            "%s-%s-%s-%s" % (self.rel_type, self.field_name,
                             self.source, self.target))

    def to_graphml(self):
        label = self.field_name
        source_arrow = 'none'
        target_arrow = 'none'
        if self.rel_type == 'many2one':
            source_arrow = 'crows_foot_many'
            target_arrow = 'crows_foot_one'

        return [graphml_yed.Edge(self.source,
                                 self.target,
                                 label=label,
                                 source_arrow=source_arrow,
                                 target_arrow=target_arrow)]


class ModelM2MRelation(ModelRelation):

    """ Many-to-many relation abstraction.

        Represents many-to-many relation betwen two models
    """

    def __init__(self, source, target, field_name):
        super(ModelM2MRelation, self).__init__(source, target, field_name)

    @property
    def m2m_table(self):
        if (self.ir_field and
                'relation_table' in self.ir_field._object.columns_info):
            return self.ir_field.relation_table
        else:  # versions of odoo before 9.0
            return self.field_info.get('m2m_join_table', None)

    @property
    def m2m_columns(self):
        if self.ir_field and 'column1' in self.ir_field._object.columns_info:
            return self.ir_field.column1, self.ir_field.column2
        else:  # versions of odoo before
            return self.field_info.get('m2m_join_columns', None)

    def __eq__(self, other):
        if (isinstance(other, ModelM2MRelation) and
                super(ModelM2MRelation, self).__eq__(other)):
            return (self.m2m_table and other.m2m_table and
                    self.m2m_columns and other.m2m_columns and
                    self.m2m_table == other.m2m_table and
                    self.m2m_columns == reversed(other.m2m_columns))
        return False

    def __hash__(self):
        return hash(
            "%s-%s-%s-%s" % (self.rel_type, self.field_name,
                             self.source, self.target))

    def to_graphml(self):
        if self.m2m_table:
            m2m_rel_node = graphml_yed.NodeRelationship(self.m2m_table)
            m2m_rel_edge_1 = graphml_yed.Edge(
                self.source, m2m_rel_node,
                label=(
                    (self.m2m_columns[0] + '*')
                    if self.m2m_columns[0] else '?'),
                source_arrow='crows_foot_one',
                target_arrow='crows_foot_many')
            m2m_rel_edge_2 = graphml_yed.Edge(
                self.target, m2m_rel_node,
                label=(
                    (self.m2m_columns[1] + '*')
                    if self.m2m_columns[1] else '?'),
                source_arrow='crows_foot_one',
                target_arrow='crows_foot_many')

            return [m2m_rel_node, m2m_rel_edge_1, m2m_rel_edge_2]
        return super(ModelM2MRelation, self).to_graphml()


class ModelGraph(Extensible):

    """ Contains single model graph
    """

    def __init__(self, client, models, depth=1,
                 ignore_models=None, ignore_fields=None):
        """
            :param list(str) models: list of strings with names of Objects
                                     to build graph for
            :param int depth: Recursion depth for model search
        """
        self._client = client
        self._depth = depth
        self._model_cache = {}
        self._models = [
            self._get_graph_model(m, main=True) for m in models]
        self._ignore_models = [] if ignore_models is None else ignore_models
        self._ignore_fields = [] if ignore_fields is None else ignore_fields

        self._relations = set()
        self._processed_models = set()

        self._graph = None

    @property
    def depth(self):
        """ Graph depth
        """
        return self._depth

    @property
    def graph(self):
        """ Return pydot.Dot instance of graph
        """
        if self._graph is None:
            return self.generate_graph()
        return self._graph

    def clean(self):
        """ Clean graph
        """
        self._graph = None
        self._relations = set()
        self._processed_models = set()

    def _get_graph_model(self, name, main=False):
        model = self._model_cache.get(name, None)
        if model is None:
            if main:
                model = Model(self._client.get_obj(name), color="#FFFF99")
            else:
                model = Model(self._client.get_obj(name))
            self._model_cache[name] = model
        return model

    def _find_relations(self, model=None, level=0):
        """ Finds relation between selected models
        """
        if model is None:
            for model in self._models:
                self._find_relations(model)
        else:
            self._processed_models.add(model)
            for field_name, field in model.fields.items():
                if field['type'] not in ('many2one', 'many2many', 'one2many'):
                    continue

                if field_name in SKIP_MODEL_FIELDS:
                    continue

                if field_name in self._ignore_fields:
                    continue

                source = model
                target = self._get_graph_model(field['relation'])

                if target in self._ignore_models:
                    continue

                if field['type'] == 'many2many':
                    relation = ModelM2MRelation(source, target, field_name)
                else:
                    relation = ModelRelation(source, target, field_name)

                self._relations.add(relation)

                if (level < self._depth and
                        target not in self._processed_models):
                    self._find_relations(target, level + 1)
                self._processed_models.add(target)

        return self._processed_models, self._relations

    def generate_graph(self):
        """ Return pydot.Dot instance of graph
        """
        models, relations = self._find_relations()

        graph_nodes = [] + list(models)
        graph_edges = []

        for rel in list(relations):
            for g_obj in rel.to_graphml():

                if isinstance(g_obj, graphml_yed.Node):
                    graph_nodes.append(g_obj)
                elif isinstance(g_obj, graphml_yed.Edge):
                    graph_edges.append(g_obj)
                else:
                    raise ValueError(
                        "Wrong type of g_obj: %r\n(rel: %r)" %
                        (g_obj, rel))

        self._graph = graphml_yed.Graph(graph_nodes, graph_edges)

        return self._graph


class Graph(Plugin):

    """ Plugin that allow to build graphs.

        At this point it is in experimental stage
    """

    class Meta:
        name = "yed_graph"

    def __init__(self, *args, **kwargs):
        super(Graph, self).__init__(*args, **kwargs)

    def model_graph(self, models, depth=1):
        """ Build model graph
        """
        return ModelGraph(self.client, models, depth=depth)
