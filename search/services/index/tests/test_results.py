"""Tests for :mod:`search.services.index`."""

from unittest import TestCase, mock
from search.services.index import results


class TestResultsHighlightAbstract(TestCase):
    """Given a highlighted abstract, generate a safe preview."""

    def setUp(self):
        """Set a sample abstract for use in test cases."""
        self.value = (
            "A search for the standard model (SM) Higgs boson ($\\mathrm{H}"
            "$) decaying to $\\mathrm{b}\\overline{\\mathrm{b}}$ when produced"
            " in association with an electroweak vector boson is reported for"
            " the following processes: <em>$\\mathrm{b}\\overline{\\mathrm{b}}"
            "(\\nu\\nu)\\mathrm{H}$</em>, $\\mathrm{W}(\\mu\\nu)\\mathrm{H}$,"
            " $\\mathrm{W}(\\mathrm{e} \\nu)\\mathrm{H}$,"
            " $\\mathrm{Z}(\\mu\\mu)\\mathrm{H}$, and"
            " $\\mathrm{Z}(\\mathrm{e}\\mathrm{e})\\mathrm{H}$."
        )
        self.start_tag = '<em>'
        self.end_tag = '</em>'

    def test_preview(self):
        """Generate a preview that is smaller than/equal to fragment size."""
        preview = results._preview(self.value, fragment_size=350,
                                   start_tag=self.start_tag,
                                   end_tag=self.end_tag)
        self.assertEqual(len(preview), 326)


class TestResultsEndSafely(TestCase):
    """Given a highlighted abstract, find a safe end index for the preview."""

    def setUp(self):
        """Set a sample abstract for use in test cases."""
        self.value = (
            "A search for the standard model (SM) Higgs boson ($\\mathrm{H}"
            "$) decaying to $\\mathrm{b}\\overline{\\mathrm{b}}$ when produced"
            " in association with an electroweak vector boson is reported for"
            " the following processes: <em>$\\mathrm{b}\\overline{\\mathrm{b}}"
            "(\\nu\\nu)\\mathrm{H}$</em>, $\\mathrm{W}(\\mu\\nu)\\mathrm{H}$,"
            " $\\mathrm{W}(\\mathrm{e} \\nu)\\mathrm{H}$,"
            " $\\mathrm{Z}(\\mu\\mu)\\mathrm{H}$, and"
            " $\\mathrm{Z}(\\mathrm{e}\\mathrm{e})\\mathrm{H}$."
        )
        self.start_tag = '<em>'
        self.end_tag = '</em>'

    def test_end_safely_from_start(self):
        """No TeXisms/HTML are found within the desired fragment size."""
        end = results._end_safely(self.value, 45, start_tag=self.start_tag,
                                  end_tag=self.end_tag)
        self.assertEqual(end, 45, "Should end at the desired fragment length.")

    def test_end_safely_before_texism(self):
        """End before TeXism when desired fragment size would truncate."""
        end = results._end_safely(self.value, 55, start_tag=self.start_tag,
                                  end_tag=self.end_tag)
        # print(self.value[:end])
        self.assertEqual(end, 50, "Should end before the start of the TeXism.")

    def test_end_safely_before_html(self):
        """End before HTML when desired fragment size would truncate."""
        end = results._end_safely(self.value, 215, start_tag=self.start_tag,
                                  end_tag=self.end_tag)
        # print(self.value[:end])
        self.assertEqual(end, 213, "Should end before the start of the tag.")

    def test_end_safely_after_html_with_tolerance(self):
        """End before HTML when desired fragment size would truncate."""
        end = results._end_safely(self.value, 275,
                                  start_tag=self.start_tag,
                                  end_tag=self.end_tag)
        self.assertEqual(end, 275, "Should end after the closing tag.")
