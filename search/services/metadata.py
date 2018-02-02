"""Provides acces to paper metadata from the core arXiv repository."""

import os
from urllib.parse import urljoin
import json
from functools import wraps

import requests

from search.context import get_application_config, get_application_global
from search import status, logging
from search.domain import DocMeta


logger = logging.getLogger(__name__)


class DocMetaSession(object):
    """An HTTP session with the docmeta endpoint."""

    def __init__(self, endpoint: str) -> None:
        """Initialize an HTTP session."""
        self._session = requests.Session()
        self._adapter = requests.adapters.HTTPAdapter(max_retries=2)
        self._session.mount('https://', self._adapter)

        if not endpoint[-1] == '/':
            endpoint += '/'
        self.endpoint = endpoint

    def retrieve(self, document_id: str) -> DocMeta:
        """
        Retrieve metadata for an arXiv paper.

        Parameters
        ----------
        document_id : str

        Returns
        -------
        dict

        Raises
        ------
        IOError
        ValueError
        """
        if not document_id:    # This could use further elaboration.
            raise ValueError('Invalid value for document_id')

        try:
            response = requests.get(urljoin(self.endpoint, document_id))
        except requests.exceptions.SSLError as e:
            raise IOError('SSL failed: %s' % e)

        if response.status_code not in \
                [status.HTTP_200_OK, status.HTTP_206_PARTIAL_CONTENT]:
            raise IOError('%s: could not retrieve metadata: %i' %
                          (document_id, response.status_code))
        try:
            data = DocMeta(response.json())
        except json.decoder.JSONDecodeError as e:
            raise IOError('%s: could not decode response: %s' %
                          (document_id, e)) from e
        return data

    def ok(self) -> bool:
        """Health check."""
        logger.debug('check health of metadata service at %s', self.endpoint)
        try:
            r = requests.head(self.endpoint)
            logger.debug('response from metadata endpoint:  %i: %s',
                         r.status_code, r.content)
            return r.ok
        except IOError as e:
            logger.debug('connection to metadata endpoint failed with %s', e)
        return False


def init_app(app: object = None) -> None:
    """Set default configuration parameters for an application instance."""
    config = get_application_config(app)
    config.setdefault('METADATA_ENDPOINT', 'https://arxiv.org/docmeta/')


def get_session(app: object = None) -> DocMetaSession:
    """Get a new session with the docmeta endpoint."""
    config = get_application_config(app)
    endpoint = config.get('METADATA_ENDPOINT', 'https://arxiv.org/docmeta/')
    return DocMetaSession(endpoint)


def current_session():
    """Get/create :class:`.DocMetaSession` for this context."""
    g = get_application_global()
    if not g:
        return get_session()
    if 'docmeta' not in g:
        g.docmeta = get_session()
    return g.docmeta


@wraps(DocMetaSession.retrieve)
def retrieve(document_id: str) -> DocMeta:
    return current_session().retrieve(document_id)


@wraps(DocMetaSession.ok)
def ok() -> bool:
    return current_session().ok()