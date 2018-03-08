"""Core data structures internal to the search service."""

from typing import Any, Iterable, NamedTuple, Optional, Type, List, Dict
from datetime import date, datetime
import json
from operator import attrgetter

import jsonschema

from dataclasses import dataclass, fields, field


@dataclass(init=False)
class SchemaBase:
    """Base for domain classes with standardized JSON and str reprs."""

    def json(self) -> str:
        """Return the string representation of the instance in JSON."""
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)

    # def __str__(self) -> str:
    #     """Build a string representation, for use in rendering."""
    #     return '; '.join([
    #         '%s: %s' % (attr, attrgetter(attr)(self))
    #         for attr in fields(self) if attrgetter(attr)(self)
    #     ])  # pylint: disable=E1101


@dataclass
class DocMeta(SchemaBase):
    """Metadata for an arXiv paper, retrieved from the core repository."""

    paper_id: str = field(default_factory=str)
    abstract: str = field(default_factory=str)
    abstract_utf8: str = field(default_factory=str)
    authors_parsed: str = field(default_factory=str)
    authors_utf8: str = field(default_factory=str)
    author_owners: str = field(default_factory=str)
    authors: str = field(default_factory=str)
    submitted_date: str = field(default_factory=str)
    submitted_date_all: List[str] = field(default_factory=list)
    modified_date: str = field(default_factory=str)
    updated_date: str = field(default_factory=str)
    announced_date_first: str = field(default_factory=str)
    is_current: bool = True
    is_withdrawn: bool = False
    license: Dict[str, str] = field(default_factory=dict)
    primary_classification: Dict[str, str] = field(default_factory=dict)
    secondary_classification: List[Dict[str, str]] = field(default_factory=list)
    title: str = field(default_factory=str)
    title_utf8: str = field(default_factory=str)
    source: Dict[str, Any] = field(default_factory=dict)
    version: int = -1
    submitter: Dict[str, str] = field(default_factory=dict)
    report_num: str = field(default_factory=str)
    proxy: bool = False
    msc_class: str = field(default_factory=str)
    acm_class: str = field(default_factory=str)
    metadata_id: int = -1
    document_id: int = -1
    journal_ref: str = field(default_factory=str)
    journal_ref_utf8: str = field(default_factory=str)
    doi: str = field(default_factory=str)
    comments: str = field(default_factory=str)
    comments_utf8: str = field(default_factory=str)
    abs_categories: str = field(default_factory=str)
    formats: List[str] = field(default_factory=list)


@dataclass
class Fulltext(SchemaBase):
    """Fulltext content for an arXiv paper, including extraction metadata."""

    content: str
    version: str
    created: datetime


class DateRange(NamedTuple):
    """Represents an open or closed date range."""

    start_date: datetime = datetime(1990, 1, 1)
    """The day/time on which the range begins."""

    end_date: datetime = datetime.now()
    """The day/time at (just before) which the range ends."""

    # on_version = Property('field', str)
    # """The date field on which to filter

    def __str__(self) -> str:
        """Build a string representation, for use in rendering."""
        _str = ''
        if self.start_date:
            start_date = self.start_date.strftime('%Y-%m-%d')
            _str += f'from {start_date} '
        if self.end_date:
            end_date = self.end_date.strftime('%Y-%m-%d')
            _str += f'to {end_date}'
        return _str


class Classification(NamedTuple):
    """Represents an arxiv classification."""

    group: str
    archive: Optional[str] = None
    category: Optional[str] = None

    def __str__(self) -> str:
        """Build a string representation, for use in rendering."""
        rep = f'{self.group}'
        if self.archive:
            rep += f':{self.archive}'
            if self.category:
                rep += f':{self.category}'
        return rep


class ClassificationList(list):
    """Represents a list of arxiv classifications."""

    def __str__(self) -> str:
        """Build a string representation, for use in rendering."""
        return ', '.join([str(item) for item in self])


@dataclass
class Query(SchemaBase):
    """Represents a search query originating from the UI or API."""
    order: Optional[str] = None
    page_size: int = 25
    page_start: int = 0

    @property
    def page_end(self) -> int:
        """Get the index/offset of the end of the page."""
        return self.page_start + self.page_size

    @property
    def page(self) -> int:
        """Get the approximate page number."""
        return 1 + int(round(self.page_start/self.page_size))


@dataclass
class SimpleQuery(Query):
    """A query on a single field."""

    field: str = ''
    value: str = ''


@dataclass
class Document(SchemaBase):
    """A single search document, representing an arXiv paper."""

    id: str
    abstract: str
    authors: List[Dict]
    authors_freeform: str
    owners: List[Dict]
    submitted_date: str
    submitted_date_all: List[str]
    submitted_date_first: str
    submitted_date_latest: str
    modified_date: str
    updated_date: str
    announced_date_first: str
    is_current: bool
    is_withdrawn: bool
    license: Dict[str, str]
    paper_id: str
    paper_id_v: str
    title: str
    title_utf8: str
    source: Dict[str, Any]
    version: int
    submitter: Dict
    report_num: str
    proxy: bool
    msc_class: List[str]
    acm_class: List[str]
    metadata_id: int
    journal_ref: str
    doi: str
    comments: str
    abs_categories: str
    formats: List[str]

    # __schema__ = 'schema/Document.json'
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class DocumentSet(SchemaBase):
    """A set of search results retrieved from the search index."""

    metadata: Dict[str, Any]
    results: List[Document]
    # __schema__ = 'schema/DocumentSet.json'
