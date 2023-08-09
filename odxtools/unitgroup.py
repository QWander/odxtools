# SPDX-License-Identifier: MIT
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .exceptions import odxraise, odxrequire
from .nameditemlist import NamedItemList
from .odxlink import OdxDocFragment, OdxLinkDatabase, OdxLinkId, OdxLinkRef
from .unit import Unit
from .utils import create_description_from_et, short_name_as_id

if TYPE_CHECKING:
    from .diaglayer import DiagLayer


class UnitGroupCategory(Enum):
    COUNTRY = "COUNTRY"
    EQUIV_UNITS = "EQUIV-UNITS"


@dataclass
class UnitGroup:
    """A group of units.

    There are two categories of groups: COUNTRY and EQUIV-UNITS.
    """

    short_name: str
    category: UnitGroupCategory
    unit_refs: List[OdxLinkRef]
    oid: Optional[str]
    long_name: Optional[str]
    description: Optional[str]

    def __post_init__(self):
        self._units = NamedItemList[Unit](short_name_as_id)

    @staticmethod
    def from_et(et_element, doc_frags: List[OdxDocFragment]) -> "UnitGroup":
        oid = et_element.get("OID")
        short_name = et_element.findtext("SHORT-NAME")
        long_name = et_element.findtext("LONG-NAME")
        description = create_description_from_et(et_element.find("DESC"))
        category_str = et_element.findtext("CATEGORY")
        if category_str not in UnitGroupCategory.__members__:
            odxraise(f"Encountered unknown unit group category '{category_str}'")
        category = UnitGroupCategory(category_str)

        unit_refs: List[OdxLinkRef] = [
            odxrequire(OdxLinkRef.from_et(el, doc_frags))
            for el in et_element.iterfind("UNIT-REFS/UNIT-REF")
        ]

        return UnitGroup(
            short_name=short_name,
            category=category,
            unit_refs=unit_refs,
            oid=oid,
            long_name=long_name,
            description=description,
        )

    def _build_odxlinks(self) -> Dict[OdxLinkId, Any]:
        return {}

    def _resolve_odxlinks(self, odxlinks: OdxLinkDatabase) -> None:
        self._units = NamedItemList[Unit](short_name_as_id,
                                          [odxlinks.resolve(ref) for ref in self.unit_refs])

    def _resolve_snrefs(self, diag_layer: "DiagLayer") -> None:
        pass

    @property
    def units(self) -> NamedItemList[Unit]:
        return self._units