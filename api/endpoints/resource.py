# -*- coding: utf-8 -*-
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from flask import jsonify, request

from .. import app, public_bp, resource_bp
from ..mongodb import *

target_collection = 'resource'

collection = db.get_collection(target_collection)

@public_bp.route('/resources', methods=['OPTIONS'])
def get_resources_options():
    return app.make_default_options_response()


@resource_bp.route('/', methods=['GET'])
def get_resources():
    cursor = collection.find({})
    if not cursor:
        return app.response_class(
            response='The collection {0} was not found in the database'.format(target_collection),
            status=500)

    return jsonify([resource for resource in cursor])


@resource_bp.route('/<resource_id>', methods=['GET'])
def get_resource(resource_id):
    try:
        object_id = ObjectId(resource_id)
    except InvalidId:
        return app.response_class(
            response='Invalid document ID: {0}'.format(resource_id),
            status=400)
    resource = collection.find_one({'_id': object_id})

    if not resource:
        return app.response_class(
            response='The document with ID {0} was not found in the database'.format(resource_id),
            status=404)

    return jsonify(resource)


@resource_bp.route('/', methods=['POST'])
def create_resource():
    resource = request.get_json()
    if not resource:
        return app.response_class(
            response="Unable to parse payload",
            status=400
        )

    try:
        del resource['_id']
    except KeyError:
        pass

    collection.insert_one(resource)

    return jsonify(resource)


@resource_bp.route('/<resource_id>', methods=['PUT'])
def update_resource(resource_id):
    try:
        object_id = ObjectId(resource_id)
    except InvalidId:
        return app.response_class(
            response='Invalid document ID: {0}'.format(resource_id),
            status=400)

    resource = request.get_json()
    if not resource:
        return app.response_class(
            response='Unable to parse payload',
            status=400
        )

    collection.replace_one(filter={'_id': object_id}, replacement=resource)
    return jsonify(resource)


@resource_bp.route('/<resource_id>', methods=['PATCH'])
def patch_resource(resource_id):
    try:
        object_id = ObjectId(resource_id)
    except InvalidId:
        return app.response_class(
            response='Invalid document ID: {0}'.format(resource_id),
            status=400)

    body = request.get_json()
    op = {
        'add': '$push',
        'replace': '$set',
        'remove': '$unset',
        'set': '$set',
        'push': '$push',
        'pull': '$pull'
    }[body['op']]

    updates = {op: {body['path']: body['value']}}
    result = collection.update_one({'_id': object_id}, updates)
    matched = result.matched_count
    modified = result.modified_count

    if modified == 0 and matched == 0:
        return app.response_class(
            response='Unable to find field: {0}, in document with ID: {1}'.format(body['path'], resource_id),
            status=404
        )

    now = datetime.now(tz=None)
    return jsonify({'lastEdited': now})


@resource_bp.route('/<resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    try:
        object_id = ObjectId(resource_id)
    except InvalidId:
        return app.response_class(
            response='Invalid document ID: {0}'.format(resource_id),
            status=400)

    result = collection.delete_one({'_id': object_id})

    if result.deleted_count == 0:
        return app.response_class(
            response='Document with ID {0} cannot be found'.format(resource_id),
            status=404)

    return {}
